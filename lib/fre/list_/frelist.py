''' fre lister '''

#import logging
#fre_logger = logging.getLogger(__name__)

import click
from fre.list_ import list_experiments_script
from fre.list_ import list_platforms_script

@click.group(help=click.style(" - list subcommands", fg=(232,204,91)))
def list_cli():
    ''' entry point to fre list click commands '''

@list_cli.command()
@click.option("-y",
              "--yamlfile",
              type=str,
              help="YAML file to be used for parsing",
              required=True)
def exps(yamlfile):
    """ - List experiments  available"""
    list_experiments_script.list_experiments_subtool(yamlfile)

@list_cli.command()
@click.option("-y",
              "--yamlfile",
              type=str,
              help="YAML file to be used for parsing",
              required=True)
def platforms(yamlfile):
    """ - List platforms available """
    list_platforms_script.list_platforms_subtool(yamlfile)

if __name__ == "__main__":
    list_cli()
