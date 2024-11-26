'''
Description: Checkout script which accounts for 4 different scenarios: 1. branch not given, folder does not exist,
2. branch given, folder does not exist, 3. branch not given, folder exists, 4. branch given and folder exists
'''
import os
import sys
import subprocess

import click

from fre import fre

FRE_WORKFLOWS_URL = 'https://github.com/NOAA-GFDL/fre-workflows.git'

def checkout_template(experiment = None, platform = None, target = None, branch = None):
    """
    Checkout the workflow template files from the repo
    """
    ## Chdir back to here before we exit this routine
    go_back_here = os.getcwd()

    # branch and version parameters
    #default_tag = subprocess.run( ["fre","--version"],
    #                              capture_output = True, text = True, check = True).stdout.split()[2]
    default_tag = fre.__version__
    print(f'(checkout_script) default_tag is {default_tag}')


    # check args + set the name of the directory
    if None in [experiment, platform, target]:
        raise ValueError( 'one of these are None: experiment / platform / target = \n'
                         f'{experiment} / {platform} / {target}' )
    name = f"{experiment}__{platform}__{target}"

    # Create the directory if it doesn't exist
    directory = os.path.expanduser("~/cylc-src")
    try:
        os.makedirs(directory, exist_ok = True)
    except Exception as exc:
        raise OSError('(checkoutScript) directory {directory} wasnt able to be created. exit!') from exc

    print(f'(checkout_script) branch is {branch}')
    checkout_exists = os.path.isdir(f'{directory}/{name}')
    git_clone_branch_arg = branch if branch is not None else default_tag
    if branch is not None:
        print(f'(checkout_script) WARNING using default_tag as branch argument for git clone!')


    if not checkout_exists:     # scenarios 1 and 2, repo checkout doesn't exist, branch specified (or not)
        clone_output = subprocess.run(['git', 'clone','--recursive',
                                       f'--branch={git_clone_branch_arg}',
                                       FRE_WORKFLOWS_URL, f'{directory}/{name}'],
                                      capture_output = True, text = True, check = True)
        print(f'(checkout_script) output git clone command: {clone_output}')

    else:     # the repo checkout does exist, scenarios 3 and 4.
        os.chdir(f'{directory}/{name}')
        
        name_path_tag_subproc_out = subprocess.run(["git","describe","--tags"],capture_output = True, text = True, check = True).stdout
        if branch is not None:
            name_path_tag = name_path_tag_subproc_out.split('*')
            name_path_branch = subprocess.run(["git","branch"],capture_output = True, text = True,check = True).stdout.split()[0]
            if all( [ default_tag not in name_path_tag,
                      name_path_branch != branch ] ):
                sys.exit(
                    f"Tag and branch of prexisting directory {directory}/{name} does not match fre --version or branch requested")
        else:
            name_path_tag = name_path_tag_subproc_out.split()[0]
            if not default_tag in name_path_tag:
                    sys.exit(
                        f"Tag of prexisting directory {directory}/{name} does not match fre --version")

    # make sure we are back where we should be
    if os.getcwd() != go_back_here:
        os.chdir(go_back_here)
            
    return 0

#############################################

@click.command()
def _checkout_template(experiment, platform, target, branch = None):
    '''
    Wrapper script for calling checkout_template - allows the decorated version
    of the function to be separate from the undecorated version
    '''
    return checkout_template(experiment, platform, target, branch)


if __name__ == '__main__':
    checkout_template()
