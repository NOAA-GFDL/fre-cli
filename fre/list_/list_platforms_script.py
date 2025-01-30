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

def quick_combine(yml, platform, target):
    """
    Combine the intermediate model and platforms yaml.
    This is done to avoid an "undefined alias" error
    """
    # Combine model / experiment
    comb = cy.init_compile_yaml(yml,platform,target)
    comb.combine_model()
    comb.combine_platforms()

def remove(combined):
    """
    Remove intermediate combined yaml.
    """
    if Path(combined).exists():
        Path(combined).unlink()
        print("Remove intermediate combined yaml:\n",
              f"   {combined} removed.")
    else:
        raise ValueError(f"{combined} could not be found to remove.")

def list_platforms_subtool(yamlfile):
    """
    List the platforms available
    """
    # Regsiter tag handler
    yaml.add_constructor('!join', cy.join_constructor)

    e = yamlfile.split("/")[-1].split(".")[0]
    p = None
    t = None

    combined = f"combined-{e}.yaml"
    yamlpath = Path(yamlfile).parent

    # Combine model / experiment
    quick_combine(yamlfile,p,t)

    # Print experiment names
    c = cy.yaml_load(f"{yamlpath}/{combined}")

    print("\nPlatforms available:")
    for i in c.get("platforms"):
        print(f'    - {i.get("name")}')
    print("\n")

    # Clean the intermediate combined yaml
    #remove(f"{yamlpath}/{combined}")
