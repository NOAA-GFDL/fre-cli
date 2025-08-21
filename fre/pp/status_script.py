''' fre pp status '''

import subprocess
import logging
from . import make_workflow_name
fre_logger = logging.getLogger(__name__)
TIMEOUT_SECS=120#30

def status_subtool(experiment = None, platform = None, target = None):
    """
    Report workflow state for the Cylc workflow $(experiment)__$(platform)__$(target)
    
    :param experiment: One of the postprocessing experiment names from the yaml displayed by fre list exps -y $yamlfile (e.g. c96L65_am5f4b4r0_amip), default None
    :type experiment: str
    :param platform: The location + compiler that was used to run the model (e.g. gfdl.ncrc5-deploy), default None
    :type platform: str
    :param target: Options used for the model compiler (e.g. prod-openmp), default None
    :type target: str
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
