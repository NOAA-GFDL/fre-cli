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



@click.group(help=click.style(" - access fre make subcommands", fg=(210,73,57)))
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
              multiple = True, # replaces nargs = -1, since click.option()
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
              help = NO_PARALLEL_CHECKOUIT_OPT_HELP)
@click.option("-v",
              "--verbose",
              is_flag = True,
              help = VERBOSE_OPT_HELP)
@click.pass_context
def run_fremake(context, yamlfile, platform, target, parallel, jobs, no_parallel_checkout, verbose):
    # pylint: disable=unused-argument
    """ - Perform all fremake functions to run checkout and compile model"""
    context.forward(run_fremake_script._fremake_run)

####
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
              help = no_parallel_checkout_OPT_HELP)
@click.option("--execute",
              is_flag = True,
              default = False,
              help = "Use this to run the created checkout script.")
@click.option("-v",
              "--verbose",
              is_flag = True,
              help = VERBOSE_OPT_HELP)
@click.pass_context
def create_checkout(context,yamlfile,platform,target,no_parallel_checkout,jobs,execute,verbose):
    # pylint: disable=unused-argument
    """ - Write the checkout script """
    context.forward(create_checkout_script._checkout_create)

#####
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
@click.pass_context
def create_makefile(context,yamlfile,platform,target):
    # pylint: disable=unused-argument
    """ - Write the makefile """
    context.forward(create_makefile_script._makefile_create)

#####

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
@click.pass_context
def create_compile(context,yamlfile,platform,target,jobs,parallel,execute,verbose):
    # pylint: disable=unused-argument
    """ - Write the compile script """
    context.forward(create_compile_script._compile_create)

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
@click.option("--execute",
              is_flag = True,
              help = "Build Dockerfile that has been generated by create-docker.")
@click.pass_context
def create_dockerfile(context,yamlfile,platform,target,execute):
    # pylint: disable=unused-argument
    """ - Write the dockerfile """
    context.forward(create_docker_script._dockerfile_create)

if __name__ == "__main__":
    make_cli()
