import os
import logging
fre_logger = logging.getLogger(__name__)
from pathlib import Path
#import pprint

# this boots yaml with !join- see __init__
from . import *

from abc import ABC, abstractmethod

# inherited by pp_info_parser and analysis_info_parser
class MergePPANYamls(ABC):
    @abstractmethod
    def combine_model(self):
        """
        :return:
        :rtype: str
        """
        pass

    @abstractmethod
    def get_settings_yaml(self, yaml_content_str):
        """
        :return:
        :rtype: str
        """
        pass

    @abstractmethod
    def combine_yamls(self):
        """
        :return:
        :rtype: str
        """
        pass

    @abstractmethod
    def merge_multiple_yamls(self):
        """
        :return:
        :rtype: str
        """
        pass

# inherited by compile_info_parser
class MergeCompileYamls(ABC):
    @abstractmethod
    def combine_model():
        """
        :return:
        :rtype: str
        """
        pass

    @abstractmethod
    def combine_compile():
        """
        :return:
        :rtype: str
        """
        pass

    @abstractmethod
    def combine_platforms():
        """
        :return:
        :rtype: str
        """
        pass

class ValidateYamls(ABC):
#    @abstractmethod
#    def validate_keys():
#        pass
#
#    @abstractmethod
#    def validate_values():
#        pass
#
    @abstractmethod
    def validate():
        pass
