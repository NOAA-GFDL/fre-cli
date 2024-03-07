#!/usr/bin/python3
## \date 2023
## \author Tom Robinson
## \author Dana Singh
## \author Bennett Chang
## \description Script for fremake is used to create and run a code checkout script and compile a model.

from fre.fremake.checkout import *
#from fre.fremake.makefile import *
#from fre.fremake.compile import *
#from fre.fremake.dockerfile import *

# import subprocess
# import os
# import yaml
# import argparse
# import logging
# import targetfre
# import varsfre
# import yamlfre
# import checkout
# import makefilefre
# import buildDocker
# import buildBaremetal
# from multiprocessing.dummy import Pool
import click

@click.group()
def make():
    pass

@make.command()
@click.option("-y", 
              "--yamlfile", 
              type=str, 
              help="Experiment yaml compile FILE", 
              required=True) # used click.option() instead of click.argument() because we want to have help statements
@click.option("-p", 
              "--platform", 
              multiple=True, #replaces nargs=-1 since we are using click.option() instead of click.argument()
              type=str, 
              help="Hardware and software FRE platform space separated list of STRING(s). This sets platform-specific data and instructions", required=True)
@click.option("-t", "--target", 
              multiple=True, #replaces nargs=-1 since we are using click.option() instead of click.argument()
              type=str, 
              help="FRE target space separated list of STRING(s) that defines compilation settings and linkage directives for experiments. Predefined targets refer to groups of directives that exist in the mkmf template file (referenced in buildDocker.py). Possible predefined targets include 'prod', 'openmp', 'repro', 'debug, 'hdf5'; however 'prod', 'repro', and 'debug' are mutually exclusive (cannot not use more than one of these in the target list). Any number of targets can be used.", 
              required=True)
@click.option("-f", 
              "--force-checkout", 
              is_flag=True, 
              help="Force checkout to get a fresh checkout to source directory in case the source directory exists")
@click.option("-F", 
              "--force-compile", 
              is_flag=True, 
              help="Force compile to compile a fresh executable in case the executable directory exists")
@click.option("-K", 
              "--keep-compiled", 
              is_flag=True, 
              help="Keep compiled files in the executable directory for future use")
@click.option("--no-link", 
              is_flag=True, 
              help="Do not link the executable")
@click.option("-E", 
              "--execute", 
              is_flag=True, 
              help="Execute all the created scripts in the current session")
@click.option("-n", 
              "--parallel", 
              type=int,
              metavar='', 
              default=1, 
              help="Number of concurrent model compiles (default 1)")
@click.option("-j", 
              "--jobs", 
              type=int, 
              metavar='',
              default=4, 
              help="Number of jobs to run simultaneously. Used for make -jJOBS and git clone recursive --jobs=JOBS")
@click.option("-npc", 
              "--no-parallel-checkout", 
              is_flag=True, 
              help="Use this option if you do not want a parallel checkout. The default is to have parallel checkouts.")
@click.option("-s", 
              "--submit", 
              is_flag=True, 
              help="Submit all the created scripts as batch jobs")
@click.option("-v", 
              "--verbose", 
              is_flag=True, 
              help="Get verbose messages (repeat the option to increase verbosity level)")
@click.option("-w", 
              "--walltime", 
              type=int, 
              metavar='', 
              help="Maximum wall time NUM (in minutes) to use")
@click.option("--mail-list", 
              type=str, 
              help="Email the comma-separated STRING list of emails rather than $USER@noaa.gov")
@click.pass_context
def fremakeFun(context,yamlfile, platform, target, force_checkout, force_compile, keep_compiled, no_link, execute, parallel, jobs, no_parallel_checkout, submit, verbose, walltime, mail_list):
    """
    Fremake is used to create a code checkout script to compile models for FRE experiments.
    """
   
    # Define variables  
    yml = yamlfile
    ps = platform
    ts = target
    nparallel = parallel
    jobs = str(jobs)
    pcheck = no_parallel_checkout

    if pcheck:
        pc = ""
    else:
        pc = " &"

    if verbose:
      logging.basicCOnfig(level=logging.INFO)
    else:
      logging.basicConfig(level=logging.ERROR)

    srcDir="src"
    checkoutScriptName = "checkout.sh"
    baremetalRun = False # This is needed if there are no bare metal runs

    ## Split and store the platforms and targets in a list
    plist = platform
    tlist = target

    ## Get the variables in the model yaml
    freVars = varsfre.frevars(yml)

    ## Open the yaml file and parse as fremakeYaml
    modelYaml = yamlfre.freyaml(yml,freVars)
    fremakeYaml = modelYaml.getCompileYaml()
    return modelYaml, fremakeYaml

###############################################################

@make.command()
@click.pass_context
def cc(context,yamlfile,platform,target,no_parallel_checkout,jobs,verbose):
    """ - Create fremake checkout script. """
    #fremake()
    context.forward(checkout_create)

###############################################################
@make.command()
@click.pass_context
def rc(context,yamlfile,platform,target,no_parallel_checkout,jobs,verbose):
    """ - Run created fremake checkout script. """
    #fremake()
    context.forward(checkout_run)

###############################################################
@make.command()
@click.pass_context
def mc(context, yamlfile, platform, jobs, npc):
    """ - Write fremake makefile script. """
    #fremake()
    context.forward(makefile_create)

###############################################################
@make.command()
@click.pass_context
def compc(context,yamlfile,platform,target,jobs):
    """ - Write compile script """
    #fremake()
    context.forward(compile_create)

###############################################################
@make.command()
@click.pass_context
def compr(context,yamlfile,platform,target,jobs):
    """ Run compile script """
    #fremake()
    context.forward(compile_run)

###############################################################

@make.command()
@click.pass_context
def dc(context,yamlfile,platform,target):
    """ - Writes the dockerfile """
    #fremake()
    context.forward(dockerfile_create)

###############################################################

@make.command()
@click.pass_context
def dr(context,yamlfile,platform,target):
    """ - Runs the dockerfile """
    #fremake()
    context.forward(dockerfile_run)

###############################################################
if __name__ == "__main__":
    make()
