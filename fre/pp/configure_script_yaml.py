"""
Script creates the rose-suite file
for the workflow from the pp yaml.
"""

import os
import json
import logging

from pathlib import Path
from jsonschema import validate, SchemaError, ValidationError
import metomi.rose.config

import fre.yamltools.combine_yamls_script as cy

fre_logger = logging.getLogger(__name__)

######VALIDATE#####
def validate_yaml(yamlfile: dict) -> None:
    """
    Validate the format of the yaml file based
    on the schema.json in gfdl_msd_schemas

    :param yamlfile: Model, settings, pp, and analysis yaml
                     information combined into a dictionary
    :type yamlfile: dict
    :raises ValueError:
        - if gfdl_mdf_schema path is not valid
        - combined yaml is not valid
        - unclear error in validation
    :return: None
    :rtype: None
    """
    schema_dir = Path(__file__).resolve().parents[1]
    schema_path = os.path.join(schema_dir, 'gfdl_msd_schemas', 'FRE', 'fre_pp.json')
    fre_logger.info("Using yaml schema '%s'", schema_path)
    # Load the json schema: .load() (vs .loads()) reads and parses the json in one)
    try:
        with open(schema_path,'r', encoding='utf-8') as s:
            schema = json.load(s)
    except:
        fre_logger.error("Schema '%s' is not valid. Contact the FRE team.", schema_path)
        raise

    # Validate yaml
    # If the yaml is not valid, the schema validation will raise errors and exit
    try:
        validate(instance = yamlfile,schema=schema)
        fre_logger.info("Combined yaml valid")
    except SchemaError as exc:
        raise ValueError(f"Schema '{schema_path}' is not valid. Contact the FRE team.") from exc
    except ValidationError as exc:
        raise ValueError("Combined yaml is not valid. Please fix the errors and try again.") from exc
    except Exception as exc:
        raise ValueError("Unclear error from validation. Please try to find the error and try again.") from exc

####################
def rose_init(experiment: str, platform: str, target: str) -> metomi.rose.config.ConfigNode:
    """
    Initializes the rose suite configuration.

    :param experiment: Name of post-processing experiment, default None
    :type experiment: str
    :param platform: Name of platform to use, default None
    :type platform: str
    :param target: Name of target ([prod/debug/repro]-openmp)
    :type target: str
    :return:
        - rose_suite: class within Rose python library; represents
                      elements of the rose-suite configuration
    :rtype:
        - rose_suite: metomi.rose.config.ConfigNode class
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

    return rose_suite

####################
def quote_rose_values(value: str) -> str:
    """
    rose-suite.conf template variables must be quoted unless they are
    boolean or a list, in which case do not quote them.

    :param value: rose-suite configuration value 
    :type value: str
    :return: quoted rose-suite configuration value
    :rtype: str
    """
    if isinstance(value, bool):
        return f"{value}"
    elif isinstance(value, list):
        return f"{value}"
    else:
        return "'" + str(value) + "'"

####################
def set_rose_suite(yamlfile: dict, rose_suite: metomi.rose.config.ConfigNode) -> None:
    """
    Sets items in the rose suite configuration.

    :param yamlfile: Model, settings, pp, and analysis yaml
                     information combined into a dictionary
    :type yamlfile: dict
    :param rose_suite: class within Rose python library; represents 
                       elements of the rose-suite configuration 
    :type rose_suite: metomi.rose.config.ConfigNode; class
    :raises ValueError:
        - if the postproces section of the yaml is not defined
        - if more than 1 pre-analysis script is defined
    :return: None
    :rtype: None
    """
    pp=yamlfile.get("postprocess")
    dirs=yamlfile.get("directories")

    # set rose-suite items
    pa_scripts = ""
    rd_scripts = ""
    if pp is None:
        fre_logger.error("Missing 'postprocess' section!")
        raise ValueError

    for pp_key, pp_value in pp.items():
        if pp_key == "settings" or pp_key == "switches":
            for key,value in pp_value.items():
                if not isinstance(pp_value, list):
                    if key in ['pp_start', 'pp_stop']:
                        if isinstance(value, int):
                            value = f"{value:04}"

                    rose_suite.set( keys = ['template variables', key.upper()],
                                    value = quote_rose_values(value) )

        # Account for multiple scripts for refinediag
        # Fail if multiple scripts defined for preanalysis (not implemented yet)
        if pp_key == "first-step-user-scripts":
            for k2, v2 in pp_value.items():
                switch = v2["switch"]
                if switch is True:
                    script = v2["script"]

                    # If there is already a script defined for preanalysis, fail
                    # More than 1 script is not supported yet
                    if pa_scripts:
                        fre_logger.error("Using more than 1 pre-analysis script is not supported")
                        raise ValueError

                    pa_scripts += f"{script} "

        if pp_key == "refinediag-user-scripts":
            for k2, v2 in pp_value.items():
                switch = v2["switch"]
                if switch is True:
                    script = v2["script"]
                    rd_scripts += f"{script} "

    # Add refinediag switch and string of scripts if specified
    # Note: trailing space on script variables is removed for when the string
    #       is split (by spaces) in the workflow
    if rd_scripts:
        rose_suite.set( keys = ['template variables', 'DO_REFINEDIAG'],
                        value = 'True' )
        rose_suite.set( keys = ['template variables', 'REFINEDIAG_SCRIPTS'],
                        value = quote_rose_values(rd_scripts.rstrip()) )
    else:
        rose_suite.set( keys = ['template variables', 'DO_REFINEDIAG'],
                        value = 'False' )

    # Add preanalysis switch and string of scripts if specified
    if pa_scripts:
        rose_suite.set( keys = ['template variables', 'DO_PREANALYSIS'],
                        value = 'True' )
        rose_suite.set( keys = ['template variables', 'PREANALYSIS_SCRIPT'],
                        value = quote_rose_values(pa_scripts.rstrip()) )
    else:
        rose_suite.set( keys = ['template variables', 'DO_PREANALYSIS'],
                        value = 'False' )

    if dirs is not None:
        for key,value in dirs.items():
            rose_suite.set(keys=['template variables', key.upper()], value=quote_rose_values(value))

####################
def yaml_info(yamlfile: str = None, experiment: str = None, platform: str = None, target: str = None) -> None:
    """
    Using a valid pp.yaml, the rose-suite configuration file is created
    in the cylc-src directory. The pp.yaml is also copied to the cylc-src
    directory.

    :param yamlfile: Path to YAML file used for experiment configuration, default None
    :type yamlfile: str
    :param experiment: One of the postprocessing experiment names from the yaml displayed
                       by fre list exps -y $yamlfile (e.g. c96L65_am5f4b4r0_amip), default None
    :type experiment: str
    :param platform: The location + compiler that was used to run the model 
                     (e.g. gfdl.ncrc5-deploy), default None
    :type platform: str
    :param target: Options used for the model compiler (e.g. prod-openmp), default None
    :type target: str
    :raises ValueError: if experiment, platform, target or yamlfile is None
    :return: None
    :rtype: None

    .. note:: In this function, outfile is defined and used with consolidate_yamls.
              This will create a final, combined yaml file in the ~/cylc-src/[workflow_id]
              directory. Additionally, rose-suite information is being dumped into its own
              configuration file in the cylc-src directory.
    """
    fre_logger.info('Starting')

    if None in [yamlfile, experiment, platform, target]:
        raise ValueError( 'yamlfile, experiment, platform, and target must all not be None.'
                          'currently, their values are...'
                          f'{yamlfile} / {experiment} / {platform} / {target}')
    e = experiment
    p = platform
    t = target
    yml = yamlfile

    # Initialize the rose configurations
    rose_suite = rose_init(e,p,t)

    # Combine model, experiment, and analysis yamls
    cylc_dir = os.path.join(os.path.expanduser("~/cylc-src"), f"{e}__{p}__{t}")
    outfile = os.path.join(cylc_dir, f"{e}.yaml")
    full_yamldict = cy.consolidate_yamls(yamlfile = yml,
                                         experiment = e, platform = p, target = t,
                                         use = "pp",
                                         output = outfile)

    # Validate yaml
    validate_yaml(full_yamldict)

    ## PARSE COMBINED YAML TO CREATE CONFIGS
    # Set rose-suite items
    set_rose_suite(full_yamldict, rose_suite)

    # Write output files
    fre_logger.info("Writing output files...")
    fre_logger.info("  %s", outfile)

    dumper = metomi.rose.config.ConfigDumper()
    outfile = os.path.join(cylc_dir, "rose-suite.conf")
    dumper(rose_suite, outfile)
    fre_logger.info("  %s", outfile)

    fre_logger.info('Finished')
