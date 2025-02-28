""" 
this module is for 'fre cmor yaml' calls, driving and steering the cmor_run_subtool via a model-yaml file holding
configuration information on e.g. target experiments
"""

import logging
fre_logger = logging.getLogger(__name__)

from .cmor_mixer import cmor_run_subtool

from fre.yamltools.combine_yamls_script import consolidate_yamls

def cmor_yaml_subtool(yamlfile = None,
                      exp_name = None, platform = None, target = None,
                      output = None, run_one_mode = False):
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
        run_one_mode (optional): boolean, when True, will only process one of targeted files, then exit.
    '''

    # ---------------------------------------------------
    # parsing the target model yaml ---------------------
    # ---------------------------------------------------
    fre_logger.info(f'calling consolidate yamls to create a combined cmor-yaml dictionary')
    cmor_yaml_dict = consolidate_yamls(yamlfile = yamlfile,
                                       experiment = exp_name, platform = platform, target = target,
                                       use = "cmor", output = output)
    import pprint
    pprint.PrettyPrinter(indent=1).pprint(cmor_yaml_dict)

    raise NotImplementedError('under construction')

    # ---------------------------------------------------
    # inbetween-logic to form args ----------------------
    # ---------------------------------------------------
    # give reading a shot
    indir = None
    json_var_list = None
    json_table_config = None
    json_exp_config = None
    outdir = None

    try:
        fre_logger.info('reading key/values from yamlfile...')
        indir = cmor_yaml_dict['indir']
        json_var_list = cmor_yaml_dict['json_var_list']
        json_table_config = cmor_yaml_dict['json_table_config']
        json_exp_config = cmor_yaml_dict['json_exp_config']
        outdir = cmor_yaml_dict['outdir']
    except:
        raise ValueError(f'(cmor_yaml_subtool) {yamlfile} does not have all the required information.\n'
                         f'(cmor_yaml_subtool) cmor_yaml_dict=\n{cmor_yaml_dict}'      )

    # its ok if this one doesn't work out, not reqd anyway
    opt_var_name = None

    try:
        opt_var_name = cmor_yaml_dict['opt_var_name']
    except:
        fre_logger.warning('could not read opt_var_name key/value. moving on.')

    # ---------------------------------------------------
    # showtime ------------------------------------------
    # ---------------------------------------------------
    cmor_run_subtool(
        indir = indir,
        json_var_list = json_var_list,
        json_table_config = json_table_config,
        json_exp_config = json_exp_config ,
        outdir = outdir,
        run_one_mode = run_one_mode,
        opt_var_name = opt_var_name
    )

    return
