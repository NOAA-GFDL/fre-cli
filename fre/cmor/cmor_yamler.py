"""
this module is for 'fre cmor yaml' calls, driving and steering the cmor_run_subtool via a model-yaml file holding
configuration information on e.g. target experiments
"""

from pathlib import Path
import logging
import json
from fre.yamltools.combine_yamls_script import consolidate_yamls
from .cmor_mixer import cmor_run_subtool
import os

fre_logger = logging.getLogger(__name__)

def check_path_existence(some_path):
    ''' 
    simple function checking for pathlib.Path existence, raising a FileNotFoundError if needed 
    '''
    if not Path(some_path).exists():
        raise FileNotFoundError('does not exist:  {}'.format(some_path)) # uncovered

def iso_to_bronx_chunk(cmor_chunk_in):
    '''
    converts a string representing a datetime chunk in ISO's convention (e.g. 'P5Y'), 
    to a string representing the same thing in FRE-bronx's convention
    '''
    fre_logger.debug('cmor_chunk_in = %s', cmor_chunk_in)
    if cmor_chunk_in[0] == 'P' and cmor_chunk_in[-1] == 'Y':
        bronx_chunk = cmor_chunk_in[1:-1] + 'yr'
    else:
        raise Exception('problem with converting to bronx chunk from the cmor chunk. check cmor_yamler.py') #uncovered
    fre_logger.debug('bronx_chunk = %s', bronx_chunk)
    return bronx_chunk

def conv_cmor_to_bronx_freq(cmor_table_freq):
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
        raise KeyError('frequency = {} does not exist in the targeted cmor table'.format(cmor_table_freq)) #uncovered
    return bronx_freq

def get_freq_from_table(json_table_config):
    ''' 
    checks one of the variable fields within a cmip cmor table for the frequency of the data the table describes
    takes in a path to a json cmip cmor table file, and output a string corresponding to a FREbronx style frequency 
    '''
    table_freq = None
    with open(json_table_config, 'r', encoding='utf-8') as table_config_file:
        table_config_data = json.load(table_config_file)
        for var_entry in table_config_data['variable_entry']:
            try:
                table_freq = table_config_data['variable_entry'][var_entry]['frequency']
                break
            except KeyError: #uncovered
                raise KeyError('could not get freq from table!!! variable entries in cmip cmor tables'
                               'ALWAYS have frequency info under the variable entry!! EXIT! BAD!')
    bronx_freq = conv_cmor_to_bronx_freq(table_freq)
    return bronx_freq

def cmor_yaml_subtool(yamlfile=None, exp_name=None, platform=None, target=None, output=None, opt_var_name=None,
                      run_one_mode=False, dry_run_mode=False):
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
        run_one_mode (optional): boolean, when True, will only process one of targeted files, then exit.
    '''

    # ---------------------------------------------------
    # parsing the target model yaml ---------------------
    # ---------------------------------------------------
    fre_logger.info('calling consolidate yamls to create a combined cmor-yaml dictionary')
    cmor_yaml_dict = consolidate_yamls(yamlfile=yamlfile,
                                       experiment=exp_name, platform=platform, target=target,
                                       use="cmor", output=output)['cmor']

    # ---------------------------------------------------
    # inbetween-logic to form args ----------------------
    # ---------------------------------------------------

    pp_dir = os.path.expandvars(
        cmor_yaml_dict['directories']['pp_dir'] )
    fre_logger.info('pp_dir = %s', pp_dir)
    check_path_existence(pp_dir)

    cmip_cmor_table_dir = cmor_yaml_dict['directories']['table_dir']
    fre_logger.info('cmip_cmor_table_dir = %s', cmip_cmor_table_dir)
    check_path_existence(cmip_cmor_table_dir)

    cmorized_outdir = cmor_yaml_dict['directories']['outdir']
    fre_logger.info('cmorized_outdir = %s', cmorized_outdir)
    if not Path(cmorized_outdir).exists():
        try:
            fre_logger.info('cmorized_outdir does not exist.')
            fre_logger.info('attempt to create it...')
            Path(cmorized_outdir).mkdir(exist_ok=False, parents=True)
        except Exception as exc: #uncovered
            raise OSError(
                'could not create cmorized_outdir = {} for some reason!'.format(cmorized_outdir)) from exc

    json_exp_config = os.path.expandvars(
        cmor_yaml_dict['exp_json'] )
    fre_logger.info('json_exp_config = %s', json_exp_config)
    check_path_existence(json_exp_config)

    mip_era = cmor_yaml_dict['mip_era']
    fre_logger.info('mip_era = %s', mip_era)

    # ---------------------------------------------------
    # showtime ------------------------------------------
    # ---------------------------------------------------

    for table_config in cmor_yaml_dict['table_targets']:
        table_name = table_config['table_name']
        fre_logger.info('table_name = %s', table_name)
        
        json_table_config = f'{cmip_cmor_table_dir}/{mip_era}_{table_name}.json'
        fre_logger.info('json_table_config = %s', json_table_config)
        check_path_existence(json_table_config)

        freq = table_config['freq']
        if freq is None:
            freq = get_freq_from_table(json_table_config)
        fre_logger.info('freq = %s', freq)

        json_var_list = table_config['variable_list']
        fre_logger.info('json_var_list = %s', json_var_list)

        table_components_list = table_config['target_components']
        for targ_comp_config in table_components_list:            
            component = targ_comp_config['component_name']

            bronx_chunk = iso_to_bronx_chunk(targ_comp_config['chunk'])
            data_series_type = targ_comp_config['data_series_type']
            
            indir = f'{pp_dir}/{component}/{data_series_type}/{freq}/{bronx_chunk}'
            fre_logger.info('indir = %s', indir)

            fre_logger.info('PROCESSING: ( %s, %s )', table_name, component)
            if not dry_run_mode:
                cmor_run_subtool( #uncovered
                    indir = indir ,
                    json_var_list = json_var_list ,
                    json_table_config = json_table_config ,
                    json_exp_config = json_exp_config ,
                    outdir = cmorized_outdir ,
                    run_one_mode = True ,
                    opt_var_name = None
                )
            else:
                fre_logger.debug('--DRY RUN CALL---\n'
                                 'cmor_run_subtool(\n'
                                 f'    indir = {indir} ,\n'
                                 f'    json_var_list = {json_var_list} ,\n'
                                 f'    json_table_config = {json_table_config} ,\n'
                                 f'    json_exp_config = {json_exp_config} ,\n'
                                 f'    outdir = {cmorized_outdir} ,\n'
                                 '    run_one_mode = True ,\n'
                                 '    opt_var_name = None\n'
                                 ')\n'
                                 )

    return
