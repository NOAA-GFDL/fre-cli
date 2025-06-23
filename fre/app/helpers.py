import os
from pathlib import Path
import yaml

# set up logging
import logging
logging.basicConfig(level=logging.INFO)
fre_logger = logging.getLogger(__name__)

def get_variables(yml, pp_comp):
    """
    Retrieve any variables specified with active
    pp components from the yaml

    Arguments:
        yamlfile (str): Loaded yaml file
        pp_components (str): Space separated list of active pp components
    """
#    fre_logger.debug(f"Yaml file: {yamlfile}")
    fre_logger.debug(f"PP components: {pp_comp}")

#    pp_comp = pp_components.split()
#    with open(yamlfile) as file_:
#        yml = yaml.safe_load(file_)

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

## TEST ##
#print(get_variables("/home/Dana.Singh/fre/get-vars-jinjafilter/Jinja2Filters/yaml_ex.yaml", "atmos_scalar atmos_scalar_test_vars atmos_scalar_test_vars_fail atmos_scalar_static_test_vars_fail"))
