"""
fremake.py defines the `click interface <click link_>`_ for the **fre make** tool
**fre make**'s subtools include:

* all
* checkout-script
* compile-script
* dockerfile
* makefile

**fre make** is the component of **fre** that will check out model code and compile model code. **fre make** subtools 
are capable of running independently of each other and there is an "all" option that will execute the 
fre make subtools in an appropriate order to fully compile a model. **fre make** also has the functionality 
to build a container of a model.

**fre make** ingests the `model.yaml <myaml link_>`_ configuration file, specifically using information in the:

* `platforms.yaml <pyaml link_>`_
* `compile.yaml <cyaml link_>`_

For a quickstart on **fre make**, please refer to the README.md at `fre-cli/fre/make/README.md <readme link_>`_

.. _click link: https://click.palletsprojects.com/en/stable/
.. _myaml link: https://noaa-gfdl.readthedocs.io/projects/fre-cli/en/latest/usage.html#model-yaml
.. _pyaml link: https://noaa-gfdl.readthedocs.io/projects/fre-cli/en/latest/usage.html#platform-yaml
.. _cyaml link: https://noaa-gfdl.readthedocs.io/projects/fre-cli/en/latest/usage.html#compile-yaml
.. _readme link: https://github.com/NOAA-GFDL/fre-cli/blob/main/fre/make/README.md
"""

import click
from fre.make import create_checkout_script
from fre.make import create_makefile_script
from fre.make import create_compile_script
from fre.make import create_docker_script
from fre.make import run_fremake_script


# Command Help Messages
_YAMLFILE_OPT_HELP = """Model configuration yaml FILENAME (required)"""
_PLATFORM_OPT_HELP = """Comma-separated list of FRE platform strings (min 1 required)\n
See https://noaa-gfdl.readthedocs.io/projects/fre-cli/en/latest/glossary.html#term-platform
"""
_TARGET_OPT_HELP   = """Comma-separated list of mkmf target strings (min 1 required)\n
See https://noaa-gfdl.readthedocs.io/projects/fre-cli/en/latest/glossary.html#term-target
"""
_PARALLEL_OPT_HELP = """Number of concurrent compile scripts to execute (optional) (default 1)\n
fre make generates one compile script per permutation of items in the target and platform lists.
This option is ignored when the argument --execute/-x is missing.
"""
_MAKE_JOBS_OPT_HELP = """Number of make recipes to compile simultaneously (optional) (default 4)"""
_GIT_JOBS_OPT_HELP = """Number of git submodules to clone simultaneously (optional) (default 4)"""
_NO_PARALLEL_CHECKOUT_OPT_HELP =  """Turns off parallel git checkouts
By default, fre make will checkout each git repository defined in the compile.yaml configuration file
in parallel.
"""
_VERBOSE_OPT_HELP = """Turns on debug level logging"""



@click.group(help=click.style(" - make subcommands", fg=(57,139,210)))
def make_cli():
    pass

@make_cli.command()
@click.option("-y",
              "--yamlfile",
              type = str,
              help = _YAMLFILE_OPT_HELP,
              required = True) # use click.option() over click.argument(), we want help statements
@click.option("-p",
              "--platform",
              multiple = True, # replaces nargs = -1, since click.option()
              type = str,
              help = _PLATFORM_OPT_HELP, required = True)
@click.option("-t", "--target",
              multiple = True,
              type = str,
              help = _TARGET_OPT_HELP,
              required = True)
@click.option("-n",
              "--nparallel",
              type = int,
              metavar = '',
              default = 1,
              help = _PARALLEL_OPT_HELP)
@click.option("-mj",
              "--makejobs",
              type = int,
              metavar = '',
              default = 4,
              help = _MAKE_JOBS_OPT_HELP)
@click.option("-gj",
              "--gitjobs",
              type = int,
              metavar = '',
              default = 4,
              help = _GIT_JOBS_OPT_HELP)
@click.option("-npc",
              "--no-parallel-checkout",
              is_flag = True,
              help = _NO_PARALLEL_CHECKOUT_OPT_HELP)
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
              help = _VERBOSE_OPT_HELP)
def all(yamlfile, platform, target, nparallel, makejobs, gitjobs, no_parallel_checkout, no_format_transfer, execute,
        verbose, force_checkout):
    """ - Perform all fre make functions; run checkout and compile scripts to create model executable or container"""
    run_fremake_script.fremake_run(
        yamlfile, platform, target, nparallel, makejobs, gitjobs, no_parallel_checkout, no_format_transfer, execute,
        verbose, force_checkout)

@make_cli.command()
@click.option("-y",
              "--yamlfile",
              type = str,
              help = _YAMLFILE_OPT_HELP,
              required = True) # use click.option() over click.argument(), we want help statements
@click.option("-p",
              "--platform",
              multiple = True, # replaces nargs = -1, since click.option()
              type = str,
              help = _PLATFORM_OPT_HELP,
              required = True)
@click.option("-t", "--target",
              multiple = True, # replaces nargs = -1, since click.option()
              type = str,
              help = _TARGET_OPT_HELP,
              required = True)
@click.option("-gj",
              "--gitjobs",
              type = int,
              metavar = '',
              default = 4,
              help = _GIT_JOBS_OPT_HELP)
@click.option("-npc",
              "--no-parallel-checkout",
              is_flag = True,
              help = _NO_PARALLEL_CHECKOUT_OPT_HELP)
@click.option("--execute",
              is_flag = True,
              default = False,
              help = "Use this to run the created checkout script.")
@click.option("--force-checkout",
              is_flag = True,
              help = "Force checkout in case the source directory exists.")
def checkout_script(yamlfile, platform, target, no_parallel_checkout, gitjobs, execute, force_checkout):
    """ - Write the checkout script """
    create_checkout_script.checkout_create(
        yamlfile, platform, target, no_parallel_checkout, gitjobs, execute, force_checkout)

@make_cli.command
@click.option("-y",
              "--yamlfile",
              type = str,
              help = _YAMLFILE_OPT_HELP,
              required = True) # use click.option() over click.argument(), we want help statements
@click.option("-p",
              "--platform",
              multiple = True, # replaces nargs = -1, since click.option()
              type = str,
              help = _PLATFORM_OPT_HELP, required = True)
@click.option("-t", "--target",
              multiple = True, # replaces nargs = -1, since click.option()
              type = str,
              help = _TARGET_OPT_HELP,
              required = True)
def makefile(yamlfile, platform, target):
    """ - Write the makefile """
    create_makefile_script.makefile_create(yamlfile, platform, target)

@make_cli.command
@click.option("-y",
              "--yamlfile",
              type = str,
              help = _YAMLFILE_OPT_HELP,
              required = True) # use click.option() over click.argument(), we want help statements
@click.option("-p",
              "--platform",
              multiple = True, # replaces nargs = -1, since click.option()
              type = str,
              help = _PLATFORM_OPT_HELP, required = True)
@click.option("-t", "--target",
              multiple = True, # replaces nargs = -1, since click.option()
              type = str,
              help = _TARGET_OPT_HELP,
              required = True)
@click.option("-mj",
              "--makejobs",
              type = int,
              metavar = '',
              default = 4,
              help = _MAKE_JOBS_OPT_HELP)
@click.option("-n",
              "--nparallel",
              type = int,
              metavar = '', default = 1,
              help = _PARALLEL_OPT_HELP)
@click.option("--execute",
              is_flag = True,
              default = False,
              help = "Use this to run the created checkout script.")
@click.option("-v",
              "--verbose",
              is_flag = True,
              help = _VERBOSE_OPT_HELP)
def compile_script(yamlfile, platform, target, makejobs, nparallel, execute, verbose):
    """ - Write the compile script """
    create_compile_script.compile_create(
        yamlfile, platform, target, makejobs, nparallel, execute, verbose)

@make_cli.command
@click.option("-y",
              "--yamlfile",
              type = str,
              help = _YAMLFILE_OPT_HELP,
              required = True)
@click.option("-p",
              "--platform",
              multiple = True, # replaces nargs = -1, since click.option()
              type = str,
              help = _PLATFORM_OPT_HELP, required = True)
@click.option("-t", "--target",
              multiple = True,
              type = str,
              help = _TARGET_OPT_HELP,
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
