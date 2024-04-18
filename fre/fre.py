"""
prototype file for FRE CLI
authored by Bennett.Chang@noaa.gov | bcc2761
NOAA | GFDL
2023-2024
"""

import click

from .pp import checkoutTemplate, yamlInfo, convert, validate_subtool, install_subtool, run_subtool, status_subtool 
from .catalog import build_script
from .list import list_test_function 
from .check import check_test_function
from .run import run_test_function
from .test import test_test_function
from .yamltools import yamltools_test_function
from .make import checkout_create, compile_create, makefile_create, dockerfile_create, fremake_run
from .app import maskAtmosPlevel_subtool 
from .cmor import run_subtool
from .lazy_group import LazyGroup

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
def frelist():
    """ - access fre list subcommands """
    pass

@fre.group('make')
def fremake():
    """ - access fre make subcommands """
    pass

@fre.group('run')
def frerun():
    """ - access fre run subcommands"""
    pass

@fre.group('pp')
def frepp():
    """ - access fre pp subcommands """
    pass

@fre.group('check')
def frecheck():
    """ - access fre check subcommands """
    pass

@fre.group('test')
def fretest():
    """ - access fre test subcommands """
    pass

@fre.group('catalog')
def frecatalog():
    """ - access fre catalog subcommands """
    pass

@fre.group('yamltools')
def freyamltools():
    """ - access fre yamltools subcommands """
    pass
@fre.group('cmor')
def frecmor():
    """ - access fre cmor subcommands"""
    pass

@fre.group('app')
def freapp():
    """ - access fre app subcommands"""
    pass

#############################################

"""
fre app subcommands to be processed
"""
@freapp.command()
@click.option("-i", "--infile",
              type=str,
              help="Input NetCDF file containing pressure-level output to be masked",
              required=True)
@click.option("-o", "--outfile",
              type=str,
              help="Output file",
              required=True)
@click.option("-p", "--psfile",
              help="Input NetCDF file containing surface pressure (ps)",
              required=True)
@click.pass_context
def mask_atmos_plevel(context, infile, outfile, psfile):
    """Mask out pressure level diagnostic output below land surface"""
    context.forward(maskAtmosPlevel_subtool)

#############################################

"""
fre make subcommands to be processed
"""

@fremake.command()
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
              type=str,               help="FRE target space separated list of STRING(s) that defines compilation settings and linkage directives for experiments. Predefined targets refer to groups of directives that exist in the mkmf template file (referenced in buildDocker.py). Possible predefined targets include 'prod', 'openmp', 'repro', 'debug, 'hdf5'; however 'prod', 'repro', and 'debug' are mutually exclusive (cannot not use more than one of these in the target list). Any number of targets can be used.",
              required=True)
@click.option("-e",
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
@click.pass_context
def run_fremake(context, yamlfile, platform, target, execute, parallel, jobs, no_parallel_checkout, submit, verbose):
    """ - Perform all fremake functions to run checkout and compile model"""
    context.forward(fremake_run)

####
@fremake.command()
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
@click.option("-e",
              "--execute",
              is_flag=True,
              default=False,
              help="Use this to run the created checkout script.")
@click.option("-v",
              "--verbose",
              is_flag=True,
              help="Get verbose messages (repeat the option to increase verbosity level)")
@click.pass_context
def create_checkout(context,yamlfile,platform,target,no_parallel_checkout,jobs,execute,verbose):
    """ - Write the checkout script """
    context.forward(checkout_create)

#####
@fremake.command
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
@click.pass_context
def create_makefile(context,yamlfile,platform,target):
    """ - Write the makefile """
    context.forward(makefile_create)

#####

@fremake.command
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
@click.option("-j",
              "--jobs",
              type=int,
              metavar='',
              default=4,
              help="Number of jobs to run simultaneously. Used for make -jJOBS and git clone recursive --jobs=JOBS")
@click.option("-n", 
              "--parallel",
              type=int, 
              metavar='', default=1,
              help="Number of concurrent model compiles (default 1)")
@click.option("-e",
              "--execute",
              is_flag=True,
              default=False,
              help="Use this to run the created checkout script.")
@click.option("-v",
              "--verbose",
              is_flag=True,
              help="Get verbose messages (repeat the option to increase verbosity level)")
@click.pass_context
def create_compile(context,yamlfile,platform,target,jobs,parallel,execute,verbose):
    """ - Write the compile script """
    context.forward(compile_create)

#####

@fremake.command
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
@click.option("-e",
              "--execute",
              is_flag=True,
              help="Build Dockerfile that has been generated by create-docker.")
@click.pass_context
def create_dockerfile(context,yamlfile,platform,target,execute):
    """ - Write the dockerfile """
    context.forward(dockerfile_create)

#############################################

"""
fre list subcommands to be processed
"""
@frelist.command()
@click.option('--uppercase', '-u', is_flag=True, help = 'Print statement in uppercase.')
@click.pass_context
def function(context, uppercase):
    """ - Execute fre list func """
    context.forward(list_test_function)

#############################################

"""
fre check subcommands to be processed
"""
@frecheck.command()
@click.option('--uppercase', '-u', is_flag=True, help = 'Print statement in uppercase.')
@click.pass_context
def function(context, uppercase):
    """ - Execute fre check func """
    context.forward(check_test_function)

#############################################
    
""" 
fre run subcommands to be processed
"""
@frerun.command()
@click.option('--uppercase', '-u', is_flag=True, help = 'Print statement in uppercase.')
@click.pass_context
def function(context, uppercase):
    """ - Execute fre check func """
    context.forward(run_test_function)

#############################################

"""
fre cmor subcommands to be processed
"""

# fre cmor run
@frecmor.command()
@click.option("-d", "--indir",
              type=str,
              help="Input directory",
              required=True)
@click.option("-l", "--varlist",
              type=str,
              help="Variable list",
              required=True)
@click.option("-r", "--table_config",
              type=str,
              help="Table configuration",
              required=True)
@click.option("-p", "--exp_config",
              type=str,
              help="Experiment configuration",
              required=True)
@click.option("-o", "--outdir",
              type=str,
              help="Output directory",
              required=True)
@click.pass_context
def run(context, indir, outdir, varlist, table_config, exp_config):
    """Rewrite climate model output"""
    context.forward(run_subtool)

#############################################

"""
fre pp subcommands to be processed
"""

# fre pp status
@frepp.command()
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
def status(context, experiment, platform, target):
    """ - Report status of PP configuration"""
    context.forward(status_subtool)

# fre pp run
@frepp.command()
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
def run(context, experiment, platform, target):
    """ - Run PP configuration"""
    context.forward(run_subtool)

# fre pp validate
@frepp.command()
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
def validate(context, experiment, platform, target):
    """ - Validate PP configuration"""
    context.forward(validate_subtool)

# fre pp install
@frepp.command()
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
def install(context, experiment, platform, target):
    """ - Install PP configuration"""
    context.forward(install_subtool)

@frepp.command()
@click.option("-y",
              "--yamlfile",
              type=str,
              help="YAML file to be used for parsing",
              required=True)
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
def configure_yaml(context,yamlfile,experiment,platform,target):
    """ - Execute fre pp configure """
    context.forward(yamlInfo)

@frepp.command()
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
    """ - Execute fre pp checkout """
    context.forward(checkoutTemplate)

@frepp.command()
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
def configure_xml(context, xml, platform, target, experiment, do_analysis, historydir, refinedir, ppdir, do_refinediag, pp_start, pp_stop, validate, verbose, quiet, dual):
    """ - Converts a Bronx XML to a Canopy rose-suite.conf """
    context.forward(convert)

#############################################

"""
fre test subcommands to be processed
"""
@fretest.command()
@click.option('--uppercase', '-u', is_flag=True, help = 'Print statement in uppercase.')
@click.pass_context
def function(context, uppercase):
    """ - Execute fre test testfunction """
    context.forward(test_test_function)

#############################################

"""
fre catalog subcommands to be processed
"""
@frecatalog.command()
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
def build(context, input_path, output_path, filter_realm, filter_freq, filter_chunk, overwrite,append):
    """ - Execute fre catalog build """
    context.forward(build_script)

#############################################

"""
fre yamltools subcommands to be processed
"""
@freyamltools.command()
@click.option('--uppercase', '-u', is_flag=True, help = 'Print statement in uppercase.')
@click.pass_context
def testfunction(context, uppercase):
    """ - Execute fre yamltools testfunction """
    context.forward(yamltools_test_function)

#############################################

if __name__ == '__main__':
    fre()
