import os
from pathlib import Path
import yaml
from contextlib import contextmanager

# set up logging
import logging
fre_logger = logging.getLogger(__name__)

def get_variables(yml, pp_comp):
    """Retrieve any variables specified with active pp components from the yaml

    :param yml: Already loaded yaml file
    :type yml: str
    :param pp_comp: List of active pp components
    :type pp_comp: str
    """
    fre_logger.debug(f"Yaml file information: {yml}")
    fre_logger.debug(f"PP components: {pp_comp}")

    src_vars={}
    for component_info in yml["postprocess"]["components"]:
        # if component in yaml not an active pp component, skip
        if component_info.get("type") not in pp_comp:
            fre_logger.info(f'{component_info.get("type")} not in list of pp components: {pp_comp}')
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

    return src_vars

## NOTE: For python 3.11 - this might be available already as contextlib.chdir()
## Re-asses if our own contextmanager function is needed here
@contextmanager
def change_directory(new_path):
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
