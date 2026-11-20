'''
entry point for fre run subcommands
'''

import click

#from .frerunexample import run_test_function
from . import output_stager

@click.group(help=click.style(" - run subcommands", fg=(164,29,132)))
def run_cli():
    ''' entry point to fre run click commands '''

@run_cli.command()
@click.option('--uppercase', '-u', is_flag=True, help = 'Print statement in uppercase.')
def function(uppercase):
    """ - Execute fre run test """
    run_test_function(uppercase)
    raise NotImplementedError('fre run has not been implemented yet!')

run_cli.add_command(output_stager.outputStager, name="stage")
