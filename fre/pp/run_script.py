''' fre pp run '''
import subprocess
import time
import logging
fre_logger = logging.getLogger(__name__)

from . import make_workflow_name

def pp_run_subtool(experiment = None, platform = None, target = None,
                   pause = False, no_wait = False):
    """
    Starts, pauses or restarts the Cylc workflow described by $(experiment)__$(platform)__$(target)
    
    :param experiment: Name of a post-processing experiment in the yaml, default is None
    :type experiment: string
    :param platform: Platform + compiler upon which the model was run. Default is None.
    :type platform: string
    :param target: Name of the target . Default is None.
    :type target: string
    :param pause: Whether to pause the current Cylc workflow. Defaults to false, which starts or restarts the workflow.
    :type pause: boolean
    :param no_wait: Whether to avoid waiting at least 30 seconds for confirmation that the workflow is stopped. Defaults to False, which waits for confirmation.
    :type no_wait: boolean
    """
    if None in [experiment, platform, target]:
        raise ValueError( 'experiment, platform, and target must all not be None.'
                          'currently, their values are...'
                          f'{experiment} / {platform} / {target}')

    # Check to see if the workflow is already running
    name = make_workflow_name(experiment, platform, target)
    first_cmd = f'cylc scan --name ^{name}$'
    fre_logger.debug('running the following command: ')
    fre_logger.debug(first_cmd)
    result = subprocess.run(['cylc', 'scan', '--name', f"^{name}$"], capture_output = True ).stdout.decode('utf-8')
    if len(result):
        fre_logger.info("Workflow already running!")
        return

    # If not running, start it
    cmd  = "cylc play"
    if pause:
        cmd+=" --pause"
    cmd +=f" {name}"
    subprocess.run(cmd, shell=True, check=True)

    # not interested in the confirmation? gb2work now
    if no_wait:
        return

    # give the scheduler 30 seconds of peace before we hound it
    fre_logger.info("Workflow started; waiting 30 seconds to confirm")
    time.sleep(30)

    # confirm the scheduler came up. note the regex surrounding {name} for start/end of a string to avoid glob matches
    result = subprocess.run(
        ['cylc', 'scan', '--name', f"^{name}$"],
        capture_output = True ).stdout.decode('utf-8')

    if not len(result):
        raise Exception('Cylc scheduler was started without error but is not running after 30 seconds')

    fre_logger.info(result)

if __name__ == "__main__":
    pp_run_subtool()
