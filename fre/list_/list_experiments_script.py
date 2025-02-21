"""
Script combines the model yaml with exp, platform, and target to list experiment information.
"""
import logging
fre_logger = logging.getLogger(__name__)

from pathlib import Path
#import yaml

import fre.yamltools.pp_info_parser as ppip
from fre.yamltools.combine_yamls_script import yaml_load
from fre.yamltools.combine_yamls_script import output_yaml
from fre.yamltools.combine_yamls_script import get_combined_ppyaml
# To look into: ignore undefined alias error msg for listing?
# Found this somewhere but don't fully understand yet
#class NoAliasDumper(yaml.SafeDumper):
#    def ignore_aliases(self, data):
#        return True

def quick_combine(yml, exp, platform, target, output):
    """
    Create intermediate combined model and exp. yaml
    This is done to avoid an "undefined alias" error
    """
    # Combine model / experiment
    
    PPYaml = ppip.PPYaml(yml,exp,platform,target)
    get_combined_ppyaml( PPYaml, exp, output= output)
    

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

    e = None
    p = None
    t = None

    combined = f"combined-temp.yaml"
    #assert Path(combined).exists()

    # Combine model / experiment
    quick_combine(yamlfile, e,p,t, combined)

    # Print experiment names
    c = yaml_load(combined)

    fre_logger.info("\nPost-processing experiments available:")
    for i in c.get("experiments"):
        fre_logger.info(f'   - {i.get("name")}')
    fre_logger.info("\n")

    # Clean intermediate combined yaml
    remove(combined)
