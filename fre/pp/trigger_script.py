''' fre pp trigger '''

import subprocess
from . import make_workflow_name
import logging
fre_logger = logging.getLogger(__name__)

def trigger(experiment = None, platform = None, target = None, time = None):
    """
    Trigger the postprocessing tasks for one segment of the history.
    :param experiment: One of the postprocessing experiment names from the yaml displayed by fre list exps -y $yamlfile (e.g. c96L65_am5f4b4r0_amip), default None
    :type experiment: str
    :param platform: The location + compiler that was used to run the model (e.g. gfdl.ncrc5-deploy), default None
    :type platform: str
    :param target: Options used for the model compiler (e.g. prod-openmp), default None
    :type target: str
    :param time: The start time of the segment. Formatted as a series of integers.
    :type time: Cylc representation of a time point
    ..note: 
    The segment is defined as a start point (--time) and a duration (defined in
    the experiment yaml). Cylc combines the two for a cycle duration; we are using
    datetime cycling (https://cylc.github.io/cylc-doc/stable/html/glossary.html#term-datetime-cycling)
    for FRE. Historically, the start point has often been formatted YYYYMMDD and is 
    the first chunk of a filename (19790101.atmos_tracer.tile6.nc).
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


if __name__ == "__main__":
    trigger()
