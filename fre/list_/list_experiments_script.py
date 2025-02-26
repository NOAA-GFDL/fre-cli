"""
Script combines the model yaml with exp, platform, and target to list experiment information.
"""

#import logging
#fre_logger = logging.getLogger(__name__)

from pathlib import Path

# this brings in the yaml module with the join_constructor
# this is defined in the __init__
from fre.yamltools import *


from fre.yamltools.helpers import yaml_load
from fre.yamltools import combine_yamls as cy

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
    # note, this needs combine_yamls.py, instead of it's successor for now
    comb = cy.init_pp_yaml(yml,exp,platform,target)
    comb.combine_model()

def remove(combined):
    """
    Remove intermediate combined yaml.
    """
    if Path(combined).exists():
        Path(combined).unlink()
        #fre_logger.info("Remove intermediate combined yaml:\n",
        print("Remove intermediate combined yaml:\n",
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

    combined = f"combined-{e}.yaml"

    # Combine model / experiment
    quick_combine(yamlfile,e,p,t)

    # Print experiment names
    c = yaml_load(combined)

    
    ## is this, perhaps, the one spot where print is preferred? 
    #fre_logger.info("\nPost-processing experiments available:")
    #for i in c.get("experiments"):
    #    fre_logger.info(f'   - {i.get("name")}')
    #fre_logger.info("\n")


    # is this, perhaps, the one spot where print is preferred?
    # keep around for a minute as a comment, please.
    print("\nPost-processing experiments available:")
    for i in c.get("experiments"):
        print(f'   - {i.get("name")}')
    print("\n")

    # Clean intermediate combined yaml
    remove(combined)
