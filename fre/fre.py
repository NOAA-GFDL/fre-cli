"""
prototype file for FRE CLI
authored by Bennett.Chang@noaa.gov | bcc2761
NOAA | GFDL
2023-2024
"""

import click

from fre import list
from fre.list.frelist import *

from fre import check
from fre.check.frecheck import *

from fre import make
from fre.make.fremake import *

from fre import pp
from fre.pp.frepp import *

from fre import run
from fre.run.frerun import *

from fre import test
from fre.test.fretest import *

from fre import catalog
from fre.catalog.frecatalog import *

from fre import yamltools
from fre.yamltools.freyamltools import *

#############################################

"""
principal main fre click group allows for subcommand functions from subgroups to be called via through this script with 'fre' as the entry point
"""
@click.group()
def fre():
    pass

#############################################

"""
this is a nested group within the fre group that allows commands to be processed
"""
@fre.group('list')
def freList():
    """ - access fre list subcommands """
    pass

@fre.group('make')
def freMake():
    """ - access fre make subcommands """
    pass

@fre.group('run')
def freRun():
    """ - access fre run subcommands"""
    pass

@fre.group('pp')
def frePP():
    """ - access fre pp subcommands """
    pass

@fre.group('check')
def freCheck():
    """ - access fre check subcommands """
    pass

@fre.group('test')
def freTest():
    """ - access fre test subcommands """
    pass

@fre.group('catalog')
def freCatalog():
    """ - access fre catalog subcommands """
    pass

@fre.group('yamltools')
def freYamltools():
    """ - access fre yamltools subcommands """
    pass

#############################################

"""
fre make subcommands to be processed
"""
@freMake.command()
@click.option('--uppercase', '-u', is_flag=True, help = 'Print statement in uppercase.')
def checkout(uppercase):
    """ - Execute fre make checkout """
    statement = "execute fre make checkout script" 
    if uppercase:
        statement = statement.upper()
    click.echo(statement)

@freMake.command()
@click.option("-y", 
              "--yamlfile", 
              type=str, 
              help="Experiment yaml compile FILE", 
              required=True) # used click.option() instead of click.argument() because we want to have help statements
@click.option("-p", 
              "--platform", 
              multiple=True, #replaces nargs=-1 since we are using click.option() instead of click.argument()
              type=str, 
              help="Hardware and software FRE platform space separated list of STRING(s). This sets platform-specific data and instructions", required=True)
@click.option("-t", "--target", 
              multiple=True, #replaces nargs=-1 since we are using click.option() instead of click.argument()
              type=str, 
              help="FRE target space separated list of STRING(s) that defines compilation settings and linkage directives for experiments. Predefined targets refer to groups of directives that exist in the mkmf template file (referenced in buildDocker.py). Possible predefined targets include 'prod', 'openmp', 'repro', 'debug, 'hdf5'; however 'prod', 'repro', and 'debug' are mutually exclusive (cannot not use more than one of these in the target list). Any number of targets can be used.", 
              required=True)
@click.option("-f", 
              "--force-checkout", 
              is_flag=True, 
              help="Force checkout to get a fresh checkout to source directory in case the source directory exists")
@click.option("-F", 
              "--force-compile", 
              is_flag=True, 
              help="Force compile to compile a fresh executable in case the executable directory exists")
@click.option("-K", 
              "--keep-compiled", 
              is_flag=True, 
              help="Keep compiled files in the executable directory for future use")
@click.option("--no-link", 
              is_flag=True, 
              help="Do not link the executable")
@click.option("-E", 
              "--execute", 
              is_flag=True, 
              help="Execute all the created scripts in the current session")
@click.option("-n", 
              "--parallel", 
              type=int,
              metavar='', 
              default=1, 
              help="Number of concurrent model compiles (default 1)")
@click.option("-j", 
              "--jobs", 
              type=int, 
              metavar='',
              default=4, 
              help="Number of jobs to run simultaneously. Used for make -jJOBS and git clone recursive --jobs=JOBS")
@click.option("-npc", 
              "--no-parallel-checkout", 
              is_flag=True, 
              help="Use this option if you do not want a parallel checkout. The default is to have parallel checkouts.")
@click.option("-s", 
              "--submit", 
              is_flag=True, 
              help="Submit all the created scripts as batch jobs")
@click.option("-v", 
              "--verbose", 
              is_flag=True, 
              help="Get verbose messages (repeat the option to increase verbosity level)")
@click.option("-w", 
              "--walltime", 
              type=int, 
              metavar='', 
              help="Maximum wall time NUM (in minutes) to use")
@click.option("--mail-list", 
              type=str, 
              help="Email the comma-separated STRING list of emails rather than $USER@noaa.gov")
@click.pass_context
def fremakefunction(context, yamlfile, platform, target, force_checkout, force_compile, keep_compiled, no_link, execute, parallel, jobs, no_parallel_checkout, submit, verbose, walltime, mail_list):
    """ - Execute fre make func """
    context.forward(make.fremake.fremake)

# # this is the command that will execute all of `fre make`, but I need to test whether it will be able to pass specific flags to different areas when it they each have different flags
# @freMake.command()
# @click.option('--uppercase', '-u', is_flag=True, help = 'Print statement in uppercase.')
# @click.pass_context
# def executeAll(context, uppercase):
#     """ - Execute all commands under fre make"""
#     context.forward(checkout)
#     context.forward(compile)
#     context.forward(container)
#     context.forward(list)

#############################################

"""
fre list subcommands to be processed
"""
@freList.command()
@click.option('--uppercase', '-u', is_flag=True, help = 'Print statement in uppercase.')
@click.pass_context
def function(context, uppercase):
    """ - Execute fre list func """
    context.forward(list.frelist.testfunction2)

#############################################

"""
fre pp subcommands to be processed
"""
@frePP.command()
@click.option("-y", 
              type=str, 
              help="YAML file to be used for parsing", 
              required=True)
@click.pass_context
def configure(context, y):
    """ - Execute fre pp configure """
    context.forward(pp.frepp.configure)

@frePP.command()
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
@click.pass_context
def checkout(context, experiment, platform, target):
    """ - Execute fre pp checkout """
    context.forward(pp.frepp.checkout)

#############################################

"""
fre test subcommands to be processed
"""
@freTest.command()
@click.option('--uppercase', '-u', is_flag=True, help = 'Print statement in uppercase.')
@click.pass_context
def testfunction(context, uppercase):
    """ - Execute fre test testfunction """
    context.forward(test.fretest.testfunction)

#############################################

"""
fre catalog subcommands to be processed
"""
@freCatalog.command()
@click.option('-i',
              '--input_path', 
              required=True, 
              nargs=1) 
@click.option('-o',
              '--output_path', 
              required=True, 
              nargs=1)
@click.option('--filter_realm', 
              nargs=1)
@click.option('--filter_freq', 
              nargs=1)
@click.option('--filter_chunk', 
              nargs=1)
@click.option('--overwrite', 
              is_flag=True, 
              default=False)
@click.option('--append', 
              is_flag=True, 
              default=False)
@click.pass_context
def buildCatalog(context, input_path, output_path, filter_realm, filter_freq, filter_chunk, overwrite,append):
    """ - Execute fre catalog build """
    context.forward(catalog.frecatalog.buildCatalog)

#############################################

"""
fre yamltools subcommands to be processed
"""
@freYamltools.command()
@click.option('--uppercase', '-u', is_flag=True, help = 'Print statement in uppercase.')
@click.pass_context
def testfunction(context, uppercase):
    """ - Execute fre yamltools testfunction """
    context.forward(yamltools.freyamltools.testfunction)

#############################################

if __name__ == '__main__':
    fre()