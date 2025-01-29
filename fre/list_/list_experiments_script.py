"""
Script combines the model yaml with exp, platform, and target to list experiment information.
"""
from pathlib import Path
import yaml
import fre.yamltools.combine_yamls as cy

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
    comb = cy.init_pp_yaml(yml,exp,platform,target)
    comb.combine_model()

def remove(combined):
    """
    Remove intermediate combined yaml.
    """
    if Path(combined).exists():
        Path(combined).unlink()
        print(f"{combined} removed.")

def list_experiments_subtool(yamlfile):
    """
    List the post-processing experiments available
    """
    # Regsiter tag handler
    yaml.add_constructor('!join', cy.join_constructor)

    e = None
    p = None
    t = None

    combined=f"combined-{e}.yaml"
    # Combine model / experiment
    quick_combine(yamlfile,e,p,t)

    # Print experiment names
    c = cy.yaml_load(combined)

    print("\nPost-processing experiments available:")
    for i in c.get("experiments"):
        print(f'   - {i.get("name")}')
    print("\n")

    # Clean intermediate combined yaml
    remove(combined)
