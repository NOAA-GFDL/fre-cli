#!/usr/bin/python3
## \date 2023
## \author Bennett Chang
## \description Script for frepp is used to post process outputs obtained from other fre commands.

import click

from fre.frepp.configureScriptYAML import *
from fre.frepp.checkoutScript import *
from fre.frepp.configureScriptXML import *
from fre.frepp.validate import *
from fre.frepp.install import *
from fre.frepp.run import *
from fre.frepp.status import *

#############################################

@click.group()
def pp():
    pass

#############################################

# fre pp status
@pp.command()
@click.pass_context
def status(context, experiment, platform, target):
    context.forward(status_subtool)

#############################################

# fre pp run
@pp.command()
@click.pass_context
def run(context, experiment, platform, target):
    context.forward(run_subtool)

#############################################

# fre pp validate
@pp.command()
@click.pass_context
def validate(context, experiment, platform, target):
    context.forward(validate_subtool)

#############################################

# fre pp install
@pp.command()
@click.pass_context
def install(context, experiment, platform, target):
    context.forward(install_subtool)

#############################################

@pp.command()
@click.pass_context
def configureYAML(context,yamlfile,experiment,platform,target):
    """
    Takes a YAML file, parses it, and creates an output
    """
    context.forward(yamlInfo)

#############################################

@pp.command()
@click.option("-e",
              "--experiment", 
              type=str, 
              help="Experiment name", 
              required=True)
@click.option("-p",
              "--platform",
              type=str, 
              help="Platform name", 
              required=True)
@click.option("-t",
              "--target", 
              type=str, 
              help="Target name", 
              required=True)
@click.option("-b", 
              "--branch",
              show_default=True,
              default="main",
              type=str,
              help=" ".join(["Name of fre2/workflows/postproc branch to clone;" 
                            "defaults to 'main'. Not intended for production use,"
                            "but needed for branch testing."])
                            )
@click.pass_context
def checkout(context, experiment, platform, target, branch='main'):
    """
    Checkout the workflow template files from the repo
    """
    context.forward(checkoutTemplate)

#############################################

@pp.command()
@click.option('-x',
              '--xml',
              required=True,
              help="Required. The Bronx XML")
@click.option('-p',
              '--platform',
              required=True,
              help="Required. The Bronx XML Platform")
@click.option('-t',
              '--target',
              required=True,
              help="Required. The Bronx XML Target")
@click.option('-e',
              '--experiment',
              required=True,
              help="Required. The Bronx XML Experiment")
@click.option('--do_analysis',
              is_flag=True,
              default=False,
              help="Optional. Runs the analysis scripts.")
@click.option('--historydir',
              help="Optional. History directory to reference. "                    \
                    "If not specified, the XML's default will be used.")
@click.option('--refinedir',
              help="Optional. History refineDiag directory to reference. "         \
                    "If not specified, the XML's default will be used.")
@click.option('--ppdir',
              help="Optional. Postprocessing directory to reference. "             \
                    "If not specified, the XML's default will be used.")
@click.option('--do_refinediag',
              is_flag=True,
              default=False,
              help="Optional. Process refineDiag scripts")
@click.option('--pp_start',
              help="Optional. Starting year of postprocessing. "                   \
                    "If not specified, a default value of '0000' "                  \
                    "will be set and must be changed in rose-suite.conf")
@click.option('--pp_stop',
              help="Optional. Ending year of postprocessing. "                     \
                    "If not specified, a default value of '0000' "                  \
                    "will be set and must be changed in rose-suite.conf")
@click.option('--validate',
              is_flag=True,
              help="Optional. Run the Cylc validator "                             \
                    "immediately after conversion")
@click.option('-v',
              '--verbose',
              is_flag=True,
              help="Optional. Display detailed output")
@click.option('-q',
              '--quiet',
              is_flag=True,
              help="Optional. Display only serious messages and/or errors")
@click.option('--dual',
              is_flag=True,
              help="Optional. Append '_canopy' to pp, analysis, and refinediag dirs")
@click.pass_context
def configureXML(context, xml, platform, target, experiment, do_analysis, historydir, refinedir, ppdir, do_refinediag, pp_start, pp_stop, validate, verbose, quiet, dual):
    """
    Converts a Bronx XML to a Canopy rose-suite.conf 
    """
    context.forward(convert)

#############################################=

if __name__ == "__main__":
    pp()
