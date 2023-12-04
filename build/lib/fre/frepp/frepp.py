#!/usr/bin/python3
## \date 2023
## \author Bennett Chang
## \description Script for frepp is used to post process outputs obtained from other fre commands.

import os
from pathlib import Path
import yaml
import click
from jsonschema import validate, ValidationError, SchemaError
import json
import click

from multiprocessing.dummy import Pool

from fre.frepp.config import *

@click.group()
def pp():
    pass

@pp.command()
@click.option("--yaml", 
              "-y", 
              type=str, 
              is_Flag=True, 
              help="YAML file to be used for parsing", 
              required=True)
@click.pass_context
def configure(context, yaml):
    """
    # Insert fre pp configure here
    """
    context.forward(yamlInfo)    

if __name__ == "__main__":
    pp()