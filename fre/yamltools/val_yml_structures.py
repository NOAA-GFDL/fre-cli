import os
import logging
fre_logger = logging.getLogger(__name__)
from pathlib import Path
#import pprint
import yaml
from abc import ABC, abstractmethod
from fre.yamltools.abstract_classes import ValidateYamls

###HINT FROM IAN
#import yaml
#am5_mod_yaml_stream=open('fre/yamltools/tests/AM5_example/am5.yaml','r')
#iter_am5_mod_yaml_stream = yaml.scan(am5_mod_yaml_stream).__iter__()
#
#for thing in iter_am5_mod_yaml_stream:
#    if str(thing)[-2:] != "()":
#        print(thing)
###
class ModelYmlStructure(ValidateYamls):
    def __init__(self, yamlfile):
        self.yml = yamlfile

    def validate_keys(self):
        # Define required keys present in model yaml configuration
        req_keys = ["fre_properties", "build", "experiments", "nope"]
#        req_keys = ["ScalarToken(plain=True, style=None, value='fre_properties')"]
        # Open the model yaml configuration
        yml = open(self.yml, "r")

        # yaml.scan() - reads in YAML input stream abd breaks it down into
        # series of tokens
        ymlscan = yaml.scan(yml).__iter__()

        # Use map to convert list of classes to strings
        # Make list
        str_list = list(map(str, list(ymlscan)))
#        print(str_list)
#        quit()
#        for item in str_list:
#            if "ScalarToken" in item:
#                print(item)
#                for key in req_keys:
#                    if key in item:
#                        print(item)
#                else:
#                    print(f"noooooo {key}")
#        quit()
        for key in req_keys:
            if f"ScalarToken(plain=True, style=None, value='{key}'" in str_list:
                print(f"WOO HOOOOOO - {key} found")
            else:
                raise ValueError(f"MISSING REQUIRED KEY: {key}")

#        for thing in ymlscan:
#            for key in req_keys:
#                if str(thing).find(key) != -1:
#                    print(thing)
#                    print(f"WOO HOOOOOO - {key} found")
#            if str(thing) != "()":# and "ScalarToken(plain=True" in str(thing):
#            for key in req_keys:
#                if f"value='{key}'" in str(thing):
#                    print(thing)
#                    print("WOO HOOOOOO")
#                else:
#                    print(key)
#                    raise ValueError(f"MISSING REQUIRED KEY: {key}")

#    def validate values():
    def validate(self):
        self.validate_keys()
#        self.validate_values()

#class SettingsYmlStructure(YamlStructure):
#    def validate_keys():
#        present_keys = ["fre_properties", "directories", "postprocess"]
#    def validate values():
#    def validate():
#        self.validate_keys()
#        self.validate_values()

#class CompileYamlStructure(YamlStructure):
#class PlatformsYamlStructure(YamlStructure):
#class PPYamlStructure(YamlStructure):
#class AnalysisYamlStructure(YamlStructure):
#class CMORYamlStructure(YamlStructure):
