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

# To look into: ignore undefined alias error msg for listing?
# Found this somewhere but don't fully understand yet
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

def quick_combine(yml, platform, target):
    """
    Combine the intermediate model and platforms yaml.
    This is done to avoid an "undefined alias" error
    """
    # Combine model / experiment
    comb = cy.init_compile_yaml(yml,platform,target)
    comb.combine_model()
    comb.combine_platforms()

def clean(combined):
    """
    Remove intermediate combined yaml.
    """
    if Path(combined).exists():
        os.remove(combined)
        print(f"{combined} removed.")

def list_platforms_subtool(yamlfile):
    """
    List the platforms available
    """
    # Regsiter tag handler
    yaml.add_constructor('!join', join_constructor)

    e = yamlfile.split("/")[-1].split(".")[0] #"exp_placeholder"
    p = "p_placeholder"
    t = "t_placeholder"

    combined=f"combined-{e}.yaml"
    yamlpath = os.path.dirname(yamlfile)

    # Combine model / experiment
    quick_combine(yamlfile,p,t)

    # Print experiment names
    c = yaml_load(os.path.join(yamlpath,combined))

    print("\nPlatforms available:")
    for i in c.get("platforms"):
        print(f'    - {i.get("name")}')
    print("\n")
    clean(combined)
