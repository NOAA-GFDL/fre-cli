"""
Rose Configuration and YAML Processing Utility for FRE Post-Processing (fre pp).

The configure_script_yaml module processes user post-processing YAML files (`pp.yaml`), validates them
against the canonical FRE JSON schema (`fre_pp.json`), consolidates experiment
configurations, and generates the `rose-suite.conf` configuration file required
by Cylc workflows.

Key Workflow Steps:
1. Load and validate combined YAML structures against GFDL FRE JSON schemas.
2. Initialize and configure Rose suite settings (`metomi.rose.config.ConfigNode`).
3. Set workflow template variables (experiments, platforms, targets, diagnostic switches).
4. Write output configuration files to `~/cylc-src/<experiment>__<platform>__<target>/`.
"""

import os
import json
import logging

from pathlib import Path
from jsonschema import validate, SchemaError, ValidationError
import metomi.rose.config

import fre.yamltools.combine_yamls_script as cy

fre_logger = logging.getLogger(__name__)


def validate_yaml(yamlfile: dict) -> None:
    """
    Validate the combined experiment YAML structure against the official FRE JSON schema.

    The schema is loaded from `gfdl_msd_schemas/FRE/fre_pp.json` relative to the package root.

    :param yamlfile: Dictionary containing combined model, settings, post-processing,
                     and analysis specifications.
    :type yamlfile: dict

    :raises ValueError: If the JSON schema is invalid, the combined YAML fails schema validation,
                        or an unexpected error occurs during validation.
    :return: None
    :rtype: None
    """
    schema_dir = Path(__file__).resolve().parents[1]
    schema_path = os.path.join(schema_dir, 'gfdl_msd_schemas', 'FRE', 'fre_pp.json')
    fre_logger.info("Using yaml schema '%s'", schema_path)

    # Load the JSON schema
    try:
        with open(schema_path,'r', encoding='utf-8') as s:
            schema = json.load(s)
    except:
        fre_logger.error("Schema '%s' is not valid. Contact the FRE team.", schema_path)
        raise

    # Validate YAML dictionary against schema
    try:
        validate(instance = yamlfile,schema = schema)
        fre_logger.info("Combined yaml valid")
    except SchemaError as exc:
        raise ValueError(f"Schema '{schema_path}' is not valid. Contact the FRE team.") from exc
    except ValidationError as exc:
        raise ValueError("Combined yaml is not valid. Please fix the errors and try again.") from exc
    except Exception as exc:
        raise ValueError("Unclear error from validation. Please try to find the error and try again.") from exc


def rose_init(experiment: str, platform: str, target: str) -> tuple[metomi.rose.config.ConfigNode, metomi.rose.config.ConfigNode, metomi.rose.config.ConfigNode]:
    """
    Initialize a Rose suite configuration node with default template variables.

    :param experiment: Experiment identifier (e.g., ``'c96L65_am5f4b4r0_amip'``).
    :type experiment: str
    :param platform: FRE platform defined in the platforms yaml
                     If on gaea c5, a FRE platform may look like ncrc5.intel23-classic
    :type platform: str
    :param target: Predefined FRE targets; options include [prod/debug/repro]-openmp
    :type target: str

    :return: An initialized Rose configuration node populated with standard experiment settings.
    :rtype: metomi.rose.config.ConfigNode
    """
    rose_suite = metomi.rose.config.ConfigNode()

    # Set default workflow flags
    rose_suite.set(keys=['template variables', 'DO_ANALYSIS_ONLY'],  value='False')
    rose_suite.set(keys=['template variables', 'DO_MDTF'],  value='False')
    rose_suite.set(keys=['template variables', 'PP_DEFAULT_XYINTERP'],  value='0,0')

    # Set core experiment template identifiers
    rose_suite.set(keys=['template variables', 'EXPERIMENT'], value=f'"{experiment}"')
    rose_suite.set(keys=['template variables', 'PLATFORM'], value=f'"{platform}"')
    rose_suite.set(keys=['template variables', 'TARGET'], value=f'"{target}"')

    # Initialize rose regrid config
    rose_regrid = metomi.rose.config.ConfigNode()
    rose_regrid.set(keys=['command', 'default'], value='regrid-xy')

    # Initialize rose remap config
    rose_remap = metomi.rose.config.ConfigNode()
    rose_remap.set(keys=['command', 'default'], value='remap-pp-components')    

    return(rose_suite, rose_regrid, rose_remap)


def quote_rose_values(value: str) -> str:
    """
    Format and quote string values for `rose-suite.conf` variable definitions.

    Booleans and lists are returned unquoted as strings, while general strings are enclosed
    in single quotes to conform to Rose syntax requirements.

    :param value: Configuration value to format.
    :type value: object

    :return: Formatted configuration value ready for writing to `rose-suite.conf`.
    :rtype: str
    """
    if isinstance(value, bool):
        return f"{value}"
    elif isinstance(value, list):
        return f"{value}"
    else:
        return "'" + str(value) + "'"


def set_rose_suite(yamlfile: dict, rose_suite: metomi.rose.config.ConfigNode) -> None:
    """
    Populate a Rose suite configuration node with settings extracted from a post-processing YAML.

    Parses direct settings, directory structures, pre-analysis scripts, refinediag scripts,
    and analysis execution flags into template variables within `rose_suite`.

    :param yamlfile: Combined dictionary containing model and post-processing configurations.
    :type yamlfile: dict
    :param rose_suite: The Rose configuration node to update.
    :type rose_suite: metomi.rose.config.ConfigNode

    :raises ValueError: If the required `'postprocess'` section is missing from `yamlfile`, or if
                        more than one pre-analysis script is configured (currently unsupported).
    :return: None
    :rtype: None
    """
    pp=yamlfile.get("postprocess")
    dirs=yamlfile.get("directories")
    analysis=yamlfile.get("analysis")

    if dirs is not None:
        for key,value in dirs.items():
            rose_suite.set(keys=['template variables', key.upper()], value=quote_rose_values(value))

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

        # Parse pre-analysis configuration. 
        # Take into account the possibility of multiple scripts being defined (future implementation)
        if pp_key == "preanalysis":
            for k2, v2 in pp_value.items():
                switch = v2["do_preanalysis"]
                if switch is True:
                    script = v2["script"]

                    # If there is already a script defined for preanalysis, fail
                    # More than 1 script is not supported yet
                    if pa_scripts:
                        fre_logger.error("Using more than 1 pre-analysis script is not supported")
                        raise ValueError

                    pa_scripts += f"{script} "

        # Parse refinediag scripts
        # Multiple refineDiag scripts are supported, so take account for those
        if pp_key == "refinediag":
            for k2, v2 in pp_value.items():
                switch = v2["do_refinediag"]
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

    # Set DO_ANALYSIS switch
    # If no analysis section is defined, set DO_ANALYSIS as False
    # If anlaysis section is defined, analysis_on is optional key for each component
    # in the analysis yaml and defaults to True if not specified.
    # In the rose_suite.conf:
    #  - if 'analysis_on: False' for all analysis components, set DO_ANALYSIS=False
    #  - if 'analysis_on: True' for any analysis components, set DO_ANALYSIS=True
    if not analysis:
        rose_suite.set( keys = ['template variables', 'DO_ANALYSIS'],
                        value = 'False' )
        return

    do_analysis_switch = []    
    for an_key, an_value in analysis.items():
        an_workflow_info = an_value["workflow"]
        # if analysis_on key is actually set, evaluate and save its value in a list
        if "analysis_on" in an_workflow_info:
            do_analysis_switch.append(an_workflow_info["analysis_on"])
        #if analysis_on key is NOT set, save its value as True in the list
        else:
            do_analysis_switch.append("True")

    # if ANY of the analysis components do not set analysis_on or set analysis_on as True,
    # set DO_ANALYSIS=True in the rose_suite.conf
    if any(do_analysis_switch):
        rose_suite.set( keys = ['template variables', 'DO_ANALYSIS'],
                        value = 'True' )
    else:
        rose_suite.set( keys = ['template variables', 'DO_ANALYSIS'],
                        value = 'False' )


def yaml_info(yamlfile: str = None, experiment: str = None, platform: str = None, target: str = None) -> None:
    """
    Consolidate experiment YAML files, validate the result, and create `rose-suite.conf`.

    Outputs generated workflow configurations directly into:
    `~/cylc-src/<experiment>__<platform>__<target>/`

    :param yamlfile: Path to model YAML configuration file.
    :type yamlfile: str, optional
    :param experiment: Experiment name (e.g., ``'c96L65_am5f4b4r0_amip'``).
    :type experiment: str, optional
    :param platform: FRE platform defined in the platforms yaml
                     If on gaea c5, a FRE platform may look like ncrc5.intel23-classic
    :type platform: str, optional
    :param target: Predefined FRE targets; options include [prod/debug/repro]-openmp
    :type target: str, optional

    :raises ValueError: If any required argument (`yamlfile`, `experiment`, `platform`, `target`) is None.
    :return: None
    :rtype: None

    .. note::
       This function writes `rose-suite.conf` and a consolidated `<experiment>.yaml` file into
       `~/cylc-src/<workflow_name>/`.
    """
    fre_logger.info('Starting')

    if None in [yamlfile, experiment, platform, target]:
        raise ValueError( 'yamlfile, experiment, platform, and target must all not be None. '
                          'curently, their values are...'
                          f'{yamlfile} / {experiment} / {platform} / {target}')
    e = experiment
    p = platform
    t = target
    yml = yamlfile

    # Initialize the rose configurations
    rose_suite,rose_regrid,rose_remap = rose_init(e,p,t)

    # Combine input YAMLs and save consolidated output to cylc-src
    cylc_dir = os.path.join(os.path.expanduser("~/cylc-src"), f"{e}__{p}__{t}")
    outfile = os.path.join(cylc_dir, f"{e}.yaml")

    full_yamldict = cy.consolidate_yamls(yamlfile = yml,
                                         experiment = e, platform = p, target = t,
                                         use="pp",
                                         output=outfile)

    # Validate combined YAML dictionary against schema
    validate_yaml(full_yamldict)

    # Parse combined dictionary into Rose configuration
    set_rose_suite(full_yamldict,rose_suite)

    # Set regrid and remap rose app items
    set_rose_apps(full_yamldict,rose_regrid,rose_remap)

    # Write output configuration files
    fre_logger.info("Writing output files...")
    fre_logger.info(" %s", outfile)

    dumper = metomi.rose.config.ConfigDumper()
    outfile = os.path.join(cylc_dir, "rose-suite.conf")
    dumper(rose_suite, outfile)
    fre_logger.info("  %s", outfile)

    outfile = os.path.join(cylc_dir, "app", "regrid-xy", "rose-app.conf")
    dumper(rose_regrid, outfile)
    fre_logger.info("  %s", outfile)

    outfile = os.path.join(cylc_dir, "app", "remap-pp-components", "rose-app.conf")
    dumper(rose_remap, outfile)
    fre_logger.info("  %s", outfile)

    fre_logger.info('Finished')
