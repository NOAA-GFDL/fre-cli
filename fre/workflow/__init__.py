from typing import Optional

def make_workflow_name(experiment : Optional[str] = None) -> str:
    """
    Function that takes in a triplet of tags for a model experiment, platform, and target, and
    returns a directory name for the corresponding pp workflow. Because this is often given by
    user to the shell being used by python, we split/reform the string to remove semi-colons or
    spaces that may be used to execute an arbitrary command with elevated privileges.

    :param experiment: One of the postprocessing experiment names from the yaml displayed by fre list exps -y $yamlfile (e.g. c96L65_am5f4b4r0_amip), default None
    :type experiment: str
    :param platform: The location + compiler that was used to run the model (e.g. gfdl.ncrc5-deploy), default None
    :type platform: str
    :param target: Options used for the model compiler (e.g. prod-openmp), default None
    :type target: str
    :return: string created in specific format from the input strings
    :rtype: str

    .. note:: if any arguments are None, then "None" will appear in the workflow name
    """
    name = f'{experiment}__{platform}__{target}'
    return ''.join(
                      (''.join(
                          name.split(' ')
                              )
                      ).split(';')
                  ) # user-input sanitation, prevents some malicious cmds from being executed with privileges
