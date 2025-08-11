import os
from pathlib import Path
import yaml
from contextlib import contextmanager

# set up logging
import logging
fre_logger = logging.getLogger(__name__)

def get_variables(yml: dict, pp_comp: str) -> dict:
    """Retrieve any variables specified with active pp components from the yaml

    :param yml: loaded yaml file
    :type yml: dict
    :param pp_comp: Active pp component
    :type pp_comp: str
    :raises ValueError: if the active pp component is not found in the yaml configuration
    :return: dictionary of {source name: [variables]}
        - the values are a list of specified variables
        - if no variables specified, the value will be 'all'
    :rtype: dict
    """
    fre_logger.debug(f"Yaml file information: {yml}")
    fre_logger.debug(f"PP component: {pp_comp}")
    if not isinstance(yml, dict):
        raise TypeError("yml should be of type dict, but was of type " + str(type(yml)))

    src_vars={}

    for component_info in yml["postprocess"]["components"]:
        # if component in yaml not an active pp component, skip
        if component_info.get("type") != pp_comp:
            fre_logger.info(f'Component, %s, in pp yaml config, does not match active pp component: %s', component_info.get("type"), pp_comp)
            continue

        # non-static
        src_info = component_info.get("sources")
        for src_elem in src_info:
            # if variables are defined, append to dictionary
            if src_elem.get("variables"):
                src_vars[src_elem.get("history_file")] = src_elem.get("variables")
            else:
                src_vars[src_elem.get("history_file")] = "all"

        # static
        if component_info.get("static"):
            static_info = component_info.get("static")
            for static_elem in static_info:
                # if variables are defined, append to dictionary
                if static_elem.get("variables"):
                    src_vars[static_elem.get("source")] = static_elem.get("variables")
                else:
                    src_vars[static_elem.get("source")] = "all"

        ##offline statics won't use variables filtering ... yet?

    # If the dictionary is empty (no overlap of pp components and components 
    # in pp yaml) --> error
    if not src_vars:
        raise ValueError(f"PP component, {pp_comp}, not found in pp yaml configuration!")

    return src_vars

## NOTE: For python 3.11 - this might be available already as contextlib.chdir()
## Re-asses if our own contextmanager function is needed here
@contextmanager
def change_directory(new_path: str):
    """Temporarily change the directory

    :param new_path: Path to change into
    :type new_path: str
    """
    ## Get current working directory
    original_path = os.getcwd()

    ## Change into path passed
    os.chdir(new_path)

    ## Execute code within the 'with' block when using this function 
    ## ('with change_directories(path):'), then go back to the original
    ## directory 
    # 'yield': used to create generators (special types of iterators that allow
    #                                     for lazy value production; produces
    #                                     values at time of iteration)
    try:
        yield
    finally:
        os.chdir(original_path)
