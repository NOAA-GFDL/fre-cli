#!/usr/bin/python3
## \date 2024
## \author Bennett Chang
## \description 

import os
from pathlib import Path
import yaml
import click

from fre.yamltools.yamltoolsfile import *

@click.group()
def yamltools():
    pass 

@yamltools.command()
@click.option('--uppercase', '-u', is_flag=True, help = 'Print statement in uppercase.')
@click.pass_context
def testfunction(context, uppercase):
    """ - Execute fre yamltools function """
    context.forward(function)

if __name__ == "__main__":
    test()
