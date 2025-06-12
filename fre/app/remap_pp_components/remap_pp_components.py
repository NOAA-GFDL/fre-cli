#!/usr/bin/env python
"""
Description: Remap/move components that will be
             post-processed from one convention,
             such as history files, to an
             updated output directory structure
"""
import os
import subprocess
import glob
from pathlib import Path
import logging
import yaml

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def verify_dirs(in_dir,out_dir):
    """
    Verify that the input and output directories exists and are directories
    Params:
        output_dir: output directory
        input_dir: input directory
    """

    # Verify input directory exists and is a directory
    if Path(in_dir).is_dir():
        logger.info("Input directory is a valid directory")
    else:
        raise ValueError(f"Error: Input directory {in_dir} is not a valid directory")

    # Verify output directory exists and is a directory
    if Path(out_dir).is_dir():
        logger.info("Output directory is a valid directory")
    else:
        raise ValueError(f"Error: Output directory {out_dir} is not a valid directory")

def create_dir(out_dir,comp,freq,chunk,ens,dir_ts):
    """
    Create the output directory structure
    Params:
        out_dir: output directory
        comp: component that will be post-processed
        freq: frequency
        chunk: chunk
        ens: ensemble member
        dir_ts: directory time series workaround
    """

    # Define dir
    if ens is not None:
        if dir_ts is not None:
            dirs = f"{comp}/ts/{ens}/{freq}/{chunk}"
        else:
            dirs = f"{comp}/{ens}/{freq}/{chunk}"
    else:
        if dir_ts is not None:
            dirs = f"{comp}/ts/{freq}/{chunk}"
        else:
            dirs = f"{comp}/{freq}/{chunk}"

    # Create dir from outputDir
    os.chdir(out_dir)
    Path(dirs).mkdir(parents=True,exist_ok=True)

    return dirs

def freq_to_legacy(iso_dura):
    """
    Print Bronx-style frequency given an ISO8601 duration
    Params:
        iso_dura: frequency
    """

    if iso_dura=='P1Y':
        freq_legacy = 'annual'
    elif iso_dura=='P1M':
        freq_legacy = 'monthly'
    elif iso_dura=='P3M':
        freq_legacy = 'seasonal'
    elif iso_dura=='P1D':
        freq_legacy = 'daily'
    elif iso_dura=='PT120H':
        freq_legacy = '120hr'
    elif iso_dura=='PT12H':
        freq_legacy = '12hr'
    elif iso_dura=='PT8H':
        freq_legacy = '8hr'
    elif iso_dura=='PT6H':
        freq_legacy = '6hr'
    elif iso_dura=='PT4H':
        freq_legacy = '4hr'
    elif iso_dura=='PT3H':
        freq_legacy = '3hr'
    elif iso_dura=='PT2H':
        freq_legacy = '2hr'
    elif iso_dura=='PT1H':
        freq_legacy = 'hourly'
    elif iso_dura in ['PT30M', 'PT0.5H']:
        freq_legacy = '30min'
    else:
        raise ValueError(f"Could not convert ISO duration '{iso_dura}'")

    return freq_legacy

def chunk_to_legacy(iso_dura):
    """
    Print Bronx-style frequency given an ISO8601 duration
    Params:
        iso_dura: chunk
    """

    if iso_dura[0]=='P':
        if iso_dura[-1:]=='M':
            brx_freq=iso_dura[1]+'mo'
        elif iso_dura[-1:]=='Y':
            brx_freq=iso_dura[1]+'yr'
        else:
            brx_freq = 'error'
    else:
        brx_freq = 'error'

    return brx_freq

def freq_to_date_format(iso_freq):
    """
    Print legacy Bronx-like date template format given a frequency (ISO 8601 duration)
    Params:
        iso_freq: frequency
    """

    if iso_freq=='P1Y':
        return 'CCYY'
    elif iso_freq=='P1M':
        return 'CCYYMM'
    elif iso_freq=='P1D':
        return 'CCYYMMDD'
    elif (iso_freq[:2]=='PT') and (iso_freq[-1:]=='H'):
        return 'CCYYMMDDThh'
    else:
        return f'ERROR: Unknown Frequency {iso_freq}'

def truncate_date(date, freq):
    """
    Print a date string to a truncated precision.
        - Accepts a date and frequency
        - Outputs a date string with suitably reduced precision
        - Test cases: '19790101T0000Z P1D', '19800101T0000Z P1M', '19790101T0000Z PT0.5H'
        - Output using cylc (shared.sh calls in job logs): '19790101', '198001', '1979010100'
    Params:
        date: date to begin post-processing
        freq: frequency
    """

    form = freq_to_date_format(freq)
    logger.info("truncatedateformat: %s", form)
    output = subprocess.Popen(["cylc", "cycle-point", "--template", form, date],
                              stdout=subprocess.PIPE)

    bytedate = output.communicate()[0]
    date=str(bytedate.decode())
    logger.info("truncatedate: %s", date)

    #remove trailing newline
    date=date[:(len(date)-1)]

    #check for and remove 'T' if present
    if not date.isnumeric():
        date=date[:8]+date[-2:]

    return date

def search_files(product,var,source,freq,current_chunk,begin):
    """
    Pattern match and search for the correct files in the chunk directory
    Params:
        var: variables
        source: source history files for post-processed component
        begin: date to begin post-processing
        current_chunk: current chunk to post-process
        freq: frequency
    """
    files = []
    # with glob - files found as list
    if freq == "P0Y":
        if var == "all":
            f = glob.glob(f"{source}.*.nc")
            files.extend(f)
        else:
            for v in var:
                f = glob.glob(f"{source}.{v}*.nc")
                files.extend(f)
    else:
        if product == "ts":
            date = truncate_date(begin, freq)
            logger.info("date: %s", date)
        elif product == "av":
            date = truncate_date(begin, "P1Y")
        else:
            raise ValueError("Product not set to ts or av.")

        if var == "all":
            f = glob.glob(f"{source}.{date}-*.*.nc")
            files.extend(f)
        else:
            for v in var:
                logger.info("var: %s", v)
                f = glob.glob(f"{source}.{date}-*.{v}*.nc")
                files.extend(f)

        if product == "av" and current_chunk == "P1Y":
            f = glob.glob(f"{source}.{date}.*.nc")
            files.extend(f)

    return files

def get_variables(comp_info, product, req_source):
    """
    Retrieve variables listed for a component; save in dictionary for use later
    Params:
        comp_info: dictionary of information about requested component
        product: static, ts, or av
    """
    if product == "static":
        if comp_info.get("static") is None:
            raise ValueError(f"Product is set to static but no static sources/variables defined for {comp_info.get('type')}")

        for static_info in comp_info.get("static"):
            if static_info.get("source") == req_source:
                if static_info.get("variables") is None:
                    v = "all"
                else:
                    v = static_info.get("variables")

#            if static_info.get("offline_source") is not None:
#                if static_info.get("variables") is None:
#                    v = "all"
#                else:
#                    v = static_info.get("variables")
    else:
        for src_info in comp_info.get("sources"): #history_file,variables
            if src_info.get("history_file") == req_source:
                if src_info.get("variables") is None:
                    v = "all"
                else:
                    v = src_info.get("variables")

    return v

def get_sources(comp_info, product):
    """
    Retrieve source name for a component
    Params:
        comp_info: dictionary of information about requested component
        product: static, ts, or av
    """
    sources = []
    if "static" in product:
        for static_info in comp_info.get("static"):
            if static_info.get("source") is not None:
                sources.append(static_info.get("source"))
    else:
        for src_info in comp_info.get("sources"):
            sources.append(src_info.get("history_file"))

    return sources

def get_freq(comp_info):
    """
    Return the frequency
    Param:
        comp_info: dictionary of information about requested component
    """
    if "freq" not in comp_info.keys():
        freq = glob.glob("*")
    else:
        freq = comp_info.get("freq")

    return freq

def get_chunk(comp_info):
    """
    Return the chunk size
    Param:
        comp_info: dictionary of information about requested component
    """
    if "chunk" not in comp_info.keys():
        chunk = glob.glob("*")
    else:
        chunk = comp_info.get("chunk")

    return chunk
##################################### MAIN FUNCTION #####################################
def remap_pp_components(input_dir, output_dir, begin_date, current_chunk,
                        product, components, copy_tool, yaml_config,
                        ts_workaround, ens_mem):
    """
    Remap netcdf files to an updated output directory structure
    Params:
        input_dir: input directory
        output_dir: output directory
        begin: date to begin post-processing
        current_chunk: current chunk to post-process
        components: components that will be post-processed
        product: variable to define time series or time averaging
        ts_workaround: time series workaround
        ens_mem: ensemble member number
        copy_tool: tool to use for copying files
        yaml_config: yaml configuration file
    """

#    # Set variables
#    input_dir         = os.getenv('inputDir')
#    output_dir        = os.getenv('outputDir')
#    begin             = os.getenv('begin')
#    current_chunk     = os.getenv('currentChunk')
#    components        = os.getenv('components')
#    yaml_config       = os.getenv('yaml_config')
#    product           = os.getenv('product')
#    dir_ts_workaround = os.getenv('dirTSWorkaround')
#    ens_mem           = os.getenv('ens_mem')

    logger.info("Arguments:")
    logger.info("    input dir: %s", input_dir)
    logger.info("    output dir: %s", output_dir)
    logger.info("    begin: %s", begin_date)
    logger.info("    current chunk: %s", current_chunk)
    logger.info("    components: %s", components)
    logger.info("    product: %s", product)
    logger.info("    copy tool: %s", copy_tool)
    logger.info("    yaml config: %s", yaml_config)
#    if ts_workaround is not "None":
    if not ts_workaround: ## if ts_workaround is an empty string
        ts_workaround = None
        logger.info("    dirTSWorkaround: None")
    else:
        logger.info("    dirTSWorkaround: %s", ts_workaround)
#    if ens_mem is not "None":
    if not ens_mem:  ## if ens_mem is an empty string
        ens_mem = None
        logger.info("    ens_mem: None")
    else:
        logger.info("    ens_mem: %s", ens_mem)

    # Path to yaml configuration
    exp_dir = Path(__file__).resolve().parents[3]
    path_to_yamlconfig = os.path.join(exp_dir, yaml_config)
    # Load and read yaml configuration
    with open(path_to_yamlconfig,'r') as yml:
        yml_info = yaml.safe_load(yml)

    # Verify the input and output directories
    verify_dirs(input_dir, output_dir)

    # Start in input directory)
    os.chdir(input_dir)

    # loop through components to be post processed
    # list of components
    comps = components.split()
    for comp in comps:
        comp = comp.strip('""')

        # Make sure component/source is in the yaml configuration file
        for comp_info in yml_info["postprocess"]["components"]:
            yaml_components = comp_info.get("type")

            # Check that pp_components defined matches those in the yaml file
            logger.debug(f"Is {comp} in {yaml_components}?")
            if comp in yaml_components:
                logger.debug('Yes')
            else:
                logger.warning("WARNING: component %s does not exist in yaml config", comp)
                continue

            # Continue if not looking at correct information for requested component
            if comp != comp_info.get("type"):
                logger.warning("Info not associated with component, %s, requested", comp)
                continue

            offline_srcs=[]
            #if static but no static defined, skip
            if product == "static":
                if comp_info.get("static") is None:
                    logger.warning('Product set to "static" but no static source requested defined')
                    continue

                # Save list of offline sources (if defined) for later
                for static_info in comp_info.get("static"):
                    if static_info.get("offline_source") is None:
                        continue

                    offline_srcs.append(static_info.get("offline_source"))

            ## Loop through grid
            # Set grid type if component has xyInterp defined or not
            grid = []
            if "xyInterp" not in comp_info.keys():
                grid.append("native")
            else:
                interp = comp_info.get("xyInterp").split(",")
                interp = '_'.join(interp)
                interp_method = comp_info.get("interpMethod")
                grid.append(f"regrid-xy/{interp}.{interp_method}")

            for g in grid:
                if ens_mem is not None:
                    newdir = f"{input_dir}/{g}/{ens_mem}"
                    os.chdir(newdir)
                else:
                    os.chdir(f"{input_dir}/{g}")

                ## Loop through sources
                sources = get_sources(comp_info, product)
                for s in sources:
                    if ens_mem is not None:
                        source_dir = os.path.join(input_dir, g, ens_mem, s)
                    else:
                        source_dir = os.path.join(input_dir, g, s)
                    if not os.path.exists(source_dir) and product == "av":
                        logger.info("Source directory '%s' does not exist, but this could be expected, so skipping.", source_dir)
                        continue
                    os.chdir(source_dir)

                    ## Loop through freq
                    freq = get_freq(comp_info) ###might have to be a list

                    for f in freq:
                        if ens_mem is not None:
                            os.chdir(f"{input_dir}/{g}/{ens_mem}/{s}/{f}")
                        else:
                            os.chdir(f"{input_dir}/{g}/{s}/{f}")

                        ## Loop through chunk
                        chunk = get_chunk(comp_info)  ## might have to be a list ...
                        for c in chunk:
                            if c != current_chunk:
                                continue
                            if ens_mem is not None:
                                os.chdir(f"{input_dir}/{g}/{ens_mem}/{s}/{f}/{c}")
                            else:
                                os.chdir(f"{input_dir}/{g}/{s}/{f}/{c}")

                            # Create directory
                            # ts output is written to final location, av is not.
                            # so convert the ts only to bronx-style
                            if product == "ts":
                                dirs = create_dir(out_dir = output_dir,
                                                  comp = comp,
                                                  freq = freq_to_legacy(f),
                                                  chunk = chunk_to_legacy(c),
                                                  ens = ens_mem,
                                                  dir_ts = ts_workaround)
                            else:
                                dirs = create_dir(out_dir = output_dir,
                                                  comp = comp,
                                                  freq = f,
                                                  chunk = c,
                                                  ens = ens_mem,
                                                  dir_ts = ts_workaround)

                            logger.info("directory created: %s", dirs)

                            # Search for files in chunk directory
                            if ens_mem is not None:
                                os.chdir(f"{input_dir}/{g}/{ens_mem}/{s}/{f}/{c}")
                            else:
                                os.chdir(f"{input_dir}/{g}/{s}/{f}/{c}")

                            ## VARIABLE INFORMATION for requested source
                            # Note: variable filtering not done for offline static diagnostics
                            v = get_variables(comp_info, product, s)

                            files = search_files(product = product,
                                                 var = v,
                                                 source = s,
                                                 freq = f,
                                                 current_chunk = current_chunk,
                                                 begin = begin_date)

                            logger.info(f"{len(files)} files found for component '{comp}', source '{s}', product '{product}', grid '{g}', chunk '{c}', variables '{v}': {files}")

                            if not files:
                                if ens_mem is not None:
                                    raise ValueError("\nError: No input files found in",
                                                    f"{input_dir}/{g}/{ens_mem}/{s}/{f}/{c}")
                                else:
                                    raise ValueError("\nError: No input files found in",
                                                    f"{input_dir}/{g}/{s}/{f}/{c}")

                            os.chdir(output_dir)

                            for file in files:
                                newfile1 = file.split(".",1)[1]
                                newfile2 = f"{s}.{newfile1}"
                                # If file exists, remove it
                                # (would exist if workflow was run previously)
                                output_file = os.path.join(output_dir, dirs, newfile2)
                                if os.path.exists(output_file):
                                    os.remove(output_file)
                                logger.info("NEWFILE2: %s", newfile2)
                                # Symlink or copy the file for the specified
                                # component in the output directory
                                if ens_mem is not None:
                                    link = ["ln",
                                            f"{input_dir}/{g}/{ens_mem}/{s}/{f}/{c}/{file}",
                                            f"{output_dir}/{dirs}/{newfile2}"]
                                else:
                                    link = ["ln",
                                            f"{input_dir}/{g}/{s}/{f}/{c}/{file}",
                                            f"{output_dir}/{dirs}/{newfile2}"]

                                run = subprocess.run( link, check = False )
                                ret = run.returncode

                                if ret != 0:
                                    if ens_mem is None:
                                        copy = [f"{copy_tool}",
                                                f"{input_dir}/{g}/{s}/{f}/{c}/{file}",
                                                f"{output_dir}/{dirs}/{newfile2}" ]
                                        subprocess.run( copy, check = False )
                                    else:
                                        copy = [f"{copy_tool}",
                                                f"{input_dir}/{g}/{ens_mem}/{s}/{f}/{c}/{file}",
                                                f"{output_dir}/{dirs}/{newfile2}" ]
                                        subprocess.run( copy, check = False )

                            # Symlink or copy the offline diagnostic file for the
                            # specified component in the output directory.
                            # Offline diagnostic files will then be in the same
                            # location as other static files to be combined.
                            if offline_srcs is not None:
                                for src_file in offline_srcs:
                                    if not Path(src_file).exists():
                                        raise ValueError(f"Offline diagnostic file defined but {src_file} does not exist or cannot be found!")

                                    offline_link = ["ln",
                                                    "-s",
                                                    f"{src_file}",
                                                    f"{output_dir}/{dirs}"]
                                    offline_link_run = subprocess.run( offline_link, check = False )
                                    offline_link_ret = offline_link_run.returncode

                                    if offline_link_ret != 0:
                                        #raise ValueError("copy failed")
                                        offline_copy = ["{copy_tool}",
                                                        f"{src_file}",
                                                        f"{output_dir}/{dirs}"]
                                        subprocess.run( offline_copy, check = False )

    logger.info("Component remapping complete")

#if __name__ == '__main__':
#    remap()
