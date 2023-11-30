#!/usr/bin/python3
## \date 2023
## \author Tom Robinson
## \author Dana Singh
## \author Bennett Chang
## \description fremake is used to create and run a code checkout script and compile a model.

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
def fremake(yamlfile, platform, target, force_checkout, force_compile, keep_compiled, no_link, execute, parallel, jobs, no_parallel_checkout, submit, verbose, walltime, mail_list):
    """
    Fremake is used to create a code checkout script to compile models for FRE experiments.
    """
    
    # Insert Actual Code
    
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

    print("End of function")
    print(yml)
    print(ps)
    print(ts)

if __name__ == "__main__":
    make()