'''
Abstract base classes to provide scaffolding of
yaml combining process for classes that inherit
them.
'''
from abc import ABC, abstractmethod

# inherited by pp_info_parser and analysis_info_parser
class MergePPANYamls(ABC):
    """
    Scaffolding for merging pp and analysis yamls; inherited by pp_info_parser
    and analysis_info_parser
    """
    @abstractmethod
    def combine_model(self):
        """
        Function that will combine model yaml information with
        passed click options name, platform, and target
        """
        pass

    @abstractmethod
    def combine_settings(self, yaml_content_str):
        """
        Function that will combine settings yaml information
        with output yaml str from combine_model
        """
        pass

    @abstractmethod
    def combine_yamls(self):
        """
        Function that will combine output yaml str (from merging 
        the model and settings yaml) with pp/experiment yaml information
        """
        pass

    @abstractmethod
    def merge_multiple_yamls(self):
        """
        Function that will merge multiple yaml dictionaries
        to produce final combined yaml of information
        """
        pass

# inherited by compile_info_parser
class MergeCompileYamls(ABC):
    """
    Scaffolding for merging compile yamls; inherited by compile_info_parser
    """
    @abstractmethod
    def combine_model(self):
        """
        Function that will combine model yaml information with
        passed click options name, platform, and target
        """
        pass

    @abstractmethod
    def combine_compile(self):
        """
        Function that will combine compile yaml information
        with output yaml str from combine_model
        """
        pass

    @abstractmethod
    def combine_platforms(self):
        """
        Function that will combine platform yaml information
        with output yaml str from combine_compile
        """
        pass

#class ValidateYamls(ABC):
#    @abstractmethod
#    def validate_keys():
#        pass
#
#    @abstractmethod
#    def validate_values():
#        pass
#
#    @abstractmethod
#    def validate():
#        pass
