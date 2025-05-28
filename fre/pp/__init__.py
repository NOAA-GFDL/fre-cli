def make_workflow_name(experiment= None,
                       platform  = None,
                       target    = None):
    '''
    function that takes in a triplet of tags for a model experiment, platform, and target, and
    returns a directory name for the corresponding pp workflow. because this is often given by 
    user to the shell being used by python, we split/reform the string to remove semi-colons or
    spaces that may be used to execute an arbitrary command with elevated priveleges.
    inputs: 
        experiment, platform, target are all required inputs and strings that will be parsed for 
        hostile directions
    outputs:
        the desired pp workflow directory name as a string
    '''
    name = f'{experiment}__{platform}__{target}'
    return ''.join(
                      (''.join(
                          name.split(' ')
                              )
                      ).split(';')
                  ) #security




