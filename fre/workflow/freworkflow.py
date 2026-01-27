''' fre workflow '''

import click
import logging
fre_logger = logging.getLogger(__name__)

#fre tools
from . import checkout_script
from . import install_script
from . import run_script

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
#@click.option("-p", "--platform", type=str,
#              help="Platform name")
#@click.option("-t", "--target", type=str,
#              help="Target name")
@click.option("-b", "--branch", type =str,
              required=False, default = None,
              help="fre-workflows branch/tag to clone; default is $(fre --version)")
@click.option("-a", "--application",
              type=click.Choice(['run', 'pp']),
              help="Use case for checked out workflow",
              required=True)
def checkout(yamlfile, experiment, application, branch=None):
    """
    Checkout/extract fre workflow
    """
    checkout_script.workflow_checkout(yamlfile, experiment, application, branch)

@workflow_cli.command()
@click.option("-e", "--experiment", type=str,
              help="Experiment name",
              required=True)
#@click.option("-p", "--platform", type=str,
#              help="Platform name",
#              required=True)
#@click.option("-t", "--target", type=str,
#              help="Target name",
#              required=True)
def install(experiment):
    """
    Install workflow configuration
    """
    install_script.workflow_install(experiment)

@workflow_cli.command()
@click.option("-e", "--experiment", type=str,
              help="Experiment name",
              required=True)
#@click.option("-p", "--platform", type=str,
#              help="Platform name",
#              required=True)
#@click.option("-t", "--target", type=str,
#              help="Target name",
#              required=True)
@click.option("--pause", is_flag=True, default=False,
              help="Pause the workflow immediately on start up",
              required=False)
@click.option("--no_wait", is_flag=True, default=False,
              help="after submission, do not wait to ping the scheduler and confirm success",
              required=False)
def run(experiment, pause, no_wait):
    """
    Run workflow configuration
    """
    run_script.workflow_run(experiment, pause, no_wait)

@workflow_cli.command()
@click.option("-e", "--experiment", type=str,
              help="Experiment name",
              required=True)
#@click.option("-p", "--platform", type=str,
#              help="Platform name",
#              required=True)
#@click.option("-T", "--target", type=str,
#              help="Target name",
#              required=True)
@click.option("-c", "--config-file", type=str,
              help="Path to a configuration file in either XML or YAML",
              required=True)
@click.option("-b", "--branch",
              required=False, default=None,
              help="fre-workflows branch/tag to clone; default is $(fre --version)")
@click.option("-t", "--time",
              required=False, default=None,
              help="Time whose history files are ready")
def all(experiment, platform, target, config_file, branch, time):
    """
    Execute all fre workflow initialization steps in order
    """
    wrapper_script.run_workflow_steps(experiment, platform, target, config_file, branch, time)
