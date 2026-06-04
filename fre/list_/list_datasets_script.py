"""
Script combines the model yaml with the compile and platforms yaml.
Merged yaml dictionary is parsed to list dataset information.
"""

from pathlib import Path
import logging
from fre.yamltools import combine_yamls_script as cy
from fre.yamltools import helpers

fre_logger = logging.getLogger(__name__)

def list_datasets_subtool(yamlfile: str):
    """
    List the datasetsz available

    :param yamlfile: path to the yaml configuration file
    :type yamlfile: str
    """
    # set logger level to INFO
    former_log_level = fre_logger.level
    fre_logger.setLevel(logging.INFO)

    exp = yamlfile.split("/")[-1].split(".")[0]
    platform = None
    target = None

    # Combine model / experiment
    yml_dict = cy.consolidate_yamls(yamlfile = yamlfile,
                                    experiment = exp,
                                    platform = platform,
                                    target = target,
                                    use = "compile",
                                    output = None)

    # Validate the yaml
    fre_pkg_dir = Path(__file__).resolve().parents[1]
    schema_path = f"{fre_pkg_dir}/gfdl_msd_schemas/FRE/fre_make.json"
    # from fre.yamltools
    helpers.validate_yaml(yml_dict, schema_path)
    fre_logger.info("Datasets available:")

    datasets_dict = yml_dict.get("run", {}).get("input",{}).get("datasets", {})
    datasets_source_list = []
  
    # Loop through each group under datasets (e.g., 'common_LM4p2')
    for dataset_group, items in datasets_dict.items():
        if isinstance(items, list):
            for item in items:
                datasets_source_list.append(item.get("source"))

    print(f"Returning {len(datasets_source_list)} dataset absolute paths from {yamlfile}")
    return datasets_source_list
  
    fre_logger.info("\n")
    fre_logger.setLevel(former_log_level)
