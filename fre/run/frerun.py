'''
entry point for fre run subcommands
'''
d
import click

#from .frerunexample import run_test_function
from . import output_stager

@catalog_cli.command()
@click.group(help=click.style(" - run subcommands", fg=(164,29,132)))
def run_cli():
    ''' entry point to fre run click commands '''

@run_cli.command()
@click.option('--uppercase', '-u', is_flag=True, help = 'Print statement in uppercase.')
def function(uppercase):
    """ - Execute fre run test """
    run_test_function(uppercase)
    raise NotImplementedError('fre run has not been implemented yet!')

@run_cli.command()
@click.option("--check", is_flag=True, default=False, required=False,
    help="Enable the check step to verify output files.")
@click.option("--fill-grid", is_flag=True, default=False, required=False,
    help="Enable the fill-grid step.")
@click.option("--checksum", is_flag=True, default=False, required=False,
    help="Enable checksum verification of output files.")
@click.option("--compress", is_flag=True, default=False, required=False,
    help="Enable compression of output files.")
@click.option("--mode", required=True,
    type=click.Choice(['history', 'ascii', 'restart'], case_sensitive=False),
    help="Mode for staging (required). Must be one of: history, ascii, restart.")
@click.option("--verbose", is_flag=True, default=False, required=False,
    help="Enable verbose output.")
@click.argument("exp_name")
@click.argument("output_type")
@click.argument("work_dir")
@click.argument("ptmp_dir")
@click.argument("arch_dir")
@click.pass_context
def stager(check, fill_grid,  # pylint: disable=invalid-name
                 checksum, compress, mode, verbose, exp_name,
                 output_type, work_dir, ptmp_dir, arch_dir):
    """Stage output files for post-processing."""
    context.forward(output_stager.outputStager)
    
