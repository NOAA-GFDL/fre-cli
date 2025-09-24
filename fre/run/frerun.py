'''
entry point for fre run subcommands
'''

import click
from .run_script import run_test_function, run_script_subtool

@click.group(help=click.style(" - run subcommands !!!NotImplemented!!!", fg=(164,29,132)))
def run_cli():
    ''' entry point to fre run click commands '''

@run_cli.command()
@click.option('--uppercase', '-u', is_flag=True, help = 'Print statement in uppercase.')
def function(uppercase):
    """ - Execute fre run test """
    run_test_function(uppercase)
    raise NotImplementedError('fre run has not been implemented yet!')

@run_cli.command()
@click.option('--platform', '-p', type=str, help='Target platform name')
@click.option('--experiment', '-x', type=str, help='Experiment name or path to experiment configuration')
@click.option('--target', '-t', type=str, default='prod', help='Target type (prod, debug, etc.)')
@click.option('--submit', is_flag=True, help='Submit the workflow after setup')
@click.option('--staging', is_flag=True, help='Enable output staging')
def run(platform, experiment, target, submit, staging):
    """ - Execute fre run workflow """
    run_script_subtool(platform=platform, experiment=experiment, target=target, submit=submit, staging=staging)
