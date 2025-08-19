''' this file holds yaml-constructors for fre.yamltools '''

import typing
import yaml

def _join_constructor( loader: yaml.Loader,
                      node: yaml.Node ) -> str:
    """
    Allows strings defined as elements in a list, specified in a yaml, to be concatenated together. this constructor
    is generally getting associated with the default yaml.Loader used by the pyyaml module. This function is not generally
    called directly. see fre.yamltools' __init__.py for more information.

    :param loader: a yaml.Loader object
    :type loader: yaml.Loader
    :param node: (an) element(s) of a yaml representation graph to map to a string in python
    :type node: yaml.Node
    :return: Concatenated string from the list elements
    :rtype: str

    .. note:: see https://pyyaml.org/wiki/PyYAMLDocumentation for more info on yaml constructors
    .. note:: see other files in fre.yamltools that import this constructor and the yaml module at the same time
    .. note:: the constructor gets called in a yamlfile like !join[ ... ]
    .. note:: this will result in an attempt to resolve aliases and other complex objects to their final ascii values
    """
    seq = loader.construct_sequence(node)
    return ''.join( [ str(i) for i in seq ] )
