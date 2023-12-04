"""
prototype file for FRE CLI
authored by Bennett.Chang@noaa.gov | bcc2761
NOAA | GFDL
"""

import click

from fre import frelist
from fre.frelist.frelist import *

from fre import frecheck
from fre.frecheck.frecheck import *

from fre import fremake
from fre.fremake.fremake import *

from fre import frepp
from fre.frepp.frepp import *

from fre import frerun
from fre.frerun.frerun import *

from fre import fretest
from fre.fretest.fretest import *

"""
click group allows for multiple functions to be called via same script
"""
@click.group()
def fre():
    pass

"""
this is a nested group within the {fre} group that allows commands to be processed
"""
@fre.group('list')
def freList():
    """ - Execute fre list """
    pass

@fre.group('make')
def freMake():
    """ - Execute fre make """
    pass

@fre.group('run')
def freRun():
    """ - Execute fre run """
    pass

@fre.group('pp')
def frePP():
    """ - Execute fre pp """
    pass

@fre.group('check')
def freCheck():
    """ - Execute fre check """
    pass

@fre.group('test')
@click.pass_context
def freTest(context):
    """ - Execute fre test """
    pass

"""
{fremake} subcommands to be processed
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
@click.option('--uppercase', '-u', is_flag=True, help = 'Print statement in uppercase.')
def compile(uppercase):
    """ - Execute fre make compile """
    statement = "execute fre make compile script" 
    if uppercase:
        statement = statement.upper()
    click.echo(statement)

@freMake.command()
@click.option('--uppercase', '-u', is_flag=True, help = 'Print statement in uppercase.')
def container(uppercase):
    """ - Execute fre make container """
    statement = "execute fre make container script" 
    if uppercase:
        statement = statement.upper()
    click.echo(statement)

@freMake.command()
@click.option('--uppercase', '-u', is_flag=True, help = 'Print statement in uppercase.')
def list(uppercase):
    """ - Execute fre make list """
    statement = "execute fre make list script" 
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
    context.forward(fremake)

# this is the command that will execute all of `fre make`, but I need to test whether it will be able to pass specific flags to different areas when it they each have different flags
@freMake.command()
@click.option('--uppercase', '-u', is_flag=True, help = 'Print statement in uppercase.')
@click.pass_context
def executeAll(context, uppercase):
    """ - Execute all commands under fre make"""
    context.forward(checkout)
    context.forward(compile)
    context.forward(container)
    context.forward(list)

"""
{frelist} subcommands to be processed
"""
@freList.command()
@click.option('--uppercase', '-u', is_flag=True, help = 'Print statement in uppercase.')
@click.pass_context
def function(context, uppercase):
    """ - Execute fre list func """
    context.forward(testfunction2)

# """
# {frepp} subcommands to be processed
# """
# @frePP.command()
# @click.option('--uppercase', '-u', is_flag=True, help = 'Print statement in uppercase.')
# @click.pass_context
# def frepptest(context, uppercase):
#     """ - Execute fre pp test """
#     context.forward(frepptest)

@freTest.command()
# @click.option('--uppercase', '-u', is_flag=True, help = 'Print statement in uppercase.')
@click.pass_context
def testfunction(context):
    """ - Execute fre test testfunction """
    context.forward(fretest.fretest.testfunction)


if __name__ == '__main__':
    fre()