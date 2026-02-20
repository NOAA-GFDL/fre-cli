''' fre workflow '''
import os
import click
import logging
fre_logger = logging.getLogger(__name__)

#fre tools
from . import checkout_script
#from . import install_script
#from . import run_script

@click.group(help=click.style(" - workflow subcommands", fg=(57,139,210)))
def workflow_cli():
    ''' entry point to fre workflow click commands '''

@workflow_cli.command()
@click.option("-y", "--yamlfile", type=str,
              help="Model yaml file",
              required=True)
@click.option("-e", "--experiment", type=str,
              help="Experiment name",
              required=True)
@click.option("-a", "--application",
              type=click.Choice(['run', 'pp']),
              help="Type of workflow to check out/clone",
              required=True)
@click.option("--target-dir",
              type=str,
              envvar="TMPDIR",
              default=".fre",
              help=f"Target directory for workflow to be cloned into. Default location TMPDIR: {os.environ['TMPDIR']}")
@click.option("--force-checkout",
              is_flag=True,
              default=False,
              help="If the checkout already, exists, remove and check out again.")
def checkout(yamlfile, experiment, application, target_dir, force_checkout):
    """
    Checkout/extract fre workflow
    """
    checkout_script.workflow_checkout(yamlfile, experiment, application, target_dir, force_checkout)
