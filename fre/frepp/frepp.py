#!/usr/bin/python3
## \date 2023
## \author Bennett Chang
## \description Script for frepp is used to post process outputs obtained from other fre commands.

import click

from fre.frepp.configureScript import *
from fre.frepp.checkoutScript import *

#############################################

@click.group()
def pp():
    pass

#############################################

@pp.command()
@click.option("-y", 
              type=str, 
              help="YAML file to be used for parsing", 
              required=True)
@click.pass_context
def configure(context, y):
    """
    # Takes a YAML file, parses it, and creates an output
    """
    context.forward(yamlInfo)

#############################################

@pp.command()
@click.option("-e",
              "--experiment", 
              type=str, 
              help="Experiment name", 
              required=True)
@click.option("-p",
              "--platform",
              type=str, 
              help="Platform name", 
              required=True)
@click.option("-t",
              "--target", 
              type=str, 
              help="Target name", 
              required=True)
@click.pass_context
def checkout(context, experiment, platform, target):
    """
    # Checkout the template file
    """
    context.forward(checkoutTemplate)

#############################################

if __name__ == "__main__":
    pp()
