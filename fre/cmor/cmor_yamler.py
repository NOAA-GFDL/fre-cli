"""
this module is for 'fre cmor yaml' calls, driving and steering the cmor_run_subtool via a model-yaml file holding
configuration information on e.g. target experiments
"""
from pathlib import Path
#import os
#import shutil

import logging
fre_logger = logging.getLogger(__name__)

from fre.yamltools.combine_yamls_script import consolidate_yamls

from .cmor_mixer import cmor_run_subtool


def check_path_existence(some_path):
    ''' simple function checking for pathlib.Path existence 
    raising a FileNotFoundError if needed '''
    if not Path(some_path).exists():
        raise FileNotFoundError(f'does not exist:  {some_path}')



def cmor_yaml_subtool(yamlfile = None,
                      exp_name = None, platform = None, target = None,
                      output = None, opt_var_name = None, run_one_mode = False):
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
    fre_logger.info(f'calling consolidate yamls to create a combined cmor-yaml dictionary')
    cmor_yaml_dict = consolidate_yamls(yamlfile = yamlfile,
                                       experiment = exp_name, platform = platform, target = target,
                                       use = "cmor", output = output)['cmor']
    import pprint
    pprint.PrettyPrinter(indent=1).pprint(cmor_yaml_dict)


    # ---------------------------------------------------
    # inbetween-logic to form args ----------------------
    # ---------------------------------------------------


    # stuff needed for run tool arg: input directory location of files...
    # component=mustbeassignedinloop
    data_series_type = cmor_yaml_dict['data_series_type']
    fre_logger.info(f'data_series_type = {data_series_type}')

    freq = cmor_yaml_dict['freq']
    fre_logger.info(f'freq = {freq}')

    chunk = cmor_yaml_dict['chunk']
    fre_logger.info(f'chunk = {chunk}')

    pp_dir = cmor_yaml_dict['directories']['pp_dir']
    fre_logger.info(f'pp_dir = {pp_dir}')


    # stuff needed for run tool arg: target variable list...
    json_var_list=cmor_yaml_dict['variable_list']
    fre_logger.info(f'json_var_list = {json_var_list}')
    check_path_existence(json_var_list)

    # stuff needed for run tool arg: mip table...
    # table=mustbeassignedinloop
    mip_spec = cmor_yaml_dict['mip_spec']#'CMIP6'
    fre_logger.info(f'mip_spec = {mip_spec}')

    path_to_cmip_cmor_tables=cmor_yaml_dict['directories']['table_dir']
    fre_logger.info(f'path_to_cmip_cmor_tables = {path_to_cmip_cmor_tables}')
    check_path_existence(path_to_cmip_cmor_tables)

    # stuff needed for run tool arg: experiment-specific metadata... easy
    # argument to run tool: experiment-specific metadata (exp config)
    json_exp_config = cmor_yaml_dict['exp_json']#f'{exp_json}
    fre_logger.info(f'json_exp_config = {json_exp_config}')
    check_path_existence(json_exp_config)


    # OPTIONAL: output directory, **as specified in the yaml**
    yaml_outdir = None
    try:
        yaml_outdir = cmor_yaml_dict['outdir']
        fre_logger.info(f'yaml_outdir = {yaml_outdir}')
    except:
        fre_logger.warning(f'warning, couldnt read \'outdir\' key in cmor yaml dict, or has no/null value')
        fre_logger.warning(f'warning, guessing that you want your output near your input file directory as default')


    # try to determine archroot directory as needed. if not, no biggie. 
    archroot = None
    try:
        archroot='/'.join(pp_dir.split('/')[0:-1])
        fre_logger.info(f'from pp_dir, archroot must be: {archroot}')
    except:
        fre_logger.warning(f'could not figure out archroot')

    # output directory specification is based on what's in the yaml, and if we could determine archroot
    outdir = None
    try:
        outdir = f'{archroot}/publish' if yaml_outdir is None else yaml_outdir

    if outdir is None:
        raise OSError('problem with figuring out what output directory should be')

    if not Path(outdir).exists():
        fre_logger.info(f'this doesnt exist: outdir= \n    {outdir}')
        fre_logger.info('creating....')
        Path(outdir).mkdir(exist_ok=True, parents=False)


    # its ok if this one doesn't work out
    opt_var_name = None
    try:
        opt_var_name = cmor_yaml_dict['opt_var_name']
    except:
        fre_logger.warning('could not read opt_var_name key/value. moving on.')

    # ---------------------------------------------------
    # showtime ------------------------------------------
    # ---------------------------------------------------

    # --- loop over mip table / component combos
    for table_config in cmor_yaml_dict['table_targets']:
        table=table_config['table_name']
        table_components_list=table_config['target_components']
        for component in table_components_list:

            # --- now form the arguments to the run subtool:

            # argument to run tool: input directory location of files
            indir = f'{pp_dir}/{component}/{data_series_type}/{freq}/{chunk}'
            fre_logger.info(f'indir = {indir}')

            ### configuration files ###
            json_table_config = f'{path_to_cmip_cmor_tables}/{mip_spec}_{table}.json'
            fre_logger.info(f'json_table_config = {json_table_config}')

            fre_logger.info(f'PROCESSING: table, component = {table}, {component}')



            #
            #    # fire!
            #    cmor_run_subtool(
            #        indir = indir ,
            #        json_var_list = json_var_list ,
            #        json_table_config = json_table_config ,
            #        json_exp_config = json_exp_config ,
            #        outdir = outdir ,
            #        run_one_mode = True, #run_one_mode,
            #        opt_var_name = None #opt_var_name
            #    )

    raise NotImplementedError('under construction')

    return






### scratch-work, or old lines i wanna keep for now
