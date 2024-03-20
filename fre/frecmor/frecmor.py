#!/usr/bin/python3
## \date 2023
## \author Chris Blanton
## \description Script for frepp is used to post process outputs obtained from other fre commands.

import click

from fre.frecmor.CMORmixer import *

#############################################

@click.group()
def cmor():
    pass

#############################################

@cmor.command()
@click.pass_context
def runFunction(context, indir, outdir, varlist, table_config, exp_config):
    context.forward(run_subtool)

#############################################=

if __name__ == "__main__":
    cmor()
