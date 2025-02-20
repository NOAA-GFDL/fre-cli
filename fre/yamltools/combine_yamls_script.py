import os
import shutil

import logging
fre_logger = logging.getLogger(__name__)


from pathlib import Path
import click
import yaml
import fre.yamltools.compile_info_parser as cip
import fre.yamltools.pp_info_parser as ppip
import fre.yamltools.cmor_info_parser as cmorip
import pprint

def join_constructor(loader, node):
    """
    Allows FRE properties defined
    in main yaml to be concatenated.
    """
    seq = loader.construct_sequence(node)
    return ''.join([str(i) for i in seq])




def output_yaml(cleaned_yaml,experiment,output):
    """
    Write out the combined yaml dictionary info
    to a file if --output is specified
    """
    filename = output
    with open(filename,'w') as out:
        out.write(yaml.dump(cleaned_yaml,default_flow_style=False,sort_keys=False))



        
## Functions to combine the yaml files ##
def get_combined_compileyaml(CompileYaml,output=None):
    """
    Combine the model, compile, and platform yamls
    Arguments:
    CompileYaml : combined yaml object
    """
    try:
        yaml_content, loaded_yaml = CompileYaml.combine_model()
    except:
        raise ValueError("ERR: Could not merge model information.")

    # Merge compile into combined file to create updated yaml_content/yaml
    try:
        yaml_content, loaded_yaml = CompileYaml.combine_compile(yaml_content, loaded_yaml)
    except: 
        raise ValueError("ERR: Could not merge compile yaml information.")

    # Merge platforms.yaml into combined file
    try:
        yaml_content, loaded_yaml = CompileYaml.combine_platforms(yaml_content, loaded_yaml)
    except: 
        raise ValueError("ERR: Could not merge platform yaml information.")

    # Clean the yaml
    cleaned_yaml = CompileYaml.clean_yaml(yaml_content)

    # OUTPUT IF NEEDED
    if output is not None:
        output_yaml(cleaned_yaml,experiment=None,output=output)
    else:
        fre_logger.info("Combined yaml information saved as dictionary")

    return cleaned_yaml




def get_combined_ppyaml(PPYaml, experiment, output = None):
    """
    Combine the model, experiment, and analysis yamls
    Arguments:
    PPYaml : combined yaml object
    """
    # Merge model into combined file
    try:
        yaml_content, loaded_yaml = PPYaml.combine_model()
    except:
        raise ValueError("ERR: Could not merge model information.")

    # Merge pp experiment yamls into combined file
    try:
        comb_pp_updated_list = PPYaml.combine_experiment(yaml_content, loaded_yaml)
    except:
        raise ValueError("ERR: Could not merge pp experiment yaml information")

    # Merge analysis yamls, if defined, into combined file
    try:
        comb_analysis_updated_list = PPYaml.combine_analysis(yaml_content, loaded_yaml)
    except:
        raise ValueError("ERR: Could not merge analysis yaml information")

    # Merge model/pp and model/analysis yamls if more than 1 is defined
    # (without overwriting the yaml)
    try:
        full_combined = PPYaml.merge_multiple_yamls(comb_pp_updated_list, comb_analysis_updated_list,loaded_yaml)
    except: 
        raise ValueError("ERR: Could not merge multiple pp and analysis information together.")

    # Clean the yaml
    cleaned_yaml = PPYaml.clean_yaml(full_combined)

    # OUTPUT IF NEEDED
    if output is not None:
        output_yaml(cleaned_yaml,experiment,output)
    else:
        fre_logger.info("Combined yaml information saved as dictionary")

    return cleaned_yaml




def get_combined_cmoryaml(CmorYaml, experiment, output = None):
    '''
    combine model and cmor yaml
    '''

    # temp DELETEME
    pp = pprint.PrettyPrinter( indent = 2 )

    # Merge model into combined file
    try:
        fre_logger.info('calling CmorYaml.combine_model() for yaml_content and loaded_yaml')
        yaml_content, loaded_yaml = CmorYaml.combine_model()
    except:
        raise ValueError("CmorYaml.combine_model failed")

    # Merge cmor experiment yamls into combined file
    try:
        comb_cmor_updated_list = CmorYaml.combine_experiment( yaml_content,
                                                              loaded_yaml   )
    except:
        raise ValueError("CmorYaml.combine_experiment failed")


    # Merge model/cmor yamls if more than 1 is defined ???
    # (without overwriting the yaml)
    try:
        full_cmor_yaml = CmorYaml.merge_cmor_yaml( comb_cmor_updated_list,
                                                        loaded_yaml                 )
    except: 
        raise ValueError("CmorYaml.merge_cmor_yaml failed")

    
    # Clean the yaml
    cleaned_yaml = CmorYaml.clean_yaml(full_cmor_yaml)
    pp.pprint(cleaned_yaml)

    # OUTPUT IF NEEDED
    if output is not None:
        output_yaml(cleaned_yaml,experiment,output)
    else:
        fre_logger.info("Combined yaml information saved as dictionary")

    return cleaned_yaml


def consolidate_yamls(yamlfile,
                      experiment, platform, target,
                      use, output):
    """
    Depending on `use` argument passed, either create the final
    combined yaml for compilation or post-processing
    """
    fre_logger.info(f'combining+parsing yaml files, for {use} usage')

    if use == "compile":
        CompileYaml = cip.InitCompileYaml(yamlfile,
                                          platform, target,
                                          join_constructor)
        if output is None:
            yml_dict = get_combined_compileyaml(CompileYaml)
        else:
            yml_dict = get_combined_compileyaml(CompileYaml,output)
            fre_logger.info(f"Combined CompileYaml file located here: {os.getcwd()}/{output}")

    elif use == "pp":
        PPYaml = ppip.InitPPYaml(yamlfile,
                                 experiment, platform, target,
                                 join_constructor)

        if output is None:
            yml_dict = get_combined_ppyaml( PPYaml, experiment)
        else:
            yml_dict = get_combined_ppyaml( PPYaml, experiment, output )
            fre_logger.info( f"Combined PPYaml file located here: {os.getcwd()}/{output}" )

    elif use == "cmor":
        fre_logger.info(f'about to initialize the CmorYaml')
        CmorYaml = cmorip.InitCMORYaml(yamlfile,
                                       experiment, platform, target,
                                       join_constructor)
        fre_logger.info(f'\n    DONE initializing CmorYaml = \n    {CmorYaml}\n')


        if output is None:
            yml_dict = get_combined_cmoryaml(CmorYaml)
        else:
            fre_logger.info(f'will be writing out the combined yaml dictionary!')
            yml_dict = get_combined_cmoryaml(CmorYaml,experiment,output)

            
        #pprint(yaml_dict)
        #assert False

    else:
        raise ValueError("'use' value is not valid; must be 'compile' or 'pp'") 

    return yml_dict

