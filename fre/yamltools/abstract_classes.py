import os
import logging
fre_logger = logging.getLogger(__name__)
from pathlib import Path
#import pprint

# this boots yaml with !join- see __init__
from . import *

from abc import ABC, abstractmethod

class MergeYamlInfo(ABC):
    @abstractmethod
    def combine_model(self):
        pass

    @abstractmethod
    def get_settings_yaml(self, yaml_content_str):
        pass

#    @abstractmethod
#    def experiment_check():
#        pass

    @abstractmethod
    def combine_yamls(self):
        pass

    @abstractmethod
    def merge_multiple_yamls(self):
        pass 

#class AnalysisYamls():
#    @abstractmethod
#    def combine_model():
#        pass
#
#    @abstractmethod
#    def combine_settings():
#        pass
#
#    @abstractmethod
#    def combine_analysis():
#        pass
#
#    @abstractmethod
#    def merge_multiple_yamls():
#        pass
#
#    @abstractmethod
#    def clean_yaml():
#        pass
