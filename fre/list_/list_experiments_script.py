"""
Script combines the model yaml with exp, platform, and target to list experiment information.
"""
import os
from pathlib import Path
import yaml
import fre.yamltools.combine_yamls as cy

def join_constructor(loader, node):
    """
    Allows FRE properties defined
    in main yaml to be concatenated.
    """
    seq = loader.construct_sequence(node)
    return ''.join([str(i) for i in seq])

#class NoAliasDumper(yaml.SafeDumper):
#    def ignore_aliases(self, data):
#        return True

def yaml_load(yamlfile):
    """
    Load the yamlfile
    """
    with open(yamlfile, 'r') as yf:
        y = yaml.load(yf,Loader=yaml.Loader)

    return y

def quick_combine(yml, exp, platform, target):
    """
    Create intermediate combined model and exp. yaml
    This is done to avoid an "undefined alias" error
    """
    # Combine model / experiment
    comb = cy.init_pp_yaml(yml,exp,platform,target)
    comb.combine_model()

def clean(combined):
    """
    Remove intermediate combined yaml.
    """
    if Path(combined).exists():
        os.remove(combined)
        print(f"{combined} removed.")

def list_experiments_subtool(yamlfile):
    """
    List the post-processing experiments available
    """
    # Regsiter tag handler
    yaml.add_constructor('!join', join_constructor)

    e = "exp_placeholder"
    p = "p_placeholder"
    t = "t_placeholder"

    combined=f"combined-{e}.yaml"
    # Combine model / experiment
    quick_combine(yamlfile,e,p,t)

    # Print experiment names
    c = yaml_load(combined)

    print("\nPost-processing experiments available:")
    for i in c.get("experiments"):
        print(f'   - {i.get("name")}')
    print("\n")
    clean(combined)
