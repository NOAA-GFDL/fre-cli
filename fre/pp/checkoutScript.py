#!/usr/bin/env python

# Author: Bennett Chang
# Description: 

import os
import sys
from pathlib import Path
import subprocess
from subprocess import PIPE
from subprocess import STDOUT
import click
import re

#############################################

package_dir = os.path.dirname(os.path.abspath(__file__))

#############################################

def _checkoutTemplate(experiment, platform, target, branch='main'):
    """
    Checkout the workflow template files from the repo
    """
    remote = "https://gitlab.gfdl.noaa.gov/fre2/workflows/postprocessing.git"
    src_dir = make_src_dir(experiment, platform, target)
	if not os.path.exists(src_dir):
		clone_from_remote(src_dir, branch, remote)
	else:
		check_preexist_match(src_dir, branch, remote)
	return 0


#############################################
def make_src_dir(experiment, platform, target):
	'''
	Makes official location of cylc-src dir.
	Separating into a function because we might check out to a temporary dir - 
	and currently it's hard-coded in a couple functions to ~/cylc-src 
	'''
	name = f"{experiment}__{platform}__{target}"
	src_root = os.path.join(os.path.expanduser("~/cylc-src"), name)
	return(src_root)
	
def check_preexist_match(src_dir, branch, remote):
	os.chdir(src_dir)
	git_branch_cmd = "git branch --show-current"
	#If it exits with an error, odds are it isn't a git repo - advise re-checking out
	if git_branch != branch:
		stop("Error in wrapperscript: checking out a branch '{branch}' that does not match existing branch '{git_branch}' in {src_dir}!")
	else:
		git_loc_commit_cmd = "git log | head -n 1 | cut -d ' ' -f 2"
		git_rem_commit_cmd = """
		                     git remote add origin {remote_repo};
		                     git fetch
		                     git log origin/{branch} | head -n 1 | cut -d ' ' -f 2
		                     """
		 if git_loc_commit != git_rem_commit:
		 	stop("Error in check_preexist: git repo located at {src_dir} has a latest commit in {branch} that does not match the remote! Please resolve or remove and re-clone the dir at {src_dir}"

def clone_from_remote(src_dir, branch, remote):
    click.echo("cloning experiment into directory " + directory + "/" + name)
    clonecmd = f"git clone -b {branch} --single-branch --depth=1 --recursive https://gitlab.gfdl.noaa.gov/fre2/workflows/postprocessing.git {name}"
    preexist_error = f"fatal: destination path '{name}' already exists and is not an empty directory."
    cloneproc = subprocess.run(clonecmd, shell=True, check=False, stdout=PIPE, stderr=STDOUT)
    if not cloneproc.returncode == 0:
        if re.search(preexist_error.encode('ASCII'),cloneproc.stdout) is not None:
            argstring = f" -e {experiment} -p {platform} -t {target}"
            stop_report = "\n".join([f"Error in checkoutTemplate: the workflow definition specified by -e/-p/-t already exists at the location ~/cylc-src/{name}!",
                                     "Please delete workflow dir and clone again.". 
                                     "Copy/paste commands:",
                                     "\t cylc clean {name}",
                                     "\t rm -r ~/cylc-src/{name}", 
                                     "\t rm -r ~/cylc-run/{name}"])
            sys.exit(stop_report)
            return 1
        else:
            #if not identified, just print the error
            click.echo(clonecmd)
            click.echo(cloneproc.stdout)
            return 1
#############################################

@click.command()
def checkoutTemplate(experiment, platform, target, branch="main"):
    '''
    Wrapper script for calling checkoutTemplate - allows the decorated version
    of the function to be separate from the undecorated version
    '''
    return _checkoutTemplate(experiment, platform, target, branch="main")
                            

if __name__ == '__main__':
    checkoutTemplate()
