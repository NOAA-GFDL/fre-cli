''' fre run script '''

import logging
import os
from .drivers.frerun_driver import FrerunDriver

fre_logger = logging.getLogger(__name__)

def run_script_subtool(platform=None, experiment=None, target=None, submit=False, staging=False, **kwargs):
    """
    Core run script functionality - implementing frerun-like workflow execution
    
    This function replicates the functionality of the original FRE frerun command,
    which creates and optionally submits run scripts for model experiments.
    
    :param platform: Target platform name (e.g., 'hera', 'gaea'), defaults to None
    :type platform: str
    :param experiment: Experiment name or path to experiment configuration, defaults to None  
    :type experiment: str
    :param target: Target type (prod, debug, etc.), defaults to None
    :type target: str
    :param submit: Whether to submit the workflow after setup, defaults to False
    :type submit: bool
    :param staging: Whether to enable output staging, defaults to False
    :type staging: bool
    """
    fre_logger.info(f"Initializing frerun for platform: {platform}, experiment: {experiment}, target: {target}")
    
    # Validate required parameters (similar to original frerun requirements)
    if not experiment:
        fre_logger.error("*FATAL*: At least one experiment name is needed")
        raise ValueError("Experiment name is required")
    
    if not platform:
        fre_logger.error("*FATAL*: Platform must be specified")
        raise ValueError("Platform is required")
    
    # Determine experiment type based on target
    experiment_type = _determine_experiment_type(target)
    
    # Initialize the FrerunDriver with the provided options
    fre_logger.info(f"Creating FrerunDriver for {platform}/{experiment}")
    driver = FrerunDriver(platform=platform, experiment=experiment, experiment_type=experiment_type)
    
    # Validate experiment and platform
    if not driver.validate_experiment():
        fre_logger.error("*FATAL*: Experiment validation failed")
        raise ValueError("Invalid experiment specification")
    
    if not driver.validate_platform():
        fre_logger.error("*FATAL*: Platform validation failed") 
        raise ValueError("Invalid platform specification")
    
    # Setup the workflow
    fre_logger.info("Setting up workflow directories and configuration")
    workflow_dir = driver.setup()
    fre_logger.info(f"Workflow directory prepared: {workflow_dir}")

    # Enable staging if specified
    if staging:
        driver.enable_staging()
        fre_logger.info("Output staging enabled")

    # Submit the workflow if specified
    if submit:
        driver.submit_workflow(workflow_dir)
        fre_logger.info(f"Workflow submitted from: {workflow_dir}")
    else:
        # Log the path to the created script (mimicking original frerun output)
        script_path = os.path.join(workflow_dir, 'scripts/run', os.path.basename(experiment))
        if os.path.exists(script_path):
            fre_logger.info(f"The runscript '{script_path}' is ready")
        else:
            fre_logger.info(f"Workflow setup complete. To submit, use --submit option")
    
    return True

def _determine_experiment_type(target):
    """
    Determine the experiment type based on the target parameter.
    This mimics the original frerun logic for experiment types.
    
    :param target: Target specification (prod, debug, etc.)
    :type target: str
    :return: Experiment type string
    :rtype: str
    """
    if not target:
        return "production"
    
    target_lower = target.lower()
    if 'debug' in target_lower:
        return "debug"
    elif 'regr' in target_lower or 'regression' in target_lower:
        return "regression"
    elif 'unique' in target_lower:
        return "unique"
    else:
        return "production"