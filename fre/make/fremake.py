import click
from fre.make import create_checkout_script
from fre.make import create_makefile_script
from fre.make import create_compile_script
from fre.make import create_docker_script
from fre.make import run_fremake_script

YAMLFILE_OPT_HELP = """Experiment yaml compile FILE
"""
EXPERIMENT_OPT_HELP = """Name of experiment"""
PLATFORM_OPT_HELP = """Hardware and software FRE platform space separated list of STRING(s).
This sets platform-specific data and instructions
"""
TARGET_OPT_HELP   = """a space separated list of STRING(s) that defines compilation settings and
linkage directives for experiments. Predefined targets refer to groups of directives that exist in
the mkmf template file (referenced in buildDocker.py). Possible predefined targets include 'prod',
'openmp', 'repro', 'debug, 'hdf5'; however 'prod', 'repro', and 'debug' are mutually exclusive
(cannot not use more than one of these in the target list). Any number of targets can be used.
"""
PARALLEL_OPT_HELP = """Number of concurrent model compiles (default 1)
"""
JOBS_OPT_HELP = """Number of jobs to run simultaneously. Used for make -jJOBS and git clone
recursive --jobs=JOBS
"""
NO_PARALLEL_CHECKOUT_OPT_HELP =  """Use this option if you do not want a parallel checkout.
The default is to have parallel checkouts.
"""
VERBOSE_OPT_HELP = """Get verbose messages (repeat the option to increase verbosity level)
"""
FORCE_CHECKOUT_OPT_HELP = """Force checkout in case the source directory exists.
"""
FORCE_COMPILE_OPT_HELP = """Force compile in case the executable directory exists.
"""
FORCE_DOCKERFILE_OPT_HELP = """Force dockerfile creation in case dockerfile exists.
"""

@click.group(help=click.style(" - make subcommands", fg=(210,73,57)))
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
              "--parallel",
              type = int,
              metavar = '',
              default = 1,
              help = PARALLEL_OPT_HELP)
@click.option("-j",
              "--jobs",
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
@click.option("-v",
              "--verbose",
              is_flag = True,
              help = VERBOSE_OPT_HELP)
@click.option("-f",
              "--force-checkout",
              is_flag = True,
              help = FORCE_CHECKOUT_OPT_HELP)
@click.option("-F",
              "--force-compile",
              is_flag=True,
              help = FORCE_COMPILE_OPT_HELP)
@click.option("-FD",
              "--force-dockerfile",
              is_flag=True,
              help = FORCE_DOCKERFILE_OPT_HELP)
def run_fremake(yamlfile, platform, target, parallel, jobs, no_parallel_checkout, no_format_transfer, execute, verbose, force_checkout, force_compile, force_dockerfile):
    """
    - Perform all fremake functions to run checkout and compile model\n
    - For --target use: Predefined targets refer to groups of directives that exist in the mkmf template file.\n
          Possible predefined targets include 'prod','openmp', 'repro', 'debug, 'hdf5';
however 'prod', 'repro', and 'debug' are mutually exclusive (cannot not use more than one
of these in the target list). Any number of targets can be used.\n
    - The -npc option is REQUIRED for container builds\n
    - Use --force-checkout to get a fresh checkout to the source directory.\n
          An existing source directory is normally reused if possible.
However it might be an issue if current checkout instructions do not follow changes in the
experiment suite configuration file. The option --force-checkout allows to get a fresh checkout
according to the current configuration file.\n
    - Use `--force-compile` to compile a fresh executable.\n
          An existing executable directory is normally reused if possible. It's an error if
current compile instructions don't match the experiment suite configuration file UNLESS the
option --force-compile is used. This option allows the user to recreate the compile script
according to the current configuration file.
    """
    run_fremake_script.fremake_run(yamlfile, platform, target, parallel, jobs, no_parallel_checkout, no_format_transfer, execute, verbose, force_checkout, force_compile, force_dockerfile)

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
              "--jobs",
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
@click.option("-v",
              "--verbose",
              is_flag = True,
              help = VERBOSE_OPT_HELP)
def create_checkout(yamlfile, platform, target, no_parallel_checkout, jobs, execute, verbose):
    """ - Write the checkout script """
    create_checkout_script.checkout_create(
        yamlfile, platform, target, no_parallel_checkout, jobs, execute, verbose)

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
def create_makefile(yamlfile, platform, target):
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
              "--jobs",
              type = int,
              metavar = '',
              default = 4,
              help = JOBS_OPT_HELP)
@click.option("-n",
              "--parallel",
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
def create_compile(yamlfile, platform, target, jobs, parallel, execute, verbose):
    """ - Write the compile script """
    create_compile_script.compile_create(
        yamlfile, platform, target, jobs, parallel, execute, verbose)

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
              help = "Build Dockerfile that has been generated by create-docker.")
def create_dockerfile(yamlfile, platform, target, no_format_transfer, execute):
    """ - Write the dockerfile """
    create_docker_script.dockerfile_create(yamlfile, platform, target, no_format_transfer, execute)

if __name__ == "__main__":
    make_cli()
