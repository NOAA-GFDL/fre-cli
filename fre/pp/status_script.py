''' fre pp status '''

import subprocess
import logging
from . import make_workflow_name
fre_logger = logging.getLogger(__name__)
TIMEOUT_SECS=120#30

def status_subtool(experiment = None, platform = None, target = None):
    """
    Report workflow state for the Cylc workflow $(experiment)__$(platform)__$(target)
    
    :param experiment: Name of post-processing experiment, default is None
    :type experiment: string
    :param platform: Name of the platform upon which the original experiment was run. Default is None.
    :type platform: string
    :param target: Name of the target . Default is None.
    :type target: string
    """

    if None in [experiment, platform, target]:
        raise ValueError( 'experiment, platform, and target must all not be None.'
                          'currently, their values are...'
                          f'{experiment} / {platform} / {target}')    

    workflow_name = make_workflow_name(experiment, platform, target)
    cmd = f"cylc workflow-state {workflow_name}" 
    fre_logger.debug('running the following command: ')
    fre_logger.debug(cmd)

    try:
        subprocess.run(cmd, shell=True, check=True, timeout=TIMEOUT_SECS)
    except:
        raise Exception('FAILED: subprocess call to- cylc workflow-state {name}')

if __name__ == "__main__":
    status_subtool()
