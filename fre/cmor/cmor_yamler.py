"""
YAML-Driven CMORization Workflow Tools
======================================

This module powers the ``fre cmor yaml`` command, steering the CMORization workflow by parsing model-YAML
files that describe target experiments and their configurations. It combines model-level and experiment-level
configuration, parses required metadata and paths, and orchestrates calls to ``cmor_run_subtool`` for each
target variable/component.

Functions
---------
- ``check_path_existence(some_path)``
- ``iso_to_bronx_chunk(cmor_chunk_in)``
- ``conv_mip_to_bronx_freq(cmor_table_freq)``
- ``get_bronx_freq_from_mip_table(json_table_config)``
- ``cmor_yaml_subtool(...)``
"""

import json
from pathlib import Path
import pprint
import logging
import os
from typing import Optional, List, Dict, Any, Union

from fre.yamltools.combine_yamls_script import consolidate_yamls
from .cmor_mixer import cmor_run_subtool

fre_logger = logging.getLogger(__name__)

def check_path_existence(some_path: str):
    """
    Check if the given path exists, raising FileNotFoundError if not.

    Parameters
    ----------
    some_path : str
        A string representing a filesystem path (relative or absolute).

    Raises
    ------
    FileNotFoundError
        If the path does not exist.
    """
    if not Path(some_path).exists():
        raise FileNotFoundError(f'does not exist:  {some_path}')

def iso_to_bronx_chunk(cmor_chunk_in: str) -> str:
    """
    Convert an ISO8601 duration string (e.g., 'P5Y') to FRE-bronx-style chunk string (e.g., '5yr').

    Parameters
    ----------
    cmor_chunk_in : str
        ISO8601 formatted string representing a time interval (must start with 'P' and end with 'Y').

    Returns
    -------
    str
        FRE-bronx chunk string.

    Raises
    ------
    ValueError
        If the input does not follow the expected ISO format.
    """
    fre_logger.debug('cmor_chunk_in = %s', cmor_chunk_in)
    if cmor_chunk_in[0] == 'P' and cmor_chunk_in[-1] == 'Y':
        bronx_chunk = f'{cmor_chunk_in[1:-1]}yr'
    else:
        raise ValueError('problem with converting to bronx chunk from the cmor chunk. check cmor_yamler.py')
    fre_logger.debug('bronx_chunk = %s', bronx_chunk)
    return bronx_chunk

def conv_mip_to_bronx_freq(cmor_table_freq: str) -> Optional[str]:
    """
    Convert a MIP table frequency string to its FRE-bronx equivalent using a lookup table.

    Parameters
    ----------
    cmor_table_freq : str
        Frequency string as found in a MIP table (e.g., 'mon', 'day', 'yr', etc.).

    Returns
    -------
    str or None
        FRE-bronx frequency string, or None if not mappable.

    Raises
    ------
    KeyError
        If the frequency string is not recognized as valid.
    """
    cmor_to_bronx_dict = {
        "1hr"    : "1hr",
        "1hrCM"  : None,
        "1hrPt"  : None,
        "3hr"    : "3hr",
        "3hrPt"  : None,
        "6hr"    : "6hr",
        "6hrPt"  : None,
        "day"    : "daily",
        "dec"    : None,
        "fx"     : None,
        "mon"    : "monthly",
        "monC"   : None,
        "monPt"  : None,
        "subhrPt": None,
        "yr"     : "annual",
        "yrPt"   : None
    }
    bronx_freq = cmor_to_bronx_dict.get(cmor_table_freq)
    if bronx_freq is None:
        fre_logger.warning(f'MIP table frequency = {cmor_table_freq} does not have a FRE-bronx equivalent')
    if cmor_table_freq not in cmor_to_bronx_dict.keys():
        raise KeyError(f'MIP table frequency = "{cmor_table_freq}" is not a valid MIP frequency')
    return bronx_freq

def get_bronx_freq_from_mip_table(json_table_config: str) -> str:
    """
    Extract the frequency of data from a CMIP MIP table (JSON), returning its FRE-bronx equivalent.

    Parameters
    ----------
    json_table_config : str
        Path to a JSON MIP table file with 'variable_entry' metadata.

    Returns
    -------
    str
        FRE-bronx frequency string.

    Raises
    ------
    KeyError
        If the frequency cannot be found or mapped.
    """
    table_freq = None
    with open(json_table_config, 'r', encoding='utf-8') as table_config_file:
        table_config_data = json.load(table_config_file)
        for var_entry in table_config_data['variable_entry']:
            try:
                table_freq = table_config_data['variable_entry'][var_entry]['frequency']
                break
            except Exception as exc:
                raise KeyError('could not get freq from table!!! variable entries in cmip cmor tables'
                               'have frequency info under the variable entry!') from exc
    bronx_freq = conv_mip_to_bronx_freq(table_freq)
    return bronx_freq

def cmor_yaml_subtool( yamlfile: Optional[Union[str, Path]] = None,
                       exp_name: Optional[str] = None,
                       platform: Optional[str] = None,
                       target: Optional[str] = None,
                       output: Optional[Union[str, Path]] = None,
                       opt_var_name: Optional[str] = None,
                       run_one_mode: bool = False,
                       dry_run_mode: bool = False,
                       start: Optional[str] = None,
                       stop: Optional[str] = None,
                       calendar_type: Optional[str] = None) -> None:
    """
    Main driver for CMORization using model YAML configuration files.

    This routine parses the model YAML, combines configuration, resolves and checks all required
    paths and metadata, and orchestrates calls to cmor_run_subtool for each table/component/variable
    defined in the configuration.

    Parameters
    ----------
    yamlfile : str or Path
        Path to a model-yaml file holding experiment and workflow configuration.
    exp_name : str
        Experiment name (must be present in the YAML file).
    platform : str
        Platform target (e.g., 'ncrc4.intel').
    target : str
        Compilation target (e.g., 'prod-openmp').
    output : str or Path, optional
        Optional path for YAML output.
    opt_var_name : str, optional
        If specified, process only files matching this variable name.
    run_one_mode : bool, optional
        If True, process only one file and exit.
    dry_run_mode : bool, optional
        If True, print configuration and actions without executing cmor_run_subtool.
    start : str, optional
        Four-digit year (YYYY) indicating start of date range to process.
    stop : str, optional
        Four-digit year (YYYY) indicating end of date range to process.
    calendar_type : str, optional
        CF-compliant calendar type.

    Returns
    -------
    None

    Raises
    ------
    FileNotFoundError
        If required paths do not exist.
    OSError
        If output directories cannot be created.
    ValueError
        If required configuration is missing or inconsistent.

    Notes
    -----
    - Reads and combines YAML and JSON configuration.
    - Performs path, frequency, and gridding checks.
    - Delegates actual CMORization to cmor_run_subtool, except in dry-run mode.
    - All actions and key decisions are logged.
    """

    # ---------------------------------------------------
    # parsing the target model yaml ---------------------
    # ---------------------------------------------------
    fre_logger.info('calling consolidate yamls to create a combined cmor-yaml dictionary')
    cmor_yaml_dict = consolidate_yamls(yamlfile=yamlfile,
                                       experiment=exp_name, platform=platform, target=target,
                                       use="cmor", output=output)['cmor']
    fre_logger.debug('consolidate_yamls produced the following dictionary of cmor-settings from yamls: \n%s',
                     pprint.pformat(cmor_yaml_dict) )


    # ---------------------------------------------------
    # between-logic to form args ----------------------
    # ---------------------------------------------------

    # target input pp directory
    pp_dir = os.path.expandvars(
        cmor_yaml_dict['directories']['pp_dir'] )
    fre_logger.info('pp_dir = %s', pp_dir)
    check_path_existence(pp_dir)

    # directory holding mip table config inputs
    cmip_cmor_table_dir = os.path.expandvars(
        cmor_yaml_dict['directories']['table_dir'] )
    fre_logger.info('cmip_cmor_table_dir = %s', cmip_cmor_table_dir)
    check_path_existence(cmip_cmor_table_dir)

    # final directory housing whole CMOR dir structure at the end of it all
    cmorized_outdir = os.path.expandvars(
        cmor_yaml_dict['directories']['outdir'] )
    fre_logger.info('cmorized_outdir = %s', cmorized_outdir)
    if not Path(cmorized_outdir).exists():
        try:
            fre_logger.info('cmorized_outdir does not exist.')
            fre_logger.info('attempt to create it...')
            Path(cmorized_outdir).mkdir(exist_ok=False, parents=True)
        except Exception as exc: #uncovered
            raise OSError(
                f'could not create cmorized_outdir = {cmorized_outdir} for some reason!') from exc

    # path to metadata header to be appended to output netcdf file
    json_exp_config = os.path.expandvars(
        cmor_yaml_dict['exp_json'] )
    fre_logger.info('json_exp_config = %s', json_exp_config)
    check_path_existence(json_exp_config)

    # e.g. CMIP6
    mip_era = cmor_yaml_dict['mip_era']
    fre_logger.info('mip_era = %s', mip_era)

    # check start/stop years range to target desired input files
    if start is None:
        try:
            yaml_start = cmor_yaml_dict['start']
            start = yaml_start
        except KeyError:
            fre_logger.warning(
                'no start year for fre.cmor given anywhere, will start with earliest datetime found in filenames!')

    if stop is None:
        try:
            yaml_stop = cmor_yaml_dict['stop']
            stop = yaml_stop
        except KeyError:
            fre_logger.warning(
                'no stop year for fre.cmor given anywhere, will end with latest datetime found in filenames!')
    if calendar_type is None:
        try:
            yaml_calendar_type = cmor_yaml_dict['calendar_type']
            calendar_type = yaml_calendar_type
        except KeyError:
            fre_logger.warning(
                'no calendar_type for fre.cmor given anywhere, will use what is in %s', json_exp_config)

    # ---------------------------------------------------
    # showtime ------------------------------------------
    # ---------------------------------------------------
    for table_config in cmor_yaml_dict['table_targets']:
        table_name = table_config['table_name']
        fre_logger.info('table_name = %s', table_name)

        json_var_list = os.path.expandvars(
            table_config['variable_list']
        )
        fre_logger.info('json_var_list = %s', json_var_list)

        json_table_config = f'{cmip_cmor_table_dir}/{mip_era}_{table_name}.json'
        fre_logger.info('json_table_config = %s', json_table_config)
        check_path_existence(json_table_config)


        # frequency of data ---- the reason this spot looks kind of awkward is because of the case where
        #                        the table if e.g. Ofx and thus the table's frequency field is smth like 'fx'
        #                        if that's the case, we only demand that the freq field is filled out in the yaml
        #                        which is really more about path resolving than anything.
        freq = table_config['freq']
        table_freq = get_bronx_freq_from_mip_table(json_table_config)
        if freq is None:
            freq = table_freq
        fre_logger.info('freq = %s', freq)
        # check frequency info
        if freq is None:
            raise ValueError(
                f'not enough frequency information to process variables for {table_config}')
        elif freq != table_freq and table_freq is not None:
            raise ValueError(
                'frequency from MIP table is incompatible with requested frequency in cmor yaml for {table_config}')
        # frequency of data ---- the reason this spot looks kind of

        # gridding info of data ---- revisit/TODO
        gridding_dict = table_config['gridding']
        fre_logger.debug('gridding_dict = %s', gridding_dict)
        grid_label, grid_desc, nom_res = None, None, None
        if gridding_dict is not None:
            grid_label = gridding_dict['grid_label']
            grid_desc = gridding_dict['grid_desc']
            nom_res = gridding_dict['nom_res']
            if None in [grid_label, grid_desc, nom_res]:
                raise ValueError('gridding dictionary, if present, must have all three fields be non-empty.')
        # gridding info of data ---- revisit

        table_components_list = table_config['target_components']
        for targ_comp_config in table_components_list:
            component = targ_comp_config['component_name']
            bronx_chunk = iso_to_bronx_chunk(targ_comp_config['chunk'])
            data_series_type = targ_comp_config['data_series_type']
            indir = f'{pp_dir}/{component}/{data_series_type}/{freq}/{bronx_chunk}'
            fre_logger.info('indir = %s', indir)

            fre_logger.info('PROCESSING: ( %s, %s )', table_name, component)

            if dry_run_mode:
                fre_logger.info(  '--DRY RUN CALL---\n'
                                  'cmor_run_subtool(\n'
                                 f'    indir = {indir} ,\n'
                                 f'    json_var_list = {json_var_list} ,\n'
                                 f'    json_table_config = {json_table_config} ,\n'
                                 f'    json_exp_config = {json_exp_config} ,\n'
                                 f'    outdir = {cmorized_outdir} ,\n'
                                 f'    run_one_mode = {run_one_mode} ,\n'
                                 f'    opt_var_name = {opt_var_name} ,\n'
                                 f'    grid = {grid_desc} ,\n'
                                 f'    grid_label = {grid_label} ,\n'
                                 f'    nom_res = {nom_res} ,\n'
                                 f'    start = {start} ,\n'
                                 f'    stop = {stop} ,\n'
                                 f'    calendar_type={calendar_type} '
                                  ')\n' )
                continue
            cmor_run_subtool( #uncovered
                indir = indir ,
                json_var_list = json_var_list ,
                json_table_config = json_table_config ,
                json_exp_config = json_exp_config ,
                outdir = cmorized_outdir ,
                run_one_mode = run_one_mode ,
                opt_var_name = opt_var_name ,
                grid = grid_desc ,
                grid_label = grid_label ,
                nom_res = nom_res ,
                start = start,
                stop = stop
            )
