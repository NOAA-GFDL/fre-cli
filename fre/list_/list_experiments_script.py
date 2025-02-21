"""
Script combines the model yaml with exp, platform, and target to list experiment information.
"""
import logging
fre_logger = logging.getLogger(__name__)

from pathlib import Path
#import yaml

import fre.yamltools.pp_info_parser as ppip
from fre.yamltools.combine_yamls_script import yaml_load

# To look into: ignore undefined alias error msg for listing?
# Found this somewhere but don't fully understand yet
#class NoAliasDumper(yaml.SafeDumper):
#    def ignore_aliases(self, data):
#        return True

def quick_combine(yml, exp, platform, target):
    """
    Create intermediate combined model and exp. yaml
    This is done to avoid an "undefined alias" error
    """
    # Combine model / experiment
    PPYaml = ppip.PPYaml(yml,exp,platform,target)
    PPYaml.combine_model()

def remove(combined):
    """
    Remove intermediate combined yaml.
    """
    if Path(combined).exists():
        Path(combined).unlink()
        fre_logger.info("Remove intermediate combined yaml:\n",
              f"   {combined} removed.")
    else:
        raise ValueError(f"{combined} could not be found to remove.")

def list_experiments_subtool(yamlfile):
    """
    List the post-processing experiments available
    """

    e = "None"
    p = "None"
    t = "None"

    # Combine model / experiment
    quick_combine(yamlfile,e,p,t)

    combined = f"combined-{e}.yaml"
    #assert Path(combined).exists()

    # Print experiment names
    c = yaml_load(combined)

    fre_logger.info("\nPost-processing experiments available:")
    for i in c.get("experiments"):
        fre_logger.info(f'   - {i.get("name")}')
    fre_logger.info("\n")

    # Clean intermediate combined yaml
    remove(combined)
