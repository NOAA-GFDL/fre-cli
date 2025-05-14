"""
    Script creates rose-apps and rose-suite
    files for the workflow from the pp yaml.
"""

## TO-DO:
# - condition where there are multiple pp yamls
# - validation here or in combined-yamls tools

import os
import json

from pathlib import Path
from jsonschema import validate, SchemaError, ValidationError
import yaml
import metomi.rose.config

import fre.yamltools.combine_yamls_script as cy

import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

####################
def yaml_load(yamlfile):
    """
    Load the given yaml.
    """
    # Load the main yaml
    with open(yamlfile,'r') as f:
        y=yaml.safe_load(f)

    return y

######VALIDATE#####
def validate_yaml(yamlfile):
    """
     Using the schema.json file, the yaml format is validated.
    """
    schema_dir = Path(__file__).resolve().parents[1]
    schema_path = os.path.join(schema_dir, 'gfdl_msd_schemas', 'FRE', 'fre_pp.json')
    logger.info(f"Using yaml schema '{schema_path}'")
    # Load the json schema: .load() (vs .loads()) reads and parses the json in one)
    try:
        with open(schema_path,'r') as s:
            schema = json.load(s)
    except:
        logger.error(f"Schema '{schema_path}' is not valid. Contact the FRE team.")
        raise

    # Validate yaml
    # If the yaml is not valid, the schema validation will raise errors and exit
    try:
        validate(instance=yamlfile,schema=schema)
        logger.info("Combined yaml valid")
    except SchemaError:
        logger.error(f"Schema '{schema_path}' is not valid. Contact the FRE team.")
        raise
    except ValidationError:
        logger.error("Combined yaml is not valid. Please fix the errors and try again.")
        raise
    except:
        logger.error("Unclear error from validation. Please try to find the error and try again.")
        raise

####################
def rose_init(experiment,platform,target):
    """
    Initialize the rose suite and app configurations.
    """
    # initialize rose suite config
    rose_suite = metomi.rose.config.ConfigNode()
    # disagreeable; these should be optional
    rose_suite.set(keys=['template variables', 'DO_ANALYSIS_ONLY'],  value='False')
    rose_suite.set(keys=['template variables', 'DO_MDTF'],  value='False')
    rose_suite.set(keys=['template variables', 'PP_DEFAULT_XYINTERP'],  value='0,0')

    # set some rose suite vars
    rose_suite.set(keys=['template variables', 'EXPERIMENT'], value=f'"{experiment}"')
    rose_suite.set(keys=['template variables', 'PLATFORM'], value=f'"{platform}"')
    rose_suite.set(keys=['template variables', 'TARGET'], value=f'"{target}"')

    # initialize rose regrid config
    rose_regrid = metomi.rose.config.ConfigNode()
    rose_regrid.set(keys=['command', 'default'], value='regrid-xy')

    # initialize rose remap config
    rose_remap = metomi.rose.config.ConfigNode()
    rose_remap.set(keys=['command', 'default'], value='remap-pp-components')

    return(rose_suite,rose_regrid,rose_remap)

####################
def quote_rose_values(value):
    """
    rose-suite.conf template variables must be quoted unless they are
    boolean or a list, in which case do not quote them.
    """
    if isinstance(value, bool):
        return f"{value}"
    elif isinstance(value, list):
        return f"{value}"
    else:
        return "'" + str(value) + "'"

####################
def set_rose_suite(yamlfile,rose_suite):
    """
    Set items in the rose suite configuration.
    """
    pp=yamlfile.get("postprocess")
    dirs=yamlfile.get("directories")

    # set rose-suite items
    if pp is not None:
        for i in pp.values():
            if not isinstance(i,list):
                for key,value in i.items():
                    # if pp start/stop is specified as integer, pad zeros
                    # or else cylc validate will fail
                    if key == 'pp_start' or key == 'pp_stop':
                        if isinstance(value, int):
                            value = f"{value:04}"
                    # rose-suite.conf is somewhat finicky with quoting
                    # cylc validate will reveal any complaints
                    rose_suite.set( keys = ['template variables', key.upper()],
                                    value = quote_rose_values(value) )
    if dirs is not None:
        for key,value in dirs.items():
            rose_suite.set(keys=['template variables', key.upper()], value=quote_rose_values(value))

####################
def set_rose_apps(yamlfile,rose_regrid,rose_remap):
    """
    Set items in the regrid and remap rose app configurations.
    """
    components = yamlfile.get("postprocess").get("components")
    for i in components:
        comp = i.get('type')

        # Get sources
        sources = []
        for s in i.get('sources'):
            sources.append(s.get("history_file"))

        #source_str = ' '.join(sources)
        interp_method = i.get('interpMethod')

        # set remap items
        rose_remap.set(keys=[f'{comp}', 'sources'], value=f'{sources}')
        # if xyInterp doesnt exist, grid is native
        if i.get("xyInterp") is None:
            rose_remap.set(keys=[f'{comp}', 'grid'], value='native')

        # if xyInterp exists, component can be regridded
        else:
            interp_split = i.get('xyInterp').split(',')
            rose_remap.set(keys=[f'{comp}', 'grid'],
                           value=f'regrid-xy/{interp_split[0]}_{interp_split[1]}.{interp_method}')

        # set regrid items
        if i.get("xyInterp") is not None:
            sources = []
            for s in i.get("sources"):
                sources.append(s.get("history_file"))
            # Add static sources to sources list if defined
            if i.get("static") is not None:
                for s in i.get("static"):
                    sources.append(s.get("source"))

            rose_regrid.set(keys=[f'{comp}', 'sources'], value=f'{sources}')
            rose_regrid.set(keys=[f'{comp}', 'inputRealm'], value=f'{i.get("inputRealm")}')
            rose_regrid.set(keys=[f'{comp}', 'inputGrid'], value=f'{i.get("sourceGrid")}')
            rose_regrid.set(keys=[f'{comp}', 'interpMethod'], value=f'{interp_method}')
            interp_split = i.get('xyInterp').split(',')
            rose_regrid.set(keys=[f'{comp}', 'outputGridLon'], value=f'{interp_split[1]}')
            rose_regrid.set(keys=[f'{comp}', 'outputGridLat'], value=f'{interp_split[0]}')
            rose_regrid.set(keys=[f'{comp}', 'outputGridType'],
                            value=f'{interp_split[0]}_{interp_split[1]}.{interp_method}')

####################
def yaml_info(yamlfile = None, experiment = None, platform = None, target = None):
    """
    Using a valid pp.yaml, the rose-app and rose-suite
    configuration files are created in the cylc-src
    directory. The pp.yaml is also copied to the
    cylc-src directory.
    """
    logger.info('Starting')

    if None in [yamlfile, experiment, platform, target]:
        raise ValueError( 'yamlfile, experiment, platform, and target must all not be None.'
                          'currently, their values are...'
                          f'{yamlfile} / {experiment} / {platform} / {target}')
    e = experiment
    p = platform
    t = target
    yml = yamlfile

    # Initialize the rose configurations
    rose_suite,rose_regrid,rose_remap = rose_init(e,p,t)

    # Combine model, experiment, and analysis yamls
    cylc_dir = os.path.join(os.path.expanduser("~/cylc-src"), f"{e}__{p}__{t}")
    outfile = os.path.join(cylc_dir, f"{e}.yaml")

    full_yamldict = cy.consolidate_yamls(yamlfile = yml,
                                         experiment = e,
                                         platform = p,
                                         target = t,
                                         use = "pp",
                                         output = outfile)

    # Validate yaml
    validate_yaml(full_yamldict)

    ## PARSE COMBINED YAML TO CREATE CONFIGS
    # Set rose-suite items
    set_rose_suite(full_yamldict,rose_suite) ####comb_pp_yaml,rose_suite)

    # Set regrid and remap rose app items
    set_rose_apps(full_yamldict,rose_regrid,rose_remap) ####comb_pp_yaml,rose_regrid,rose_remap)

    # Write output files
    logger.info("Writing output files...")
    logger.info("  " + outfile)

    dumper = metomi.rose.config.ConfigDumper()
    outfile = os.path.join(cylc_dir, "rose-suite.conf")
    dumper(rose_suite, outfile)
    logger.info("  " + outfile)

    outfile = os.path.join(cylc_dir, "app", "regrid-xy", "rose-app.conf")
    dumper(rose_regrid, outfile)
    logger.info("  " + outfile)

    outfile = os.path.join(cylc_dir, "app", "remap-pp-components", "rose-app.conf")
    dumper(rose_remap, outfile)
    logger.info("  " + outfile)

    logger.info('Finished')

# Use parseyaml function to parse created edits.yaml
if __name__ == '__main__':
    yaml_info()
