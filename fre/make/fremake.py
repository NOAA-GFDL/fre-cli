"""
This module defines the click interface for the fre make tool
fre make's subtools include:
    - all
    - checkout-script
    - compile-script
    - dockerfile
    - makefile
fre make is the component of fre that will check out model code and build the model. fre make subtools 
are capable of running independently of each other and there is an "all" option that will execute the 
fre make subtools in an appropriate order to fully compile a model. Fre make also has the functionality 
to build a container of a model. 
fre make ingests the model.yaml configuration file, specifically using information in the:
    - platforms.yaml (this configuration file specifies the software needed to compile a model)
    - compile.yaml (this configuration file specifies code repositories and versions to checkout)
To checkout model code: fre make checkout-script
To compile model code (after the model code has been checked out):
    - First, create a makefile: fre make makefile
    - Then, compile the model: fre make compile-script
To create a container which will package the compiled model executable and the environment:
    - First, create a makefile: fre make makefile
    - Then, build the model in a container: fre make dockerfile
"""

import click
from fre.make import create_checkout_script
from fre.make import create_makefile_script
from fre.make import create_compile_script
from fre.make import create_docker_script
from fre.make import run_fremake_script


# Command Help Messages
_YAMLFILE_OPT_HELP = """Model configuration yaml FILENAME (required)"""
_PLATFORM_OPT_HELP = """List of FRE platform strings (required)
The name of the platform from platforms.yaml.
"""
_TARGET_OPT_HELP   = """List of mkmf Target strings (required)
The mkmf targets correspond to macros in the template file specified by platforms.yaml. 
Users must provide a single optimization target: either prod, repro, or debug. 
To enable supplementary features such as openmp or lto, append them to the primary target using a hyphen separator.
"""
_PARALLEL_OPT_HELP = """Number of concurrent compile scripts to execute (optional) (default 1)
This option is only used when --execute/-x is also defined.
"""
_JOBS_OPT_HELP = """Number of make jobs to run simultaneously (optional) (default4)
make -jJOBS which enables make to compile multiple source files simultaneously

and git clone recursive --njobs=JOBS (# of submodules fetched simultaneously)
"""
_NO_PARALLEL_CHECKOUT_OPT_HELP =  """Turns off parallel git checkouts
By default, fre make will checkout each git repository defined in the compile.yaml configuration file 
in parallel.
"""
_VERBOSE_OPT_HELP = """Turns on debug level logging
"""



@click.group(help=click.style(" - make subcommands", fg=(57,139,210)))
def make_cli():
    pass

@make_cli.command()
@click.option("-y",
              "--yamlfile",
              type = str,
              help = YAMLFILE_OPT_HELP,
              required = True) # use click.option() over click.argument(), we want help statements
@click.option("-p",
              "--platform",
              multiple = True, # replaces nargs = -1, since click.option()
              type = str,
              help = PLATFORM_OPT_HELP, required = True)
@click.option("-t", "--target",
              multiple = True,
              type = str,
              help = TARGET_OPT_HELP,
              required = True)
@click.option("-n",
              "--nparallel",
              type = int,
              metavar = '',
              default = 1,
              help = PARALLEL_OPT_HELP)
@click.option("-j",
              "--njobs",
              type = int,
              metavar = '',
              default = 4,
              help = JOBS_OPT_HELP)
@click.option("-npc",
              "--no-parallel-checkout",
              is_flag = True,
              help = NO_PARALLEL_CHECKOUT_OPT_HELP)
@click.option("-nft",
              "--no-format-transfer",
              is_flag = True,
              default = False,
              help = "Use this to skip the container format conversion to a .sif file.")
@click.option("-e",
              "--execute",
              is_flag = True,
              default = False,
              help = "Use this to run the created compilation script.")
@click.option("--force-checkout",
              is_flag = True,
              help = "Force checkout in case the source directory exists.")
@click.option("-v",
              "--verbose",
              is_flag = True,
              help = VERBOSE_OPT_HELP)
def all(yamlfile, platform, target, nparallel, njobs, no_parallel_checkout, no_format_transfer, execute, verbose, force_checkout):
    """ - Perform all fre make functions; run checkout and compile scripts to create model executable or container"""
    run_fremake_script.fremake_run(
        yamlfile, platform, target, nparallel, njobs, no_parallel_checkout, no_format_transfer, execute, verbose, force_checkout)

@make_cli.command()
@click.option("-y",
              "--yamlfile",
              type = str,
              help = YAMLFILE_OPT_HELP,
              required = True) # use click.option() over click.argument(), we want help statements
@click.option("-p",
              "--platform",
              multiple = True, # replaces nargs = -1, since click.option()
              type = str,
              help = PLATFORM_OPT_HELP,
              required = True)
@click.option("-t", "--target",
              multiple = True, # replaces nargs = -1, since click.option()
              type = str,
              help = TARGET_OPT_HELP,
              required = True)
@click.option("-j",
              "--njobs",
              type = int,
              metavar = '',
              default = 4,
              help = JOBS_OPT_HELP)
@click.option("-npc",
              "--no-parallel-checkout",
              is_flag = True,
              help = NO_PARALLEL_CHECKOUT_OPT_HELP)
@click.option("--execute",
              is_flag = True,
              default = False,
              help = "Use this to run the created checkout script.")
@click.option("--force-checkout",
              is_flag = True,
              help = "Force checkout in case the source directory exists.")
def checkout_script(yamlfile, platform, target, no_parallel_checkout, njobs, execute, force_checkout):
    """ - Write the checkout script """
    create_checkout_script.checkout_create(
        yamlfile, platform, target, no_parallel_checkout, njobs, execute, force_checkout)

@make_cli.command
@click.option("-y",
              "--yamlfile",
              type = str,
              help = YAMLFILE_OPT_HELP,
              required = True) # use click.option() over click.argument(), we want help statements
@click.option("-p",
              "--platform",
              multiple = True, # replaces nargs = -1, since click.option()
              type = str,
              help = PLATFORM_OPT_HELP, required = True)
@click.option("-t", "--target",
              multiple = True, # replaces nargs = -1, since click.option()
              type = str,
              help = TARGET_OPT_HELP,
              required = True)
def makefile(yamlfile, platform, target):
    """ - Write the makefile """
    create_makefile_script.makefile_create(yamlfile, platform, target)

@make_cli.command
@click.option("-y",
              "--yamlfile",
              type = str,
              help = YAMLFILE_OPT_HELP,
              required = True) # use click.option() over click.argument(), we want help statements
@click.option("-p",
              "--platform",
              multiple = True, # replaces nargs = -1, since click.option()
              type = str,
              help = PLATFORM_OPT_HELP, required = True)
@click.option("-t", "--target",
              multiple = True, # replaces nargs = -1, since click.option()
              type = str,
              help = TARGET_OPT_HELP,
              required = True)
@click.option("-j",
              "--njobs",
              type = int,
              metavar = '',
              default = 4,
              help = JOBS_OPT_HELP)
@click.option("-n",
              "--nparallel",
              type = int,
              metavar = '', default = 1,
              help = PARALLEL_OPT_HELP)
@click.option("--execute",
              is_flag = True,
              default = False,
              help = "Use this to run the created checkout script.")
@click.option("-v",
              "--verbose",
              is_flag = True,
              help = VERBOSE_OPT_HELP)
def compile_script(yamlfile, platform, target, njobs, nparallel, execute, verbose):
    """ - Write the compile script """
    create_compile_script.compile_create(
        yamlfile, platform, target, njobs, nparallel, execute, verbose)

@make_cli.command
@click.option("-y",
              "--yamlfile",
              type = str,
              help = YAMLFILE_OPT_HELP,
              required = True)
@click.option("-p",
              "--platform",
              multiple = True, # replaces nargs = -1, since click.option()
              type = str,
              help = PLATFORM_OPT_HELP, required = True)
@click.option("-t", "--target",
              multiple = True,
              type = str,
              help = TARGET_OPT_HELP,
              required = True)
@click.option("-nft",
              "--no-format-transfer",
              is_flag = True,
              default = False,
              help = "Use this to skip the container format conversion to a .sif file.")
@click.option("--execute",
              is_flag = True,
              default = False,
              help = "Build Dockerfile that has been generated by create-docker.")
def dockerfile(yamlfile, platform, target, no_format_transfer, execute):
    """ - Write the dockerfile """
    create_docker_script.dockerfile_create(yamlfile, platform, target, no_format_transfer, execute)
