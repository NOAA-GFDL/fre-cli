'''
Description: Checkout script which accounts for 4 different scenarios:
    default repo: 
        default branch:
            checkout folder does not exist
            checkout folder exists
            checkout folder exists, --force-update set to True
        non-default branch:
            ... (same 3 combos)
    non-default repo
        ... (same 6 combos)
Non-default repo in combination with default branch is likely to give you 
an error, but that's arguably a user problem
'''
import os
import subprocess
improt re

import logging
fre_logger = logging.getLogger(__name__)

from ..fre import version as fre_ver

FRE_WORKFLOWS_URL = 'https://github.com/NOAA-GFDL/fre-workflows.git'

def checkout_template(experiment = None, platform = None, target = None, 
                      branch = None, repo = None, force_update = False):
    """
    Checkout the workflow template files from the repo
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
        
    #repo parameters:
    if repo is None:
        repo = FRE_WORKFLOWS_URL
        fre_logger.info(f"default repo is '{FRE_WORKFLOWS_URL}'")
    else:
        regex = ".*github.com/NOAA-GFDL/.*\.git"
        if re.match(regex, repo) is None:
            fre_logger.error(f"error in checkout_template: repo {repo} is not under github.com/NOAA-GFDL!")

    # check args + set the name of the directory
    if None in [experiment, platform, target]:
        os.chdir(go_back_here)
        raise ValueError( 'one or more of these are not set: experiment / platform / target = \n'
                         f'{experiment} / {platform} / {target}' )
    name = f"{experiment}__{platform}__{target}"

    # Create the directory if it doesn't exist
    directory = os.path.expanduser("~/cylc-src")
    try:
        os.makedirs(directory, exist_ok = True)
    except Exception as exc:
        raise OSError(
            '(checkoutScript) directory {directory} wasnt able to be created. exit!') from exc
    finally:
        os.chdir(go_back_here)
    
    clonedir = f'{directory}/{name}'
    checkout_exists = os.path.isdir(clonedir)

    if not checkout_exists: #checkout doesn't exist
        fre_logger.info('checkout does not yet exist; will create now')
        clone_fre_workflows(clonedir, repo, git_clone_branch_arg)

    else:                  #checkout does exist
        os.chdir(f'{directory}/{name}')

        # capture the branch and tag
        # if either match git_clone_branch_arg, then success. otherwise, fail.

        current_tag = subprocess.run(["git -C $directory","describe","--tags"],
                                     capture_output = True,
                                     text = True, check = True).stdout.strip()
        current_branch = subprocess.run(["git", "branch", "--show-current"],
                                         capture_output = True,
                                         text = True, check = True).stdout.strip()
                                         
        #TODO: this also needs a check to make sure that the repo is the same. 

        if current_tag == git_clone_branch_arg or current_branch == git_clone_branch_arg:
            fre_logger.info(f"checkout exists ('{directory}/{name}'), and matches '{git_clone_branch_arg}'")
            if force_update:
                fre_logger.info(
                    f"Forcing an update of the branch {branch} from repo {repo}")
                update_fre_workflows(clonedir, repo, git_clone_branch_arg)
        else:
            fre_logger.info(
                f"ERROR: experiment checkout exists ('{directory}/{name}') and does not match '{git_clone_branch_arg}'")
            fre_logger.info(
                f"ERROR: current branch is '{current_branch}', current tag-describe is '{current_tag}'")
            fre_logger.info(
                f"You can fix this by running your config with a new experiment name (-e) or using --force-update")
            os.chdir(go_back_here)
            raise ValueError('neither tag nor branch matches the git clone branch arg')

    # make sure we are back where we should be
    if os.getcwd() != go_back_here:
        os.chdir(go_back_here)
        
def clone_fre_workflows(clone_loc, repo, branch, limit_checkout_size=False):
    '''
    Clones fre-workflows into a location $clone_loc from $repo and $branch. 
    '''
    git_command = f"git clone --recursive --branch {branch}}"
    if limit_checkout_size:
        git_command += " --depth 1 --shallow-submodules --filter=blob:none --no-tags"
    git_command += f" {repo} {clone_loc}"
    fre_logger.info(git_command)
    clone_output = subprocess.run(git_command.split(" "), 
                                  capture_output=True, text=True, check=True)
    fre_logger.info(f'{clone_output}')
    
def update_fre_workflows(clone_loc, repo, branch):
    '''
    Does a git pull of the current branch from the repo; needed if the code
    is going to update (i.e. if you're testing a bugfix)
    git -C does a pushd and popd internal ot the git command
    '''
    git_command = f"git -C {clone_loc} pull"


#############################################

if __name__ == '__main__':
    checkout_template()
