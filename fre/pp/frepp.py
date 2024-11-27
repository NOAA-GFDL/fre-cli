''' fre pp '''

import click
from .checkout_script import _checkout_template
from .configure_script_yaml import _yamlInfo
from .configure_script_xml import convert
from .validate import _validate_subtool
from .install import _install_subtool
from .run import _pp_run_subtool
from .trigger import _trigger
from .status import _status_subtool
from .wrapper import runFre2pp

@click.group(help=click.style(" - access fre pp subcommands", fg=(57,139,210)))
def pp_cli():
    ''' entry point to fre pp click commands '''


# fre pp status
@pp_cli.command()
@click.option("-e", "--experiment", type=str,
              help="Experiment name",
              required=True)
@click.option("-p", "--platform", type=str,
              help="Platform name",
              required=True)
@click.option("-t", "--target", type=str,
              help="Target name",
              required=True)
@click.pass_context
def status(context, experiment, platform, target):
    # pylint: disable=unused-argument
    """ - Report status of PP configuration"""
    context.forward(_status_subtool)

# fre pp run
@pp_cli.command()
@click.option("-e", "--experiment", type=str,
              help="Experiment name",
              required=True)
@click.option("-p", "--platform", type=str,
              help="Platform name",
              required=True)
@click.option("-t", "--target", type=str,
              help="Target name",
              required=True)
@click.pass_context
def run(context, experiment, platform, target):
    # pylint: disable=unused-argument
    """ - Run PP configuration"""
    context.forward(_pp_run_subtool)

# fre pp validate
@pp_cli.command()
@click.option("-e", "--experiment", type=str,
              help="Experiment name",
              required=True)
@click.option("-p", "--platform", type=str,
              help="Platform name",
              required=True)
@click.option("-t", "--target", type=str,
              help="Target name",
              required=True)
@click.pass_context
def validate(context, experiment, platform, target):
    # pylint: disable=unused-argument
    """ - Validate PP configuration"""
    context.forward(_validate_subtool)

# fre pp install
@pp_cli.command()
@click.option("-e", "--experiment", type=str,
              help="Experiment name",
              required=True)
@click.option("-p", "--platform", type=str,
              help="Platform name",
              required=True)
@click.option("-t", "--target", type=str,
              help="Target name",
              required=True)
@click.pass_context
def install(context, experiment, platform, target):
    # pylint: disable=unused-argument
    """ - Install PP configuration"""
    context.forward(_install_subtool)

@pp_cli.command()
@click.option("-y", "--yamlfile", type=str,
              help="YAML file to be used for parsing",
              required=True)
@click.option("-e", "--experiment", type=str,
              help="Experiment name",
              required=True)
@click.option("-p", "--platform", type=str,
              help="Platform name",
              required=True)
@click.option("-t", "--target", type=str,
              help="Target name",
              required=True)
@click.pass_context
def configure_yaml(context,yamlfile,experiment,platform,target):
    # pylint: disable=unused-argument
    """ - Execute fre pp configure """
    context.forward(_yamlInfo)

@pp_cli.command()
@click.option("-e", "--experiment", type=str,
              help="Experiment name",
              required=True)
@click.option("-p", "--platform", type=str,
              help="Platform name",
              required=True)
@click.option("-t", "--target", type=str,
              help="Target name",
              required=True)
@click.option("-b", "--branch",
              required=False,
              help="fre-workflows branch/tag to clone; default is $(fre --version)")
@click.pass_context
def checkout(context, experiment, platform, target, branch=None):
    # pylint: disable=unused-argument
    """ - Execute fre pp checkout """
    context.forward(_checkout_template)

@pp_cli.command()
@click.option('-x', '--xml',
              required=True,
              help="Required. The Bronx XML")
@click.option('-p', '--platform',
              required=True,
              help="Required. The Bronx XML Platform")
@click.option('-t', '--target',
              required=True,
              help="Required. The Bronx XML Target")
@click.option('-e', '--experiment',
              required=True,
              help="Required. The Bronx XML Experiment")
@click.option('--do_analysis',
              is_flag=True,
              default=False,
              help="Optional. Runs the analysis scripts.")
@click.option('--historydir',
              help="Optional. History directory to reference. " \
                   "If not specified, the XML's default will be used.")
@click.option('--refinedir',
              help="Optional. History refineDiag directory to reference. " \
                   "If not specified, the XML's default will be used.")
@click.option('--ppdir',
              help="Optional. Postprocessing directory to reference. " \
                   "If not specified, the XML's default will be used.")
@click.option('--do_refinediag',
              is_flag=True,
              default=False,
              help="Optional. Process refineDiag scripts")
@click.option('--pp_start',
              help="Optional. Starting year of postprocessing. " \
                   "If not specified, a default value of '0000' " \
                   "will be set and must be changed in rose-suite.conf")
@click.option('--pp_stop',
              help="Optional. Ending year of postprocessing. " \
                    "If not specified, a default value of '0000' " \
                    "will be set and must be changed in rose-suite.conf")
@click.option('--validate',
              is_flag=True,
              help="Optional. Run the Cylc validator " \
                    "immediately after conversion")
@click.option('-v', '--verbose',
              is_flag=True,
              help="Optional. Display detailed output")
@click.option('-q', '--quiet',
              is_flag=True,
              help="Optional. Display only serious messages and/or errors")
@click.option('--dual',
              is_flag=True,
              help="Optional. Append '_canopy' to pp, analysis, and refinediag dirs")
@click.pass_context
def configure_xml(context, xml, platform, target, experiment, do_analysis, historydir, refinedir,
                  ppdir, do_refinediag, pp_start, pp_stop, validate, verbose, quiet, dual):
    # pylint: disable=unused-argument
    """ - Converts a Bronx XML to a Canopy rose-suite.conf """
    context.forward(convert)

#fre pp wrapper
@pp_cli.command()
@click.option("-e", "--experiment", type=str,
              help="Experiment name",
              required=True)
@click.option("-p", "--platform", type=str,
              help="Platform name",
              required=True)
@click.option("-T", "--target", type=str,
              help="Target name",
              required=True)
@click.option("-c", "--config-file", type=str,
              help="Path to a configuration file in either XML or YAML",
              required=True)
@click.option("-t", "--time",
              required=False,
              help="Time whose history files are ready")
@click.option("-b", "--branch",
              required=False,
              help="fre-workflows branch/tag to clone; default is $(fre --version)")
@click.pass_context
def wrapper(context, experiment, platform, target, config_file, time=None, branch=None):
    # pylint: disable=unused-argument
    """ - Execute fre pp steps in order """
    context.forward(runFre2pp)

@pp_cli.command()
@click.option("-e", "--experiment", type=str,
              help="Experiment name",
              required=True)
@click.option("-p", "--platform", type=str,
              help="Platform name",
              required=True)
@click.option("-T", "--target", type=str,
              help="Target name",
              required=True)
@click.option("-t", "--time",
              required=True,
              help="Time whose history files are ready")
@click.pass_context
def trigger(context, experiment, platform, target, time):
    # pylint: disable=unused-argument
    """ - Start postprocessing for a particular time """
    context.forward(_trigger)

if __name__ == "__main__":
    ''' entry point for click to fre pp commands '''
    pp_cli()
