'''
entry point for fre run subcommands
'''

import click
from .run_script import run_test_function

@click.group(help=click.style(" - run subcommands !!!NotImplemented!!!", fg=(164,29,132)))
def run_cli():
    ''' entry point to fre run click commands '''

@run_cli.command()
@click.option('--uppercase', '-u', is_flag=True, help = 'Print statement in uppercase.')
def function(uppercase):
    """ - Execute fre run test """
    run_test_function(uppercase)
    raise NotImplementedError('fre run has not been implemented yet!')
