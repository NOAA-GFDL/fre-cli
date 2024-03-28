#!/usr/bin/python3
## \date 2023
## \author Tom Robinson
## \author Dana Singh
## \author Bennett Chang
## \description Script for fremake is used to create and run a code checkout script and compile a model.

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

@click.command()
def fre_make_function(yamlfile, platform, target, force_checkout, force_compile, keep_compiled, no_link, execute, parallel, jobs, no_parallel_checkout, submit, verbose, walltime, mail_list):
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
    fre_make_function()
