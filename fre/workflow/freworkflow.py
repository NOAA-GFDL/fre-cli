''' fre workflow '''
import os
import click
import logging
fre_logger = logging.getLogger(__name__)

#fre tools
#from . import checkout_script
from . import install_script
#from . import run_script

@click.group(help=click.style(" - workflow subcommands", fg=(57,139,210)))
def workflow_cli():
    ''' entry point to fre workflow click commands '''

@workflow_cli.command()
@click.option("-e", "--experiment",
              type=str,
              required=True,
              help="Experiment name")
@click.option("--src-dir",
              type=str,
              envvar="TMPDIR",
              default=os.path.expanduser("~/.fre"),
              required=True,
              help="Path to cylc-src directory")
@click.option("--target-dir",
              type=str,
              help="""Target directory to install the cylc
                      workflow into. Default location is
                      ~/cylc-run/<workflow name>""")
@click.option("--force-install",
              type=bool,
              help="If cylc-run/[workflow_name] exists")
def install(experiment, src_dir, target_dir):
    """
    Install workflow configuration
    """
    install_script.workflow_install(experiment, src_dir, target_dir)
