#!/usr/bin/python3
## \date 2023
## \author Bennett Chang
## \description

import click

#############################################

@click.group()
def yaml():
    pass

#############################################

@yaml.command()
@click.option("-y",
              type=str,
              help="YAML file to be used for parsing",
              required=True)
@click.pass_context
def diag-convert(context, y):
    """
    # Insert fre yaml diag-convert here
    """
    context.forward(diag-convertfunction)

#############################################

@yaml.command()
@click.option("-y",
              type=str,
              help="YAML file to be used for parsing",
              required=True)
@click.pass_context
def diag-combine(context, y):
    """
    # Insert fre yaml diag-combine here
    """
    context.forward(diag-combinefunction)

#############################################

@yaml.command()
@click.option("-y",
              type=str,
              help="YAML file to be used for parsing",
              required=True)
@click.pass_context
def field-convert(context, y):
    """
    # Insert fre yaml field-convert here
    """
    context.forward(field-convertfunction)

#############################################

if __name__ == "__main__":
    yaml()
