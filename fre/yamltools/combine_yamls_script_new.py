"""
YAML Combination Utilities for FRE
----------------------------------

This module provides utility functions for combining model, experiment, compile, platform, and analysis
YAML files into unified configurations for the Flexible Runtime Environment (FRE) workflow. It offers routines
to consolidate YAMLs for CMORization, compilation, and post-processing, supporting both command-line tools
and internal workflow automation.


- can use fre list output to pipe to this tool
- can use this tool with just model yaml (will use fre list tool)
- can use this tool to pass in multiple yamls either comma separated string
  (-y y1,y2) OR multiple options (-y y1 -y y2 ...)
- checks fre-version
- uses uw config compose (to combine), resolve (to check unrendered values), and validate (to validate yaml)
"""

import os
import logging
import contextlib
from pathlib import Path
from typing import Optional

from uwtools.api import config
from uwtools.api.logging import use_uwtools_logger
#from fre.list_.list_yamls_script import list_yamls_subtool
from fre.yamltools.helpers import output_yaml, clean_yaml#, check_fre_version

fre_logger = logging.getLogger(__name__)

class LetsGo():
    """
    :ivar: ??
    """
    def __init__(self, yamls, experiment, platform, target, output):
        """
        :param yamls:
        :type yamls:
        :param experiment:
        :type experiment:
        :param platform:
        :type platform:
        :param target:
        :type target:
        :param output:
        :type output:
        """
        self.y = yamls.split(",")
        self.e = experiment
        self.p = platform
        self.t = target
        self.o = output

    def list_check_yamls(self, init_file):
        """
        :param init_file:
        :type init_file:
        """
        yaml_list=[]
        # create intermediate yaml to pass to uw config compose
        #  - needs yamls files; cannot pass dictionaries
        #  - intermediate yaml file will be removed later
        init = {"name": self.e, "platform": self.p, "target": self.t}
        output_yaml(init, init_file)

        ## append init file (needed for schema and other variables?)
        yaml_list.append(init_file)

        ## self.y should be a list
        ## case where it might not be?
        yaml_list.extend(self.y)

        for y in yaml_list:
            if not Path(y).exists():
                fre_logger.error(" *** YAML FILES DNE: %s ***", y)
                raise ValueError("Yaml files could be not found!")

        return yaml_list

    def use_uwtools(self, yaml_list):
        """
        :param self:
        :param yaml_list:
        :type yaml_list:

        :raises:
        """
        ## COMBINE YAMLS AND RESOLVE WHERE WE CAN ##
        ## uw config compose: pass yaml list to compose final yaml

        # CAN THIS BE DICTIONARIES??
        # config.compose returns a base class specifying methods to read, manipulate,
        # and write several configuration-file formats. (use as_dict to return dictionary)
        # use realize=True to resolve what we can here; if any unresolved, it does not error out
        # yet (use config.realize)

        # Mainly just want to pass dictionary to config.resolve but output from config.compose is a printed dictionary
        # we don't need all this output but maybe it can be wrapped up in fre_logger.debug if needed?
        with open(os.devnull, 'w', encoding="utf-8") as f, contextlib.redirect_stdout(f):
            print("This will not be displayed")
            combined_yaml_dict = config.compose(configs=yaml_list, realize=True).as_dict()

        # CLEAN SERIALIZED YAML ##
        cleaned_yaml_dict = clean_yaml(combined_yaml_dict)
        if not cleaned_yaml_dict:
            raise ValueError("YAML configuration could not be cleaned (experiments)")

        ###  SHOLD BE RESOLVED BUT THIS IS TO CATCH ANY UNRESOLVED JUST IN CASE AND OUTPUT TO FILE IF SPECIFIED ##
        ## uw config realize: resolve final yaml
        # get nice uw tools cli output
        use_uwtools_logger()

        config.realize(input_config = cleaned_yaml_dict,
                       values_needed = True,
                       total = True)

        if self.o:
            out_path = Path.cwd()/self.o
            fre_logger.info("Writing resolved YAML file: %s", out_path)
            output_yaml(cleaned_yaml_dict, out_path)
        # Is this helpful? (if config.realize fails, it will not be written to output file,
        # but error will hopefully come up; this is just more output if the user wants to
        # see what the combined yaml dictonary would look like
        #fre_logger.debug(pformat(cleaned_yaml_dict))
        else:
            fre_logger.info("Resolved YAML saved as dictionary. To display dictionary, pass fre -v ...")
            fre_logger.info(cleaned_yaml_dict)

        return cleaned_yaml_dict

#    def validate(self, final_dict)
#        """
#        """

# VALIDATE SERIALIZED YAML ##
#    ## uw config validate
#    # output from validate is True or False
#    validate_out = config.validate(schema_file="/home/Dana.Singh/fre/singh/generalize-yaml-serialization/fre/gfdl_msd_schemas/FRE/fre_make.json",
#                                   config_data=cleaned_yaml_dict)
#
#    # If the YAML is not valid, exit with error instead of continuing
#    if validate_out:
#        fre_logger.info("VALID")
#    else:
#        fre_logger.error("INVALID")
#        raise ValueError("INVALID. CHECK YA YAMLS")
#
## Combine schemas?
#from json import load, dump
#
#with open("/home/Dana.Singh/fre/singh/generalize-yaml-serialization/fre/gfdl_msd_schemas/FRE/fre_make.json") as j1, open("/home/Dana.Singh/fre/singh/generalize-yaml-serialization/fre/gfdl_msd_schemas/FRE/fre_pp.json") as j2, open("j3.json", 'w') as j3:
#    dump([load(j1), load(j2)], j3)

def yamltools_combine_subtool(yamls:str, experiment:str, platform:str, target:str, output: Optional[str]=None) -> dict:
    """
    :param yamls:
    :type yamls: str
    :param experiment:
    :type experiment: str
    :param platform:
    :type platform: str
    :param target:
    :type target: str
    :param output:
    :type output: str
    """
#    fre_logger.info('checking fre_cli_version compatibility...')
#    check_fre_version(combined)
    
    init_obj = LetsGo(yamls, experiment, platform, target, output)

    init_file = f"{Path.cwd()}/init.yaml"
    ymls = init_obj.list_check_yamls(init_file)
    combined = init_obj.use_uwtools(ymls)

#    #validate
#    init_obj.validate(combined)

    # clean init_file (not needed anymore)
    Path(init_file).unlink()

    return combined

##### NOTES:
##### - report of unrendered keys only shown when total not used with values_needed
##### - report shows keys and vals; values is a list in a list and shows fre_properties AND  FRE_STEM
##### - uw config compose WILL output yaml dictionary unless --output [file] is specified
