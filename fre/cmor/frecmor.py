''' please use NOAA-GFDL/fremor '''

import click

from .cmor_mixer import cmor_run_subtool
from .cmor_yamler import cmor_yaml_subtool
from .cmor_config import cmor_config_subtool
from .cmor_finder import make_simple_varlist, cmor_find_subtool

@click.group(help=click.style(" - please use NOAA-GFDL/fremor", fg=(232,91,204)))
def cmor_cli():
    ''' please use NOAA-GFDL/fremor '''


@cmor_cli.command()
def yaml():
    """
    PLACEHOLDER STUB
    """
    cmor_yaml_subtool()


@cmor_cli.command()
def find():
    '''
    PLACEHOLDER STUB
    '''
    cmor_find_subtool()


@cmor_cli.command()
def run():
    """
    PLACEHOLDER STUB
    """
    cmor_run_subtool()


@cmor_cli.command()
def varlist():
    """
    PLACEHOLDER STUB
    """
    make_simple_varlist()


@cmor_cli.command()
def config():
    """
    PLACEHOLDER STUB
    """
    cmor_config_subtool()
