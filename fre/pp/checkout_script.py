'''
Description: Checkout script which accounts for 4 different scenarios:
1. branch not given, folder does not exist,
2. branch given, folder does not exist,
3. branch not given, folder exists,
4. branch given and folder exists
'''
import os
import subprocess

import logging
fre_logger = logging.getLogger(__name__)

from . import make_workflow_name

from ..fre import version as fre_ver

FRE_WORKFLOWS_URL = 'https://github.com/NOAA-GFDL/fre-workflows.git'

def checkout_template(experiment = None, platform = None, target = None, branch = None):
    """
    Create a directory and checkout the workflow template files from the repo

    :param experiment: One of the postprocessing experiment names from the yaml displayed by fre list exps -y $yamlfile (e.g. c96L65_am5f4b4r0_amip), default None
    :type experiment: str
    :param platform: The location + compiler that was used to run the model (e.g. gfdl.ncrc5-deploy), default None
    :type platform: str
    :param target: Options used for the model compiler (e.g. prod-openmp), default None
    :type target: str
    :param branch: which git branch to pull from, default None
    :type branch: str
    :raises OSError: why checkout script was not able to be created
    :raises ValueError: 
        -if experiment or platform or target is None
        -if branch argument cannot be found as a branch or tag
    """

    ## Chdir back to here before we exit this routine
    go_back_here = os.getcwd()

    # branch and version parameters
    default_tag = fre_ver #fre.version
    git_clone_branch_arg = branch if branch is not None else default_tag
    if branch is None:
        fre_logger.info(f"default tag is '{default_tag}'")
    else:
        fre_logger.info(f"requested branch/tag is '{branch}'")

    # check args + set the name of the directory
    if None in [experiment, platform, target]:
        os.chdir(go_back_here)
        raise ValueError( 'one of these are None: experiment / platform / target = \n'
                         f'{experiment} / {platform} / {target}' )
    #name = f"{experiment}__{platform}__{target}"
    workflow_name = make_workflow_name(experiment, platform, target)

    # Create the directory if it doesn't exist
    directory = os.path.expanduser("~/cylc-src")
    try:
        os.makedirs(directory, exist_ok = True)
    except Exception as exc:
        raise OSError(
            '(checkoutScript) directory {directory} wasnt able to be created. exit!') from exc
    finally:
        os.chdir(go_back_here)

    checkout_exists = os.path.isdir(f'{directory}/{workflow_name}')

    if not checkout_exists: # scenarios 1+2, checkout doesn't exist, branch specified (or not)
        fre_logger.info('checkout does not yet exist; will create now')
        clone_output = subprocess.run( ['git', 'clone','--recursive',
                                        f'--branch={git_clone_branch_arg}',
                                        FRE_WORKFLOWS_URL, f'{directory}/{workflow_name}'],
                                       capture_output = True, text = True, check = True)
        fre_logger.info(f'{clone_output}')

    else:     # the repo checkout does exist, scenarios 3 and 4.
        os.chdir(f'{directory}/{workflow_name}')

        # capture the branch and tag
        # if either match git_clone_branch_arg, then success. otherwise, fail.

        current_tag = subprocess.run(["git","describe","--tags"],
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
            raise ValueError('neither tag nor branch matches the git clone branch arg') #exit(1)

    # make sure we are back where we should be
    if os.getcwd() != go_back_here:
        os.chdir(go_back_here)


#############################################

if __name__ == '__main__':
    checkout_template()
