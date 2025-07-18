import os
import logging
fre_logger = logging.getLogger(__name__)
from pathlib import Path
#import pprint

# this boots yaml with !join- see __init__
import os
import logging
fre_logger = logging.getLogger(__name__)
from pathlib import Path
import pprint
from .helpers import experiment_check, clean_yaml
import yaml

class InitAnalysisYaml():
    """ ---- """
    def __init__(self,yamlfile,experiment,platform,target):
        """
        Process to combine the applicable yamls for post-processing
        """
        self.yml = yamlfile
        self.name = experiment
        self.platform = platform
        self.target = target

        # Path to the main model yaml
        mainyaml_dir = os.path.abspath(self.yml)
        self.mainyaml_dir = os.path.dirname(mainyaml_dir)

        # Create combined pp yaml
        former_log_level = fre_logger.level
        fre_logger.setLevel(logging.INFO)
        fre_logger.info("Combining yaml files into one dictionary: ")


    def combine_model(self):
        """
        Create the combined.yaml and merge it with the model yaml
        """
        # Define click options in string
        yaml_content_str = (f'name: &name "{self.name}"\n'
                        f'platform: &platform "{self.platform}"\n'
                        f'target: &target "{self.target}"\n')

        # Read model yaml as string
        with open(self.yml,'r') as f:
            model_content = f.read()

        # Combine information as strings
        yaml_content_str += model_content

        # Return the combined string and loaded yaml
        former_log_level = fre_logger.level
        fre_logger.setLevel(logging.INFO)
        fre_logger.info(f"   model yaml: {self.yml}")
        fre_logger.setLevel(former_log_level)

        return yaml_content_str

    def get_settings_yaml(self, yaml_content_str):
        """
        :param yaml_content_str: 
        :type yaml_content_str: str
        """
        my = yaml.load(yaml_content_str, Loader=yaml.Loader)
#        print(yml.get("experiments"))

        for i in my.get("experiments"):
            if self.name != i.get("name"):
                continue
            settings = i.get("settings")

#        print(f"{self.mainyaml_dir}/{settings}")
        with open(f"{self.mainyaml_dir}/{settings}", 'r') as f:
            settings_content = f.read()

        yaml_content_str += settings_content
        return yaml_content_str
 
    def combine_yamls(self,yaml_content_str):
        """
        Combine analysis yamls with the defined combined.yaml
        If more than 1 analysis yaml defined, return a list of paths.
        """
        # Load string as yaml
        yml=yaml.load(yaml_content_str,Loader=yaml.Loader)
        (ey_path,ay_path) = experiment_check(self.mainyaml_dir,self.name,yml)

        analysis_yamls = []
        analysis_yamls.append(yaml_content_str)

        ## COMBINE EXPERIMENT YAML INFO
        # If no analysis yaml defined, move on silently. 
        if ay_path is None:
            pass

        # If only 1 analysis yaml defined, combine with model yaml
        elif len(ay_path) == 1:
            with open(ay_path[0],'r') as ayp:
                analysis_content = ayp.read()

            analysis_info = yaml_content_str + analysis_content
            analysis_yamls.append(analysis_info)

        # If more than 1 pp yaml listed
        # (Must be done for aliases defined)
        elif len(ay_path) > 1:
            for i in ay_path:
                with open(i,'r') as ayp:
                    analysis_content = ayp.read()

                analysis_info_i = yaml_content_str + analysis_content
                analysis_yamls.append(analysis_info_i)

###        print(analysis_yamls)
###        ah2
        return analysis_yamls

    def merge_multiple_yamls(self, analysis_list, yaml_content_str):
        """
        Merge separately combined post-processing and analysis
        yamls into fully combined yaml (without overwriting like sections).
        """
        # Load string as yaml
        yml=yaml.load(yaml_content_str,Loader=yaml.Loader)
        (ey_path,ay_path) = experiment_check(self.mainyaml_dir,self.name,yml)

        result = {}
        # If more than one analysis yaml is listed, update dictionary with content from 1st yaml
        # Looping through rest of yamls listed, compare key value pairs.
        # If instance of key is a dictionary in both result and loaded yamlfile, update the key
        # in result to include the loaded yaml file's value.
        if analysis_list is not None and len(analysis_list) > 1:
###            yml_analysis = "".join(analysis_list[0])
###            result.update(yaml.load(yml_analysis,Loader=yaml.Loader))

#            print(analysis_list[0])
#            quit()
            result.update(yaml.load(analysis_list[1],Loader=yaml.Loader))

###            print(analysis_list)
###            pprint.pprint(result)
###            quit()

            for i in analysis_list[2:]:
#               analysis_list_to_string_concat = "".join(i)
###                print(i)
###                quit()
                yf = yaml.load(i,Loader=yaml.Loader)
                for key in result:
                    #print(key)
                    #quit()

                    if key not in yf:
                        continue
                    if isinstance(result[key],dict) and isinstance(yf[key],dict):
                        result['analysis'] = yf['analysis'] | result['analysis']
#                        result['analysis'] += yf['analysis']

#        # If only one analysis yaml listed
#        elif analysis_list is not None and len(analysis_list) == 1:
##            yml_analysis = "".join(analysis_list[0])
#            result.update(yaml.load(analysis_list[0],Loader=yaml.Loader))

        if ay_path is not None:
            former_log_level = fre_logger.level
            fre_logger.setLevel(logging.INFO)
            for i in ay_path:
                analysis = str(i).rsplit('/', maxsplit=1)[-1]
                fre_logger.info(f"   analysis yaml: {analysis}")
            fre_logger.setLevel(former_log_level)

        return result
