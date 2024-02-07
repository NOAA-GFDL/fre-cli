#!/usr/bin/python3
## \date 2023
## \author Bennett Chang
## \description Script for frepp is used to post process outputs obtained from other fre commands.

# import os
# from pathlib import Path
# import yaml
# import click
# from jsonschema import validate, ValidationError, SchemaError
# import json
import click

from multiprocessing.dummy import Pool

from fre.fretest.testfile import *

@click.group()
def test():
    pass 

@test.command()
@click.option('--uppercase', '-u', is_flag=True, help = 'Print statement in uppercase.')
@click.pass_context
def testfunction(context, uppercase):
    """ - Execute fre test function """
    context.forward(function)

if __name__ == "__main__":
    test()
