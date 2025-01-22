"""
Script combines the model yaml with exp, platform, and target to list experiment information.
"""

import os
import click
import yaml
import fre.yamltools.combine_yamls as cy
from pathlib import Path

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

def quick_combine(yml, exp, platform, target,combined):
    """
    """
    # Combine model / experiment
    comb = cy.init_compile_yaml(yml,platform,target)
    comb.combine_model()
    comb.combine_platforms()

def clean(combined):
    if Path(combined).exists():
        os.remove(combined)
        print(f"{combined} removed.")

def list_platforms_subtool(yamlfile):
    # Regsiter tag handler
    yaml.add_constructor('!join', join_constructor)

    e = yamlfile.split("/")[-1].split(".")[0] #"exp_placeholder"
    p = "p_placeholder"
    t = "t_placeholder"

    combined=f"combined-am5.yaml"
    # Combine model / experiment
    quick_combine(yamlfile,e,p,t,combined)

    # Print experiment names
    c = yaml_load(combined)

    print("\nPlatforms available:")
    for i in c.get("platforms"):
        print(f'    - {i.get("name")}')
    print("\n")
    clean(combined)
