''' fre pp trigger '''

import subprocess
from . import make_workflow_name
import logging
fre_logger = logging.getLogger(__name__)

def trigger(experiment = None, platform = None, target = None, time = None):
    """
    Trigger the pp-starter task for the time indicated
    """
    if None in [experiment, platform, target, time]:
        raise ValueError( 'experiment, platform, target and time must all not be None.'
                          'currently, their values are...'
                          f'{experiment} / {platform} / {target} / {time}')

    #name = experiment + '__' + platform + '__' + target
    workflow_name = make_workflow_name(experiment, platform, target)
    cmd = f"cylc trigger {workflow_name}//{time}/pp-starter"
    fre_logger.debug('running the following command: ')
    fre_logger.debug(cmd)
    subprocess.run(cmd, shell=True, check=True, timeout=30)
