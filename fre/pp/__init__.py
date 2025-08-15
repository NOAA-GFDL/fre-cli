from typing import Optional

def make_workflow_name(experiment : Optional[str] = None,
                       platform : Optional[str] = None,
                       target : Optional[str] = None) -> Optional[str]:
    """
    function that takes in a triplet of tags for a model experiment, platform, and target, and
    returns a directory name for the corresponding pp workflow. because this is often given by 
    user to the shell being used by python, we split/reform the string to remove semi-colons or
    spaces that may be used to execute an arbitrary command with elevated privileges.

    :param experiment: string representing the name of an experiment
    :type experiment: str
    :param platform: string representing the name of a platform
    :type platform: str
    :param target: string representing the name of a compilation target
    :type target: str
    :return: string created in specific format from the input strings
    :rtype: str

    .. note:: does not check for inputs for None value, and will use it to create a return object
    """
    name = f'{experiment}__{platform}__{target}'
    return ''.join(
                      (''.join(
                          name.split(' ')
                              )
                      ).split(';')
                  ) # user-input sanitation, prevents some malicious cmds from being executed with privileges




