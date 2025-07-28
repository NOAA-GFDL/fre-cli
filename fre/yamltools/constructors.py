''' this file holds yaml-constructors for fre.yamltools '''

def join_constructor(loader, node):
    """
    Allows FRE properties defined
    in main yaml to be concatenated.

    :param loader:
    :type loader:
    :param node:
    :type node:
    :return:
    :rtype: str
    """
    seq = loader.construct_sequence(node)
    return ''.join( [ str(i) for i in seq ] )
