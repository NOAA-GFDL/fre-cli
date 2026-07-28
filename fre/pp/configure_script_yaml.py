"""
Rose Configuration and YAML Processing Utility for FRE Post-Processing (fre pp).

This module processes user post-processing YAML files (`pp.yaml`), validates them
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
        with open(schema_path, 'r', encoding='utf-8') as s:
            schema = json.load(s)
    except Exception as exc:
        fre_logger.error("Schema '%s' is not valid. Contact the FRE team.", schema_path)
        raise exc

    # Validate YAML dictionary against schema
    try:
        validate(instance=yamlfile, schema=schema)
        fre_logger.info("Combined yaml valid")
    except SchemaError as exc:
        raise ValueError(f"Schema '{schema_path}' is not valid. Contact the FRE team.") from exc
    except ValidationError as exc:
        raise ValueError("Combined yaml is not valid. Please fix the errors and try again.") from exc
    except Exception as exc:
        raise ValueError("Unclear error from validation. Please try to find the error and try again.") from exc


def rose_init(experiment: str, platform: str, target: str) -> metomi.rose.config.ConfigNode:
    """
    Initialize a Rose suite configuration node with default template variables.

    :param experiment: Post-processing experiment identifier (e.g., ``'c96L65_am5f4b4r0_amip'``).
    :type experiment: str
    :param platform: Target platform and compiler combination (e.g., ``'gfdl.ncrc5-deploy'``).
    :type platform: str
    :param target: Compilation options string (e.g., ``'prod-openmp'``).
    :type target: str

    :return: An initialized Rose configuration node populated with standard experiment settings.
    :rtype: metomi.rose.config.ConfigNode
    """
    rose_suite = metomi.rose.config.ConfigNode()

    # Set default workflow flags
    rose_suite.set(keys=['template variables', 'DO_ANALYSIS_ONLY'], value='False')
    rose_suite.set(keys=['template variables', 'DO_MDTF'], value='False')
    rose_suite.set(keys=['template variables', 'PP_DEFAULT_XYINTERP'], value='0,0')

    # Set core experiment template identifiers
    rose_suite.set(keys=['template variables', 'EXPERIMENT'], value=f'"{experiment}"')
    rose_suite.set(keys=['template variables', 'PLATFORM'], value=f'"{platform}"')
    rose_suite.set(keys=['template variables', 'TARGET'], value=f'"{target}"')

    return rose_suite


def quote_rose_values(value: object) -> str:
    """
    Format and quote string values for `rose-suite.conf` variable definitions.

    Booleans and lists are returned unquoted as strings, while general strings are enclosed
    in single quotes to conform to Rose syntax requirements.

    :param value: Configuration value to format.
    :type value: object

    :return: Formatted configuration value ready for writing to `rose-suite.conf`.
    :rtype: str
    """
    if isinstance(value, (bool, list)):
        return f"{value}"
    return f"'{value}'"


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
    pp = yamlfile.get("postprocess")
    dirs = yamlfile.get("directories")
    analysis = yamlfile.get("analysis")

    if dirs is not None:
        for key, value in dirs.items():
            rose_suite.set(
                keys=['template variables', key.upper()],
                value=quote_rose_values(value)
            )

    if pp is None:
        fre_logger.error("Missing 'postprocess' section!")
        raise ValueError("Missing 'postprocess' section in configuration YAML.")

    pa_scripts = ""
    rd_scripts = ""

    for pp_key, pp_value in pp.items():
        if pp_key in ("settings", "switches"):
            for key, value in pp_value.items():
                if not isinstance(pp_value, list):
                    if key in ['pp_start', 'pp_stop'] and isinstance(value, int):
                        value = f"{value:04}"
                    rose_suite.set(
                        keys=['template variables', key.upper()],
                        value=quote_rose_values(value)
                    )

        # Parse pre-analysis configuration
        if pp_key == "preanalysis":
            for k2, v2 in pp_value.items():
                if v2.get("do_preanalysis") is True:
                    script = v2["script"]
                    if pa_scripts:
                        fre_logger.error("Using more than 1 pre-analysis script is not supported")
                        raise ValueError("Multiple pre-analysis scripts are not supported.")
                    pa_scripts += f"{script} "

        # Parse refinediag scripts
        if pp_key == "refinediag":
            for k2, v2 in pp_value.items():
                if v2.get("do_refinediag") is True:
                    script = v2["script"]
                    rd_scripts += f"{script} "

    # Configure refinediag settings
    if rd_scripts:
        rose_suite.set(keys=['template variables', 'DO_REFINEDIAG'], value='True')
        rose_suite.set(
            keys=['template variables', 'REFINEDIAG_SCRIPTS'],
            value=quote_rose_values(rd_scripts.rstrip())
        )
    else:
        rose_suite.set(keys=['template variables', 'DO_REFINEDIAG'], value='False')

    # Configure pre-analysis settings
    if pa_scripts:
        rose_suite.set(keys=['template variables', 'DO_PREANALYSIS'], value='True')
        rose_suite.set(
            keys=['template variables', 'PREANALYSIS_SCRIPT'],
            value=quote_rose_values(pa_scripts.rstrip())
        )
    else:
        rose_suite.set(keys=['template variables', 'DO_PREANALYSIS'], value='False')

    # Configure general analysis flags
    if not analysis:
        rose_suite.set(keys=['template variables', 'DO_ANALYSIS'], value='False')
        return

    do_analysis_switch = []
    for an_key, an_value in analysis.items():
        an_workflow_info = an_value.get("workflow", {})
        if "analysis_on" in an_workflow_info:
            do_analysis_switch.append(an_workflow_info["analysis_on"])
        else:
            do_analysis_switch.append("True")

    if any(do_analysis_switch):
        rose_suite.set(keys=['template variables', 'DO_ANALYSIS'], value='True')
    else:
        rose_suite.set(keys=['template variables', 'DO_ANALYSIS'], value='False')


def yaml_info(yamlfile: str = None, experiment: str = None, platform: str = None, target: str = None) -> None:
    """
    Consolidate experiment YAML files, validate the result, and create `rose-suite.conf`.

    Outputs generated workflow configurations directly into:
    `~/cylc-src/<experiment>__<platform>__<target>/`

    :param yamlfile: Path to input experiment YAML configuration file.
    :type yamlfile: str, optional
    :param experiment: Experiment name (e.g., ``'c96L65_am5f4b4r0_amip'``).
    :type experiment: str, optional
    :param platform: Target platform identifier (e.g., ``'gfdl.ncrc5-deploy'``).
    :type platform: str, optional
    :param target: Target compilation options string (e.g., ``'prod-openmp'``).
    :type target: str, optional

    :raises ValueError: If any required argument (`yamlfile`, `experiment`, `platform`, `target`) is None.
    :return: None
    :rtype: None

    .. note::
       This function writes `rose-suite.conf` and a consolidated `<experiment>.yaml` file into
       `~/cylc-src/<workflow_name>/`.
    """
    fre_logger.info('Starting configure_script_yaml execution...')

    if None in [yamlfile, experiment, platform, target]:
        raise ValueError(
            'yamlfile, experiment, platform, and target must all not be None. '
            f'Received: yamlfile={yamlfile}, experiment={experiment}, '
            f'platform={platform}, target={target}'
        )

    e, p, t, yml = experiment, platform, target, yamlfile

    # Initialize Rose configuration
    rose_suite = rose_init(e, p, t)

    # Combine input YAMLs and save consolidated output to cylc-src
    cylc_dir = os.path.join(os.path.expanduser("~/cylc-src"), f"{e}__{p}__{t}")
    outfile = os.path.join(cylc_dir, f"{e}.yaml")

    full_yamldict = cy.consolidate_yamls(
        yamlfile=yml,
        experiment=e,
        platform=p,
        target=t,
        use="pp",
        output=outfile
    )

    # Validate combined YAML dictionary against schema
    validate_yaml(full_yamldict)

    # Parse combined dictionary into Rose configuration
    set_rose_suite(full_yamldict, rose_suite)

    # Write output configuration files
    fre_logger.info("Writing output files to %s...", cylc_dir)
    fre_logger.info("  Combined YAML: %s", outfile)

    dumper = metomi.rose.config.ConfigDumper()
    rose_outfile = os.path.join(cylc_dir, "rose-suite.conf")
    dumper(rose_suite, rose_outfile)
    fre_logger.info("  Rose Suite Conf: %s", rose_outfile)

    fre_logger.info('Finished configure_script_yaml execution.')