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
def get_combined_compileyaml(comb,output=None):
    """
    Combine the model, compile, and platform yamls
    Arguments:
    comb : combined yaml object
    """
    try:
        yaml_content, loaded_yaml = comb.combine_model()
    except:
        raise ValueError("uh oh: comb.combine_model failed")

    # Merge compile into combined file to create updated yaml_content/yaml
    try:
        yaml_content, loaded_yaml = comb.combine_compile(yaml_content, loaded_yaml)
    except: 
        raise ValueError("uh oh: comb.combine_compile failed")

    # Merge platforms.yaml into combined file
    try:
        yaml_content, loaded_yaml = comb.combine_platforms(yaml_content, loaded_yaml)
    except: 
        raise ValueError("uh oh: comb.combine_platforms failed")

    # Clean the yaml
    cleaned_yaml = comb.clean_yaml(yaml_content)

    # OUTPUT IF NEEDED
    if output is not None:
        output_yaml(cleaned_yaml,experiment=None,output=output)
    else:
        fre_logger.info("Combined yaml information saved as dictionary")

    return cleaned_yaml

def get_combined_ppyaml(comb,experiment,output=None):
    """
    Combine the model, experiment, and analysis yamls
    Arguments:
    comb : combined yaml object
    """
    try:
        # Merge model into combined file
        yaml_content, loaded_yaml = comb.combine_model()
    except:
        raise ValueError("pp uh oh 1")

    try:
        # Merge pp experiment yamls into combined file
        comb_pp_updated_list = comb.combine_experiment(yaml_content, loaded_yaml)
    except:
        raise ValueError("pp uh oh 2")

    try:
        # Merge analysis yamls, if defined, into combined file
        comb_analysis_updated_list = comb.combine_analysis(yaml_content, loaded_yaml)
    except:
        raise ValueError("uh oh 3")

    try:
        # Merge model/pp and model/analysis yamls if more than 1 is defined
        # (without overwriting the yaml)
        full_combined = comb.merge_multiple_yamls(comb_pp_updated_list, comb_analysis_updated_list,loaded_yaml)
    except: 
        raise ValueError("uh oh 4")

    # Clean the yaml
    cleaned_yaml = comb.clean_yaml(full_combined)

    # OUTPUT IF NEEDED
    if output is not None:
        output_yaml(cleaned_yaml,experiment,output)
    else:
        fre_logger.info("Combined yaml information saved as dictionary")

    return cleaned_yaml

def get_combined_cmoryaml(CmorYaml,experiment,output=None):
    '''
    combine model and cmor yaml
    '''

    pp = pprint.PrettyPrinter(indent=2)

    try:
        # Merge model into combined file
        fre_logger.info('calling CmorYaml.combine_model() for yaml_content and loaded_yaml')
        yaml_content, loaded_yaml = CmorYaml.combine_model()
    except:
        raise ValueError("CmorYaml.combine_model failed")









    try:
        # Merge cmor experiment yamls into combined file
        comb_cmor_updated_list = CmorYaml.combine_experiment( yaml_content,
                                                              loaded_yaml   )
    except:
        raise ValueError("CmorYaml.combine_experiment failed")


    #pp.pprint(comb_cmor_updated_list)
    #assert False
    
    # Clean the yaml
    cleaned_yaml = CmorYaml.clean_yaml(comb_cmor_updated_list)


#    try:
#        # Merge model/cmor yamls if more than 1 is defined ???
#        # (without overwriting the yaml)
#        full_cmor_yaml = CmorYaml.merge_multiple_yamls( comb_cmor_updated_list,
#                                                        comb_analysis_updated_list,
#                                                        loaded_yaml                 )
#    except: 
#        raise ValueError("CmorYaml.merge_multiple_yamls failed")

    # Clean the yaml
    #cleaned_yaml = CmorYaml.clean_yaml(full_cmor_yaml)

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
        combined = cip.InitCompileYaml(yamlfile, platform, target, join_constructor)

        if not output:
            yml_dict = get_combined_compileyaml(combined)
        else:
            yml_dict = get_combined_compileyaml(combined,output)
            fre_logger.info(f"Combined yaml file located here: {os.getcwd()}/{output}")

    elif use == "pp":
        combined = ppip.InitPPYaml(yamlfile, experiment, platform, target, join_constructor)

        if not output:
            yml_dict = get_combined_ppyaml(combined)
        else:
            yml_dict = get_combined_ppyaml(combined,experiment,output)
            fre_logger.info(f"Combined yaml file located here: {os.getcwd()}/{output}")

    elif use == "cmor":
        
        CmorYaml = cmorip.InitCMORYaml(yamlfile, experiment, platform, target, join_constructor)
        fre_logger.info(f'DONE initializing CmorYaml = \n{CmorYaml}\n')


        if not output:
            yml_dict = get_combined_cmoryaml(CmorYaml)
        else:
            fre_logger.info(f'will be writing out the combined yaml dictionary!')
            yml_dict = get_combined_cmoryaml(CmorYaml,experiment,output)

            
        pprint(yaml_dict)
        assert False

    else:
        raise ValueError("'use' value is not valid; must be 'compile' or 'pp'") 

    return yml_dict

# Use parseyaml function to parse created edits.yaml
if __name__ == '__main__':
    consolidate_yamls()
