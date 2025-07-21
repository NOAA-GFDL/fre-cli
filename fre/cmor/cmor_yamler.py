"""
this module is for 'fre cmor yaml' calls, driving and steering the cmor_run_subtool via a model-yaml file holding
configuration information on e.g. target experiments
"""

import json
from pathlib import Path
import pprint
import logging
import os
from fre.yamltools.combine_yamls_script import consolidate_yamls
from .cmor_mixer import cmor_run_subtool

fre_logger = logging.getLogger(__name__)

def check_path_existence(some_path):
    '''
    simple function checking for pathlib.Path existence, raising a FileNotFoundError if needed
    Args:
        some_path (str), required, a string representing a path. can be relative or absolute
    '''
    if not Path(some_path).exists():
        raise FileNotFoundError('does not exist:  {}'.format(some_path)) #uncovered heyyyyyy... codecov bot, overhere!

def iso_to_bronx_chunk(cmor_chunk_in):
    '''
    converts a string representing a datetime chunk in ISO's convention (e.g. 'P5Y'),
    to a string representing the same thing in FRE-bronx's convention
    Args:
        cmor_chunk_in (str), required, ISO 8601 formatted string representing a datetime interval
    '''
    fre_logger.debug('cmor_chunk_in = %s', cmor_chunk_in)
    if cmor_chunk_in[0] == 'P' and cmor_chunk_in[-1] == 'Y':
        bronx_chunk = f'{cmor_chunk_in[1:-1]}yr'
    else:
        raise ValueError('problem with converting to bronx chunk from the cmor chunk. check cmor_yamler.py') #uncovered heyyyyyy... codecov bot, overhere!
    fre_logger.debug('bronx_chunk = %s', bronx_chunk)
    return bronx_chunk

def conv_mip_to_bronx_freq(cmor_table_freq):
    '''
    uses a look up table to convert a given frequency in a MIP table, to that same frequency under FRE-bronx convention instead
    Args:
        cmor_table_freq (str), required, a frequency string read from a MIP table, subject to a controlled vocabulary. 
    '''
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
        fre_logger.warning(f'MIP table frequency = {cmor_table_freq} does not have a FRE-bronx equivalent') #uncovered heyyyyyy... codecov bot, overhere!
    if cmor_table_freq not in cmor_to_bronx_dict.keys():# and cmor_table_freq != 'fx':
        raise KeyError(f'MIP table frequency = "{cmor_table_freq}" is not a valid MIP frequency')
    return bronx_freq

def get_bronx_freq_from_mip_table(json_table_config):
    '''
    checks one of the variable fields within a cmip cmor table for the frequency of the data the table describes
    takes in a path to a json cmip cmor table file, and output a string corresponding to a FREbronx style frequency
    Args:
        json_table_config (str), required, a string representing a path to a json MIP table holding metadata under variable names
    '''
    table_freq = None
    with open(json_table_config, 'r', encoding='utf-8') as table_config_file:
        table_config_data = json.load(table_config_file)
        for var_entry in table_config_data['variable_entry']:
            try:
                table_freq = table_config_data['variable_entry'][var_entry]['frequency']
                break
            except Exception as exc: #uncovered heyyyyyy... codecov bot, overhere!
                raise KeyError('could not get freq from table!!! variable entries in cmip cmor tables'
                               'have frequency info under the variable entry!') from exc
    bronx_freq = conv_mip_to_bronx_freq(table_freq)
    return bronx_freq

def cmor_yaml_subtool(yamlfile=None, exp_name=None, platform=None, target=None, output=None, opt_var_name=None,
                      run_one_mode=False, dry_run_mode=False, start=None, stop=None, calendar_type=None):
    '''
    A routine that cmorizes targets based on configuration stored in the model yaml. The model yaml
    points to various cmor-yaml configurations. The two levels of information are combined, their fields
    are parsed to de-reference anchors and call fre's internal yaml constructor functions.
        yamlfile (required): string or Path to a model-yaml
        exp_name (required): string representing an experiment name. it must be present in the list of
                             experiments within the targeted yamlfile
        platform (required): string representing platform target (e.g. ncrc4.intel)
        target   (required): string representing compilation target (e.g. prod-openmp)
        output   (optional): string or Path representing target location for yamlfile output if desired
        opt_var_name (optional): string, specify a variable name to specifically process only filenames matching
                                 that variable name. I.e., this string help target local_vars, not target_vars.
        calendar_type (optional): string representing a CF compliant calendar type name. if None, use whats in json
        run_one_mode (optional): boolean, when True, will only process one of targeted files, then exit.
        start, stop: string, optional arguments, strings of four integers representing years (YYYY).
    '''

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
    # inbetween-logic to form args ----------------------
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
        except Exception as exc: #uncovered heyyyyyy... codecov bot, overhere!
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
            cmor_run_subtool( #uncovered heyyyyyy... codecov bot, overhere!
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


