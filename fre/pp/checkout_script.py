"""
Workflow Template Checkout Utility for FRE Post-Processing (fre pp).

The checkout_script module manages the automated cloning and validation of post-processing Cylc
workflow templates from the official NOAA-GFDL workflows Git repository into the
local user's Cylc source directory (`~/cylc-src`).

It supports four operational scenarios:
1. **Branch omitted, directory does not exist**: Clones the workflow template using the current `fre` package version tag.
2. **Branch provided, directory does not exist**: Clones the workflow template using the specified branch or tag.
3. **Branch omitted, directory exists**: Validates that the existing directory matches the default `fre` package version tag.
4. **Branch provided, directory exists**: Validates that the existing directory matches the user-specified branch or tag.
"""
import logging
import os
import subprocess

from . import make_workflow_name
from ..fre import version as fre_ver

fre_logger = logging.getLogger(__name__)

FRE_WORKFLOWS_URL = 'https://github.com/NOAA-GFDL/fre-workflows.git'

def checkout_template(experiment = None, platform = None, target = None, branch = None):
    """
    Check out workflow template files from https://github.com/NOAA-GFDL/fre-workflows.git 
    into the default ~/cylc-src path.

    Constructs a standardized workflow name from the given experiment, platform, and target settings,
    ensures ~/cylc-src exists, and either clones the `fre-workflows`
    repository or verifies that an existing checkout matches the specified Git branch/tag version.

    :param experiment: Experiment name as listed in the model YAML file
                       (e.g., ``'c96L65_am5f4b4r0_amip'``). Must not be None.
    :type experiment: str, optional
    :param platform: FRE platform defined in the platforms yaml
                     If on gaea c5, a FRE platform may look like ncrc5.intel23-classic
    :type platform: str, optional
    :param target: Predefined FRE targets; options include [prod/debug/repro]-openmp
    :type target: str, optional
    :param branch: Git branch or tag name to checkout. If None, defaults to the installed `fre` package version.
    :type branch: str, optional

    :return: None
    :rtype: None

    :raises ValueError: If any required arguments (``experiment``, ``platform``, or ``target``) are None,
                        or if an existing workflow directory does not match the expected branch/tag.
    :raises OSError: If the target output directory ``~/cylc-src`` cannot be created.
    :raises subprocess.CalledProcessError: If underlying Git operations (clone, tag describe, branch query) fail.
    """

    # Record original working directory to restore state upon completion or failure
    go_back_here = os.getcwd()

    # Determine fallback git tag based on fre package version
    default_tag = fre_ver
    git_clone_branch_arg = branch if branch is not None else default_tag
    if branch is None:
        fre_logger.info(f"default tag is '{default_tag}'")
    else:
        fre_logger.info(f"requested branch/tag is '{branch}'")

    # Validate mandatory parameters
    if None in [experiment, platform, target]:
        os.chdir(go_back_here)
        raise ValueError( 'one of these are None: experiment / platform / target = \n'
                         f'{experiment} / {platform} / {target}' )

    # Generate canonical workflow directory name
    workflow_name = make_workflow_name(experiment, platform, target)

    # Ensure Cylc source root directory (~/cylc-src) exists
    directory = os.path.expanduser("~/cylc-src")
    try:
        os.makedirs(directory, exist_ok = True)
    except Exception as exc:
        raise OSError(
            f"(checkoutScript) directory {directory} wasn't able to be created. exit!"
        ) from exc
    finally:
        os.chdir(go_back_here)

    checkout_exists = os.path.isdir(f'{directory}/{workflow_name}')

    if not checkout_exists:
        # Scenarios 1 & 2: Workflow directory does not exist yet; clone repository
        fre_logger.info('checkout does not yet exist; will create now')
        clone_output = subprocess.run( ['git', 'clone', '--recursive',
                                        f'--branch={git_clone_branch_arg}',
                                        FRE_WORKFLOWS_URL, f'{directory}/{workflow_name}'],
                                       capture_output = True, text = True, check = True)
        fre_logger.info(f'{clone_output}')

    else:
        # Scenarios 3 & 4: Workflow directory exists; verify branch/tag alignment
        os.chdir(f'{directory}/{workflow_name}')

        current_tag = subprocess.run(["git", "describe", "--tags"],
                                     capture_output = True, 
                                     text = True, check = True).stdout.strip()

        current_branch = subprocess.run(["git", "branch", "--show-current"],
                                         capture_output = True, 
                                         text = True, check = True).stdout.strip()

        if current_tag == git_clone_branch_arg or current_branch == git_clone_branch_arg:
            fre_logger.info(f"checkout exists ('{directory}/{workflow_name}'), and matches '{git_clone_branch_arg}'")
        else:
            fre_logger.info(
                f"ERROR: checkout exists ('{directory}/{workflow_name}') and does not match '{git_clone_branch_arg}'")
            fre_logger.info(
                f"ERROR: current branch is '{current_branch}', current tag-describe is '{current_tag}'")
            os.chdir(go_back_here)
            raise ValueError('neither tag nor branch matches the git clone branch arg')

    # Ensure working directory is restored to initial state
    if os.getcwd() != go_back_here:
        os.chdir(go_back_here)
