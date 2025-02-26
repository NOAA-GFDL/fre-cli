''' this holds functions widely used across various parts of fre/yamltools '''

# this brings in the yaml module with the join_constructor
# this is defined in the __init__
from . import *

def yaml_load(yamlfile):
    """
    Load the yamlfile
    """
    with open(yamlfile, 'r') as yf:
        y = yaml.load(yf, Loader = yaml.Loader)

    return y


def output_yaml(cleaned_yaml, experiment, output):
    """
    Write out the combined yaml dictionary info
    to a file if --output is specified
    """
    filename = output
    with open(filename,'w') as out:
        out.write(
            yaml.dump(
                cleaned_yaml,
                default_flow_style = False,
                sort_keys = False ) )
