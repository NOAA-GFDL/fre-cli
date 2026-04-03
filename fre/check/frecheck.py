''' fre check '''

import click

from .frecheckexample import check_test_function
from fre import log_and_raise

@click.group(help=click.style(" - check subcommands !!!NotImplemented!!!", fg=(162,91,232)))
def check_cli():
    ''' entry point to fre check click commands '''

@check_cli.command()
@click.option('--uppercase', '-u', is_flag=True, help = 'Print statement in uppercase.')
def function(uppercase):
    """ - Execute fre check test """
    check_test_function(uppercase)
    log_and_raise('fre check has not been implemented yet!', NotImplementedError)
