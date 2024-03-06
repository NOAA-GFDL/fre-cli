#!/usr/bin/python3
## \date 2024
## \author Bennett Chang
## \description Integration of CatalogBuilder to build a data catalog which can then be ingested in climate analysis scripts/workflow

import click

from scripts import gen_intake_gfdl

@click.group()
def catalog():
    pass

#@click.pass_context
#def buildCatalog(context, input_path, output_path, filter_realm, filter_freq, filter_chunk, overwrite, append):
#    """ - Execute fre catalog build """
#    context.forward(build)

@catalog.command()
@click.option('-i',
              '--input_path',
              required=False,
              nargs=1,
              help="The directory path with the datasets to be cataloged. e.g. a GFDL PP path till /pp")
@click.option('-o',
              '--output_path',
              required=False,
              nargs=1,
              help="Specify output filename suffix only. e.g. 'catalog'")
@click.option('-c',
              '--config',
              required=False,
              type=click.Path(exists=True),
              nargs=1,
              help="Path to your yaml configuration, use the config_template in intakebuilder repo")
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
#@click.pass_context
def buildCatalog(input_path=None, output_path=None, config=None, filter_realm=None, filter_freq=None, filter_chunk=None, overwrite=False, append=False):
    """
    - Execute CatalogBuilder gen_intake_gfdl build script
    """
    # context.forward(gen_intake_gfdl.main)
    # not sure if we need this ^, but if so, we need to add context argument
    gen_intake_gfdl.main() # this seems to work, even defaulting name to None, but it doesn't seem to recognize any arguments provided

if __name__ == "__main__":
    catalog()                                                                                                                                                      
