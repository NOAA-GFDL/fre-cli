import click
from fre.make import create_checkout_script
from fre.make import create_makefile_script
from fre.make import create_compile_script
from fre.make import create_docker_script
from fre.make import run_fremake_script

YAMLFILE_OPT_HELP = """Experiment yaml compile FILE
"""
EXPERIMENT_OPT_HELP = """Name of experiment"""
PLATFORM_OPT_HELP = """Hardware and software FRE platform string.
This sets platform-specific data and instructions
"""
TARGET_OPT_HELP   = """String that defines compilation settings and
linkage directives for experiments. Predefined targets refer to groups of directives that exist in
the mkmf template file (referenced in buildDocker.py). Possible predefined targets include 'prod',
'openmp', 'repro', 'debug, 'hdf5'; however 'prod', 'repro', and 'debug' are mutually exclusive
(cannot not use more than one of these in the target list). Any number of targets can be used.
"""
PARALLEL_OPT_HELP = """Number of concurrent model compiles (default 1)
"""
JOBS_OPT_HELP = """Number of jobs to run simultaneously; default=4. Used for make -jJOBS (parallelism with make) and git clone recursive --njobs=JOBS (# of submodules fetched simultaneously)
"""
NO_PARALLEL_CHECKOUT_OPT_HELP =  """Use this option if you do not want a parallel checkout.
The default is to have parallel checkouts.
"""
VERBOSE_OPT_HELP = """Get verbose messages (repeat the option to increase verbosity level)
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
