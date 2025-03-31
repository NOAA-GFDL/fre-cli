'''
 Primary Usage: fre-bronx-to-canopy -x XML -e EXP -p PLATFORM -t TARGET

 The Bronx-to-Canopy XML converter overwrites 3 files:
 - rose-suite.conf
 - app/remap-pp-components/rose-app.conf
 - app/regrid-xy/rose-app.conf
'''

# std lib
import re
import os
import subprocess
import logging
fre_logger = logging.getLogger(__name__)

# third party
import metomi.rose.config
import metomi.isodatetime.parsers

#############################################

LOGGING_FORMAT = '%(asctime)s  %(levelname)s: %(message)s'
CYLC_PATH = '/home/fms/fre-canopy/system-settings/bin'
CYLC_REFINED_SCRIPTS = ["check4ptop.pl",
                        "module_init_3_1_6.pl",
                        "plevel_mask.ncl",
                        "refineDiag_atmos.csh",
                        "refine_fields.pl",
                        "surface_albedo.ncl",
                        "tasminmax.ncl",
                        "tracer_refine.ncl",
                        "refineDiag_atmos_cmip6.csh"
                       ]
CYLC_REFINED_DIR = "\\$CYLC_WORKFLOW_RUN_DIR/etc/refineDiag"
PREANALYSIS_SCRIPT = "refineDiag_data_stager_globalAve.csh"


def freq_from_legacy(legacy_freq):
    """Return ISO8601 duration given Bronx-style frequencies

    Arguments:
        1. legacy_freq[str]: The Bronx frequency
    """
    lookup = {
        'annual': 'P1Y',
        'monthly': 'P1M',
        'seasonal': 'P3M',
        'daily': 'P1D',
        '120hr': 'P120D',
        '12hr': 'PT12H',
        '8hr': 'PT8H',
        '6hr': 'PT6H',
        '4hr': 'PT4H',
        '3hr': 'PT3H',
        '2hr': 'PT2H',
        '1hr': 'PT1H',
        'hourly': 'PT1H',
        '30min': 'PT30M'
    }
    return lookup[legacy_freq]

def chunk_from_legacy(legacy_chunk):
    """Return ISO8601 duration given Bronx-style chunk

    Arguments:
        1. legacy_chunk[str]: The Bronx chunk
    """
    regex = re.compile( r'(\d+)(\w+)' )
    match = regex.match( legacy_chunk )
    if not match:
        fre_logger.error( "Could not convert Bronx chunk to ISO8601 duration: %s",
                       legacy_chunk )
        raise ValueError

    time_unit = match.group(2)
    if time_unit not in ['yr','mo']:
        fre_logger.error("Unknown time units %s", match.group(2) )
        raise ValueError

    time_quant = match.group(1)
    ret_val=f'P{time_quant}'
    if time_unit == "yr":
        ret_val+='Y'#return f'P{time_quant}Y'
    elif time_unit == 'mo':
        ret_val+='M'#return f'P{time_quant}M'
    return ret_val

def frelist_xpath(xml, platform, target, experiment,
#                  do_analysis, historydir, refinedir, ppdir,
#                  do_refinediag, pp_start, pp_stop, validate, verbose, quiet, dual,
                  xpath):
    """Returns filepaths of FRE XML elements that use X-path notation
       using Bronx's 'frelist' command via subprocess module

    Arguments:
        1. args[str]: Argparse user-input arguments
        2. xpath[str]: X-path (XML) notation required by 'frelist'
    """

    cmd = f"frelist -x {xml} -p {platform} -t {target} {experiment} --evaluate '{xpath}'"
    fre_logger.info("running cmd:\n %s",cmd)   #fre_logger.info(f"running cmd:\n {cmd}")
    fre_logger.info(">> %s",xpath)
    process = subprocess.run(cmd,
                             shell=True,
                             check=False, #if True, retrieving std err difficult...
                             capture_output=True,
                             universal_newlines=True)

    fre_logger.info("stdout: \n%s",process.stdout.strip())
    fre_logger.info("stderr: \n%s",process.stderr.strip())
    fre_logger.info("returncode: \n%s",process.returncode)


    result = process.stdout.strip()
    if process.returncode > 0:
        raise subprocess.CalledProcessError(
            returncode=process.returncode,
            cmd=cmd,
            output=process.stdout.strip(),
            stderr=process.stderr.strip() )
    return result

def duration_to_seconds(duration):
    """Returns the conversion of a chunk duration to seconds

    Arguments:
        1. duration[str]: The original chunk duration
    """
    dur = metomi.isodatetime.parsers.DurationParser().parse(duration)
    return dur.get_seconds()


def main(xml, platform, target, experiment, do_analysis, historydir, refinedir, ppdir,
         do_refinediag, pp_start, pp_stop, validate, verbose, quiet, dual):
    """The meat of the converter

       Arguments:
           1. args[argparse Namespace]: Arguments given at the command line

       Tasks:
           1. Generate key-value pairs for the rose-suite.conf.
           2. Generate content for the regrid-xy app
           3. Generate content for the remap-pp-components app
    """

    ##########################################################################
    # Set up default configurations for regrid-xy and remap-pp-components
    ##########################################################################
    rose_remap = metomi.rose.config.ConfigNode()
    rose_remap.set(keys=['command', 'default'], value='remap-pp-components')

    rose_regrid_xy = metomi.rose.config.ConfigNode()
    rose_regrid_xy.set(keys=['command', 'default'], value='regrid-xy')

    ##########################################################################
    # Create the rose-suite config and begin setting up key-value pairs
    # Note: All strings inside the rose-suite configuration MUST be quoted.
    # Note: The exception to the 'quote' rule is boolean values.
    # Note: Addition of quotes will appear as "'" in the code.
    ##########################################################################
    rose_suite = metomi.rose.config.ConfigNode()
    rose_suite.set(keys=['template variables', 'SITE'],              value='"ppan"')
    rose_suite.set(keys=['template variables', 'CLEAN_WORK'],        value='True')
    rose_suite.set(keys=['template variables', 'PTMP_DIR'],          value='"/xtmp/$USER/ptmp"')
    rose_suite.set(keys=['template variables', 'DO_MDTF'],           value='False')
    rose_suite.set(keys=['template variables', 'DO_STATICS'],        value='True')
    rose_suite.set(keys=['template variables', 'DO_TIMEAVGS'],       value='True')
    rose_suite.set(keys=['template variables', 'DO_ANALYSIS_ONLY'],  value='False')
    rose_suite.set(keys=['template variables', 'DO_ATMOS_PLEVEL_MASKING'], value='True')
    rose_suite.set(keys=['template variables', 'FRE_ANALYSIS_HOME'],
                   value='"/home/fms/local/opt/fre-analysis/test"')

    # not sure about these
    rose_suite.set(keys=['template variables', 'PP_DEFAULT_XYINTERP'], value='"360,180"')
    rose_suite.set(keys=['template variables', 'DO_ANALYSIS'],  value='True')

    rose_suite.set(keys=['template variables', 'EXPERIMENT'],
                   value=f"'{experiment}'") #value=f"'{}'".format(experiment))
    rose_suite.set(keys=['template variables', 'PLATFORM'],
                   value=f"'{platform}'")#value="'{}'".format(platform))
    rose_suite.set(keys=['template variables', 'TARGET'],
                   value=f"'{target}'")#value="'{}'".format(target))

    #regex_fre_property = re.compile(r'\$\((\w+)') #notyetimplemented
    #all_components = set() #notyetimplemented

    ##########################################################################
    # Run 'frelist' in the background to fetch the default history directory,
    # the default history_refineDiag directory, and the default PP directory,
    # all of which have been set in the XML. If the custom arguments for these
    # directory variables have not been set by the user at the command line,
    # the XML's default paths will be inserted into rose-suite.conf.
    ##########################################################################
    if historydir is None:
        fre_logger.info("Running frelist for historydir assignment, this may fail")
        fre_logger.info("If so, try the frelist call manually and use the historydir argument")

        fetch_history_cmd = f"frelist -x {xml} -p {platform} -t {target} {experiment} -d archive"
        fre_logger.info(">> %s", fetch_history_cmd)

        fetch_history_process = subprocess.run(fetch_history_cmd,
                                               shell=True,
                                               check=True,
                                               capture_output=True,
                                               universal_newlines=True)
        historydir = fetch_history_process.stdout.strip() + '/history'
        fre_logger.info(historydir)



    # Q: should respond to do_refineDiag and refinedir args of this function?
    historydir_refined = historydir + '_refineDiag'

    if ppdir is None:
        fre_logger.info("Running frelist for ppdir assignment...")
        fre_logger.info("If this fails, try the frelist call manually and use the ppdir argument")
        fetch_pp_cmd = f"frelist -x {xml} -p {platform} -t {target} {experiment} -d postProcess"
        fre_logger.info(">> %s", fetch_pp_cmd)

        fetch_pp_process = subprocess.run(fetch_pp_cmd,
                                          shell=True,
                                          check=True,
                                          capture_output=True,
                                          universal_newlines=True)
        ppdir = fetch_pp_process.stdout.strip()
        fre_logger.info(ppdir)


    # Q: shouldn't there be a CLI analysis dir arg while we're here?
    # basically, this is borderline on the same level as the ppDir and historydir fields.
    #if do_analysis:
    fre_logger.info("Running frelist for analysis_dir assignment...")
    fetch_analysis_dir_cmd = f"frelist -x {xml} -p {platform} -t {target} {experiment} -d analysis"
    fre_logger.info(">> %s", fetch_analysis_dir_cmd)

    fetch_analysis_dir_process = subprocess.run(fetch_analysis_dir_cmd,
                                                shell=True,
                                                check=True,
                                            capture_output=True,
                                                universal_newlines=True)
    analysis_dir = fetch_analysis_dir_process.stdout.strip()
    fre_logger.info(analysis_dir)
    #else:
    #    fre_logger.info('not doing analysis.')


    grid_spec = frelist_xpath(xml, platform, target, experiment,
                              #do_analysis,
                              #historydir, refinedir, ppdir, do_refinediag,
                              #pp_start, pp_stop, validate,
                              #verbose, quiet, dual,
                              'input/dataFile[@label="gridSpec"]')
    sim_time = frelist_xpath(xml, platform, target, experiment,
                             #do_analysis,
                             #historydir, refinedir, ppdir, do_refinediag,
                             #pp_start, pp_stop, validate,
                             #verbose, quiet, dual,
                             'runtime/production/@simTime')
    sim_units = frelist_xpath(xml, platform, target, experiment,
                              #do_analysis,
                              #historydir, refinedir, ppdir, do_refinediag,
                              #pp_start, pp_stop, validate,
                              #verbose, quiet, dual,
                              'runtime/production/@units')

    rose_suite.set(keys=['template variables', 'HISTORY_DIR'],
                   value=f"'{historydir}'") #value="'{}'".format(historydir))
    # set some dirs to something else to allow bronx dual-pps easily
    if dual:
        rose_suite.set(keys=['template variables', 'PP_DIR'],
                       value=f"'{ppdir}_canopy'")
        rose_suite.set(keys=['template variables', 'ANALYSIS_DIR'],
                       value=f"'{analysis_dir}_canopy'")
    else:
        rose_suite.set(keys=['template variables', 'PP_DIR'],
                       value=f"'{ppdir}'")
        rose_suite.set(keys=['template variables', 'ANALYSIS_DIR'],
                       value=f"'{analysis_dir}'")
    rose_suite.set(keys=['template variables', 'PP_GRID_SPEC'],
                   value=f"'{grid_spec}'")

    ##########################################################################
    # Process the refineDiag scripts into the rose-suite configuration from
    # the <refineDiag> tags in the XML. There is one special <refineDiag>
    # script that contains its own key-value pair: PREANALYSIS. Everything
    # else gets processed into a list of strings under the REFINEDIAG_SCRIPT
    # rose-suite setting. Also, if a script referenced can also be found in
    # Canopy's centralized refineDiag repository, located in the
    # $CYLC_WORKFLOW_DIR/etc/refineDiag, then THOSE references will be used.
    # Otherwise, the reference will be whatever path the XML finds.
    ##########################################################################
    #preanalysis_path_xml = None #notyetimplemented
    #preanalysis_path_cylc = "'{}/{}'".format(CYLC_REFINED_DIR, #notyetimplemented
    #                                         PREANALYSIS_SCRIPT)

    # get the refinediag scripts
    refine_diag_cmd = f"frelist -x {xml} -p {platform} -t {target} {experiment} " \
                                     "--evaluate postProcess/refineDiag/@script"
    refine_diag_process = subprocess.run(refine_diag_cmd,
                                         shell=True,
                                         check=True,
                                         capture_output=True,
                                         universal_newlines=True)
    refine_diag_scripts = refine_diag_process.stdout.strip('\n')

    # If one of the refinediag scripts contains "vitals", assume it
    # won't generate output, so relabel it as a preAnalysis script.
    # There is only one preAnalysis slot currently, so if there are multiple
    # refineDiag scripts that match "vitals" throw away the rest.
    list_refinediags = []
    str_preanalysis = None
    for x in refine_diag_scripts.split():
        if "vitals" in x:
            if str_preanalysis is None:
                str_preanalysis = x
        else:
            list_refinediags.append(x)

    if list_refinediags:
        # turn refinediag off by default in favor of the built-in plevel masking
        rose_suite.set(keys=['template variables', 'DO_REFINEDIAG'], value='False')
        if dual:
            rose_suite.set(keys=['template variables', '#HISTORY_DIR_REFINED'],
                           value=f"'{historydir_refined}_canopy'")
        else:
            rose_suite.set(keys=['template variables', '#HISTORY_DIR_REFINED'],
                           value=f"'{historydir_refined}'")

        rose_suite.set(keys=['template variables', '#REFINEDIAG_SCRIPTS'],
                       value=f"'{' '.join(list_refinediags)}'")

        fre_logger.info( "refineDiag scripts: %s", ' '.join(list_refinediags) )
        fre_logger.info( "NOTE: Now turned off by default; please re-enable in config file if needed" )
    else:
        rose_suite.set(keys=['template variables', 'DO_REFINEDIAG'], value='False')
        fre_logger.info("No refineDiag scripts written. ")

    if str_preanalysis is not None:
        rose_suite.set(keys=['template variables', 'DO_PREANALYSIS'], value='True')
        rose_suite.set(keys=['template variables', 'PREANALYSIS_SCRIPT'],
                       value=f"'{str_preanalysis}'" )
        fre_logger.info( "Preanalysis script: %s", str_preanalysis )
    else:
        rose_suite.set(keys=['template variables', 'DO_PREANALYSIS'], value='False')
        fre_logger.info( "No preAnalysis scripts written." )

    # Grab all of the necessary PP component items/elements from the XML
    comps = frelist_xpath(xml, platform, target, experiment,
                          #do_analysis,
                          #historydir, refinedir, ppdir,
                          #do_refinediag, pp_start, pp_stop, validate,
                          #verbose, quiet, dual,
                          'postProcess/component/@type').split()
    rose_suite.set(keys=['template variables', 'PP_COMPONENTS'],
                   value=f"'{' '.join(sorted(comps))}'" )

    segment_time = frelist_xpath(xml, platform, target, experiment,
                                 #do_analysis,
                                 #historydir, refinedir, ppdir,
                                 #do_refinediag, pp_start, pp_stop, validate,
                                 #verbose, quiet, dual,
                                 'runtime/production/segment/@simTime')
    segment_units = frelist_xpath(xml, platform, target, experiment,
                                  #do_analysis,
                                  #historydir, refinedir, ppdir,
                                  #do_refinediag, pp_start, pp_stop, validate,
                                  #verbose, quiet, dual,
                                  'runtime/production/segment/@units')

    if segment_units == 'years':
        segment = f'P{segment_time}Y'
    elif segment_units == 'months':
        segment = f'P{segment_time}M'
    else:
        fre_logger.error("Unknown segment units: %s", segment_units)
        raise ValueError

    # P12M is identical to P1Y but the latter looks nicer
    if segment == 'P12M':
        segment = 'P1Y'
    rose_suite.set(keys=['template variables', 'HISTORY_SEGMENT'], value=f"'{segment}'" )

    # Get the namelist current_date as the likely PP_START (unless "start" is used in the PP tags)
    # frelist --namelist may be better, but sometimes may not work
    current_date_str = frelist_xpath(xml, platform, target, experiment,
                                     #do_analysis,
                                     #historydir, refinedir, ppdir,
                                     #do_refinediag, pp_start, pp_stop, validate,
                                     #verbose, quiet, dual,
                                     'input/namelist')
    match = re.search(r'current_date\s*=\s*(\d+),(\d+),(\d+)', current_date_str)
    if match:
        try:
            current_date = metomi.isodatetime.data.TimePoint(
                year=match.group(1), month_of_year=match.group(2), day_of_month=match.group(3) )
        except:
            fre_logger.warning("Could not parse date from namelist current_date")
            current_date = None
    else:
        current_date = None
        fre_logger.warning("Could not find current_date in namelists")
    fre_logger.info("current_date (from namelists): %s", current_date)

    # Take a good guess for the PP_START and PP_STOP
    # PP_START could be the coupler_nml/current_date
    # PP_STOP could be the PP_START plus the simulation length
    if sim_units == "years":
        oneless = int(sim_time) - 1
        duration = f"P{oneless}Y"
    elif sim_units == "months":
        duration = f"P{sim_time}M"
    else:
        raise ValueError(f"Was hoping sim_units would be years or months; got {sim_units}")
    dur = metomi.isodatetime.parsers.DurationParser().parse(duration)
    pp_stop = current_date + dur
    rose_suite.set(keys=['template variables', 'PP_START'], value=f'"{current_date}"')
    rose_suite.set(keys=['template variables', 'PP_STOP'], value=f'"{pp_stop}"')

    # Loop over all of the PP components, fetching the sources, xyInterp,
    # and sourceGrid.
    chunks = set()
    comp_count = 0
    for comp in comps:
        comp_count += 1
        pp_comp_xpath_header = f'postProcess/component[@type="{comp}"]'
        fre_logger.info( "Component loop: %s out of %s", comp_count, len(comps))

        # get the comp attributes
        comp_source = frelist_xpath(xml, platform, target, experiment,
                                    #do_analysis,
                                    #historydir, refinedir, ppdir,
                                    #do_refinediag, pp_start, pp_stop, validate,
                                    #verbose, quiet, dual,
                                    f'{pp_comp_xpath_header}/@source' )
        xy_interp = frelist_xpath(xml, platform, target, experiment,
                                  #do_analysis,
                                  #historydir, refinedir, ppdir,
                                  #do_refinediag, pp_start, pp_stop, validate,
                                  #verbose, quiet, dual,
                                  f'{pp_comp_xpath_header}/@xyInterp' )
        source_grid = frelist_xpath(xml, platform, target, experiment,
                                    #do_analysis,
                                    #historydir, refinedir, ppdir,
                                    #do_refinediag, pp_start, pp_stop, validate,
                                    #verbose, quiet, dual,
                                    f'{pp_comp_xpath_header}/@sourceGrid' )
        interp_method = frelist_xpath(xml, platform, target, experiment,
                                      #do_analysis,
                                      #historydir, refinedir, ppdir,
                                      #do_refinediag, pp_start, pp_stop, validate,
                                      #verbose, quiet, dual,
                                      f'{pp_comp_xpath_header}/@interpMethod')

        # split some of the stuffs
        if xy_interp != "":
            interp_split = xy_interp.split(',')
            output_grid_lon = interp_split[1]
            output_grid_lat = interp_split[0]
        if source_grid != "":
            sourcegrid_split = source_grid.split('-')
            input_grid = sourcegrid_split[1]
            input_realm = sourcegrid_split[0]

        # determine the interp method
        if xy_interp:
            if interp_method == "":
                if input_grid == "cubedsphere":
                    interp_method = 'conserve_order2'
                elif input_grid == 'tripolar':
                    interp_method = 'conserve_order1'
                else:
                    raise Exception(f"Expected cubedsphere or tripolar, not {source_grid}")

        # determine the grid label
        if xy_interp:
            grid = f"regrid-xy/{output_grid_lon}_{output_grid_lat}.{interp_method}"
            grid_tail = f"{output_grid_lon}_{output_grid_lat}.{interp_method}"
        else:
            grid = "native"

        sources = set()
        if comp_source.endswith('_refined'):
            fre_logger.info(
                "NOTE: Skipping history file %s, refineDiag is turned off by default.", comp_source)
        else:
            sources.add(comp_source)
        timeseries_count = 0

        # Get the number of TS nodes
        results = frelist_xpath(xml, platform, target, experiment,
                                #do_analysis,
                                #historydir, refinedir, ppdir,
                                #do_refinediag, pp_start, pp_stop, validate,
                                #verbose, quiet, dual,
                                f'{pp_comp_xpath_header}/timeSeries/@freq' ).split()
        timeseries_count = len(results)

        # Loop over the TS nodes and write out the frequency, chunklength, and
        # grid to the remap-pp-components Rose app configuration
        for i in range(1, timeseries_count + 1):
            #label = "{}.{}".format(comp, str(i)) #notyetimplemented

            source = frelist_xpath(xml, platform, target, experiment,
                                   #do_analysis,
                                   #historydir, refinedir, ppdir,
                                   #do_refinediag, pp_start, pp_stop, validate,
                                   #verbose, quiet, dual,
                                   f'{pp_comp_xpath_header}/timeSeries[{i}]/@source' )
            if source.endswith('_refined'):
                fre_logger.info(
                    "NOTE: Skipping history file %s, refineDiag is turned off by default.", source)
            else:
                sources.add(source)

            #freq = freq_from_legacy(frelist_xpath(args,
            #                                      '{}/timeSeries[{}]/@freq'            \
            #                                      .format(pp_comp_xpath_header, i)))
            chunk = chunk_from_legacy(
                frelist_xpath(xml, platform, target, experiment,
                              #do_analysis,
                              #historydir, refinedir, ppdir,
                              #do_refinediag, pp_start, pp_stop, validate,
                              #verbose, quiet, dual,
                              f'{pp_comp_xpath_header}/timeSeries[{i}]/@chunkLength'
                ) )
            chunks.add(chunk)
            #rose_remap.set(keys=[label, 'freq'], value=freq)
            #rose_remap.set(keys=[label, 'chunk'], value=chunk)

        rose_remap.set(keys=[comp, 'sources'], value=' '.join(sources))
        rose_remap.set(keys=[comp, 'grid'], value=grid)

        if grid == "native":
            pass
        else:
            # Write out values to the 'regrid-xy' Rose app
            rose_regrid_xy.set(keys=[comp, 'sources'], value=' '.join(sources))
            rose_regrid_xy.set(keys=[comp, 'inputGrid'], value=input_grid)
            rose_regrid_xy.set(keys=[comp, 'inputRealm'], value=input_realm)
            rose_regrid_xy.set(keys=[comp, 'interpMethod'], value=interp_method)
            rose_regrid_xy.set(keys=[comp, 'outputGridType'], value=grid_tail)
            rose_regrid_xy.set(keys=[comp, 'outputGridLon'], value=output_grid_lon)
            rose_regrid_xy.set(keys=[comp, 'outputGridLat'], value=output_grid_lat)

    # Process all of the found PP chunks into the rose-suite configuration
    fre_logger.info("Setting PP chunks...")

    sorted_chunks = list(chunks)
    sorted_chunks.sort(key=duration_to_seconds, reverse=False)

    if len(chunks) == 0:
        raise ValueError('no chunks found! exit.')

    fre_logger.info("  Chunks found: %s", ', '.join(sorted_chunks))
    if len(chunks) == 1:
        rose_suite.set(['template variables', 'PP_CHUNK_A'],
                       f"'{sorted_chunks[0]}'")
    else:
        rose_suite.set(['template variables', 'PP_CHUNK_A'],
                       f"'{sorted_chunks[0]}'")
        rose_suite.set(['template variables', 'PP_CHUNK_B'],
                       f"'{sorted_chunks[1]}'")
    fre_logger.info("  Chunks used: %s", ', '.join(sorted_chunks[0:2]) )

    # Write out the final configurations.
    fre_logger.info("Writing output files...")

    dumper = metomi.rose.config.ConfigDumper()
    rose_outfiles=[ ( rose_suite,     'rose-suite.conf'                       ),
                    ( rose_remap,     'app/remap-pp-components/rose-app.conf' ),
                    ( rose_regrid_xy, 'app/regrid-xy/rose-app.conf'           ) ]
    for outfile in rose_outfiles:
        fre_logger.info("  %s", outfile[1])
        dumper(outfile[0], outfile[1])

    #outfile = "app/remap-pp-components/rose-app.conf"
    #fre_logger.info("  %s", outfile)
    #dumper(rose_remap, outfile)
    #
    #outfile = "app/regrid-xy/rose-app.conf"
    #fre_logger.info("  %s", outfile)
    #dumper(rose_regrid_xy, outfile)

def _convert(xml, platform, target, experiment, do_analysis=False, historydir=None,
             refinedir=None, ppdir=None, do_refinediag=False, pp_start=None,
             pp_stop=None, validate=False, verbose=False, quiet=False, dual=False):
    """
    Converts a Bronx XML to a Canopy rose-suite.conf
    """

    # Logging settings. The default is throwing only warning messages
    if verbose:
        fre_logger.setLevel( level = logging.INFO )
    elif quiet:
        fre_logger.setLevel( level = logging.ERROR )
    else:
        fre_logger.setLevel( level = logging.WARNING )

    # Set the name of the directory
    name = f"{experiment}__{platform}__{target}"

    # Create the directory if it doesn't exist
    cylc_dir = os.path.expanduser("~/cylc-src")
    new_dir = os.path.join(cylc_dir, name)
    os.makedirs(new_dir, exist_ok=True)

    # Change the current working directory
    xml = os.path.abspath(xml)
    os.chdir(new_dir)

    ##########################################################################
    # NOTE: Ideally we would check that "frelist" is in the PATH here,
    # but in practice the frelist will just fail later if it's not loaded.
    # If that error scenario is too confusing, let's add a check back here.
    cylc_loaded = False
    if validate:
        if CYLC_PATH in os.getenv('PATH'):
            cylc_loaded = True
        else:
            raise EnvironmentError("Cannot run the validator tool because "            \
                                   "the Cylc module isn't loaded. Please "             \
                                   "run 'module load cylc/test' and try again.")

    # Alert the user if only 1 or zero PP years are given as an option, and
    # notify them that a default of '0000' for those years will be set in the
    # rose-suite configuration
    if any( [ pp_stop is None, pp_start is None ] ):
        if pp_start is None:
            fre_logger.warning("PP start year was not specified.")
        if pp_stop is None:
            fre_logger.warning("PP stop year was not specified.")
        fre_logger.warning("After the converter has run, please edit the "                \
                        "default '0000' values within your rose-suite.conf.")

    # These series of conditionals takes into account input from the user
    # (for the PP_START and PP_STOP year) that is not 4 digits or other
    # nonsensical years. The rose-suite config requires 4 digits for years
    # and if the year is under '1000' (but > 0), then leading zeros must be used.
    if all( [ pp_start is not None, pp_stop is not None ] ):
        def format_req_pp_year(pp_year):
            if len(pp_year) < 4 and int(pp_year) > 0:
                pp_year = '0' * (4 - len(pp_year)) + pp_year
            return pp_year
        pp_start = format_req_pp_year(pp_start)
        pp_stop = format_req_pp_year(pp_stop)

        if int(pp_start) >= int(pp_stop):
            fre_logger.warning("Your PP_START date is equal to or later than "            \
                            "your PP_STOP date. Please revise these values in "        \
                            "your configuration after the converter has run.")
        if any( [ len(pp_start) >  4, len(pp_stop) >  4,
                  int(pp_start) <= 0, int(pp_stop) <= 0 ] ):
            fre_logger.warning("At least one of your PP_start or PP_stop years "          \
                            "does not make sense. Please revise this value in "        \
                            "your configuration after the converter has run.")

    main( xml, platform, target, experiment, do_analysis, historydir, refinedir, ppdir,
          do_refinediag, pp_start, pp_stop, validate, verbose, quiet, dual )

    fre_logger.info("XML conversion complete!")

    # Run the Cylc validator tool on the current directory if conditions are met.
    # Note: the user must be running the converter in the parent Cylc Workflow
    # Directory if the validator is run.
    if cylc_loaded:
        fre_logger.info("Running the Cylc validator tool...")
        try:
            subprocess.run("cylc validate .", shell=True, check=True)
        except subprocess.CalledProcessError:
            fre_logger.error("Errant values in rose-suite.conf or other Cylc errors. "    \
                            "Please check your configuration and run the validator "     \
                            "again separately.")
        finally:
            fre_logger.info("Validation step complete!")

##############################################

if __name__ == '__main__':
    convert()
