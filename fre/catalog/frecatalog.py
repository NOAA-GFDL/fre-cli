#!/usr/bin/python3
## \date 2024
## \author Bennett Chang
## \description Integration of CatalogBuilder to build a data catalog which can then be ingested in climate analysis scripts/workflow

import click

from fre.catalog.get_intake_gfdl import *

@click.group()
def catalog():
    pass

@catalog.command()
@click.option('-i',
              '--input_path', 
              required=True, 
              nargs=1) 
@click.option('-o',
              '--output_path', 
              required=True, 
              nargs=1)
@click.option('--filter_realm', 
              nargs=1)
@click.option('--filter_freq', 
              nargs=1)
@click.option('--filter_chunk', 
              nargs=1)
@click.option('--overwrite', 
              is_flag=True, 
              default=False)
@click.option('--append', 
              is_flag=True, 
              default=False)
@click.pass_context
def buildCatalog(context, input_path, output_path, filter_realm, filter_freq, filter_chunk, overwrite, append):
    """ - Execute fre catalog build """
    context.forward(build)

if __name__ == "__main__":
    catalog()
