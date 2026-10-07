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
- uses uw config compose (to combine), resolve (to check unrendered values)
"""

import os
import logging
import contextlib
from pathlib import Path
from typing import Optional

from uwtools.api import config
from uwtools.api.logging import use_uwtools_logger
from fre.yamltools.helpers import output_yaml, clean_yaml#, check_fre_version

fre_logger = logging.getLogger(__name__)

class MergeYamls():
    """
    :ivar str yamls: is the list of YAML configuration files to combine
    :ivar str experiment: is the experiment name (relates to the run and postprocessing)
    :ivar str platform: is the FRE platform defined
    :ivar str target: is the predefined FRE targets; options include [prod/debug/repro]-openmp
    :ivar str output: is the file path to a file that will incude the final combined, resolved YAML
                      configuration file
    """
    def __init__(self, yamls, experiment, platform, target, output, no_clean):
        self.y = yamls.split(",")
        self.e = str(experiment)
        self.p = str(platform)
        self.t = str(target)
        self.o = output
        self.no_clean = no_clean

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

        # config.compose returns a base class specifying methods to read, manipulate,
        # and write several configuration-file formats. (use as_dict to return dictionary)
        # use realize=True to resolve what we can here; if any unresolved, it does not error out
        # yet (use config.realize)

        # Mainly just want to pass dictionary to config.resolve but output from config.compose is a printed dictionary
        # we don't need all this output but maybe it can be wrapped up in fre_logger.debug if needed?
        with open(os.devnull, 'w', encoding="utf-8") as f, contextlib.redirect_stdout(f):
            print("This will not be displayed")
            combined_yaml_dict = config.compose(configs=yaml_list, realize=True).as_dict()

        if self.no_clean:
            final_yaml_dict = combined_yaml_dict
        else:
            # CLEAN SERIALIZED YAML ##
            final_yaml_dict = clean_yaml(combined_yaml_dict)
#            if not final_yaml_dict:
#                raise ValueError("YAML configuration could not be cleaned (experiments)")

        ###  SHOLD BE RESOLVED BUT THIS IS TO CATCH ANY UNRESOLVED JUST IN CASE AND OUTPUT TO FILE IF SPECIFIED ##
        ## uw config realize: resolve final yaml
        # get nice uw tools cli output

        # Save current root logger handlers and level
        root_logger = logging.getLogger()
        original_handlers = list(root_logger.handlers)
        original_level = root_logger.level


        uwlogger = use_uwtools_logger()

        config.realize(input_config = final_yaml_dict,
                       values_needed = True,
                       total = True)

        # 3. Restore root logger state back to original
        root_logger.handlers = original_handlers
        root_logger.setLevel(original_level)

        if self.o:
            out_path = Path.cwd()/self.o
            fre_logger.info("Writing resolved YAML file: %s", out_path)
            output_yaml(final_yaml_dict, out_path)
        # Is this helpful? (if config.realize fails, it will not be written to output file,
        # but error will hopefully come up; this is just more output if the user wants to
        # see what the combined yaml dictonary would look like
        #fre_logger.debug(pformat(final_yaml_dict))
        else:
            fre_logger.info("Resolved YAML saved as dictionary. To display dictionary, pass fre -v ...")
            fre_logger.info(final_yaml_dict)

        return final_yaml_dict

def yamltools_combine_subtool(yamls:str, experiment:str, platform:str, target:str, output: Optional[str]=None, no_clean: Optional[bool]=False) -> dict:
    """
    :param yamls: is the list of YAML configuration files to combine
    :type yamls: str
    :param experiment: is the experiment name (relates to the run and postprocessing)
    :type experiment: str
    :param platform: is the FRE platform defined
    :type platform: str
    :param target: is the predefined FRE targets; options include [prod/debug/repro]-openmp
    :type target: str
    :param output: is the file path to a file that will incude the final combined, resolved YAML
                   configuration file
    :type output: str
    :param no_clean: is a True/False value to determine whether or not to remove any keys/sections from the YAML. Default is False.
    :type no_clean: boolean
    """
#    fre_logger.info('checking fre_cli_version compatibility...')
#    check_fre_version(combined)
    init_obj = MergeYamls(yamls, experiment, platform, target, output, no_clean)

    init_file = f"{Path.cwd()}/init.yaml"
    ymls = init_obj.list_check_yamls(init_file)
    combined = init_obj.use_uwtools(ymls)

    # clean init_file (not needed anymore)
    Path(init_file).unlink()

    return combined

##### NOTES:
##### - report of unrendered keys only shown when total not used with values_needed
##### - report shows keys and vals; values is a list in a list and shows fre_properties AND  FRE_STEM
##### - uw config compose WILL output yaml dictionary unless --output [file] is specified
