''' this file holds yaml-constructors for fre.yamltools '''

import typing

def join_constructor(loader, node) -> str:
    """
    Allows strings defined as elements in a list, specified in a yaml, to be concatenated together. this constructor
    is generally getting associated with the default yaml.Loader used by the pyyaml module. This function is not generally
    called directly. see fre.yamltools' __init__.py for more information.

    Parameters
    ----------
    loader : a yaml.Loader object
    node : (an) element(s) of a yaml representation graph to map to a string in python

    Returns
    -------
    string

    Notes
    -----
    - see https://pyyaml.org/wiki/PyYAMLDocumentation for more info on yaml constructors
    - see other files in fre.yamltools that import this constructor and the yaml module at the same time
    - the constructor gets called in a yamlfile like !join[ ... ]
    - this will result in an attempt to resolve aliases and other complex objects to their final ascii values
    """
    seq = loader.construct_sequence(node)
    return ''.join( [ str(i) for i in seq ] )
