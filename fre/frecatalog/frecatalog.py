#!/usr/bin/python3
## \date 2024
## \author Bennett Chang
## \description Integration of CatalogBuilder to build a data catalog which can then be ingested in climate analysis scripts/workflow

import os
from pathlib import Path
import yaml
import click

from fre.frecatalog.catalogfile import *

@click.group()
def catalog():
    pass 

@catalog.command()
@click.option('--uppercase', '-u', is_flag=True, help = 'Print statement in uppercase.')
@click.pass_context
def testfunction(context, uppercase):
    """ - Execute fre catalog function """
    context.forward(function)

if __name__ == "__main__":
    test()
