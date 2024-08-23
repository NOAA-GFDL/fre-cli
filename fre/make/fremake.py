import click
from .createCheckout import checkout_create
from .createCompile import compile_create
from .createDocker import dockerfile_create
from .createMakefile import makefile_create
from .runFremake import fremake_run

yamlfile_opt_help = """Experiment yaml compile FILE
"""
experiment_opt_help = """Name of experiment"""
platform_opt_help = """Hardware and software FRE platform space separated list of STRING(s).
This sets platform-specific data and instructions
"""
target_opt_help   = """a space separated list of STRING(s) that defines compilation settings and
linkage directives for experiments. Predefined targets refer to groups of directives that exist in
the mkmf template file (referenced in buildDocker.py). Possible predefined targets include 'prod',
'openmp', 'repro', 'debug, 'hdf5'; however 'prod', 'repro', and 'debug' are mutually exclusive
(cannot not use more than one of these in the target list). Any number of targets can be used.
"""
parallel_opt_help = """Number of concurrent model compiles (default 1)
"""
jobs_opt_help = """Number of jobs to run simultaneously. Used for make -jJOBS and git clone
recursive --jobs=JOBS
"""
no_parallel_checkout_opt_help =  """Use this option if you do not want a parallel checkout.
The default is to have parallel checkouts.
"""
verbose_opt_help = """Get verbose messages (repeat the option to increase verbosity level)
"""



@click.group(help=click.style(" - access fre make subcommands", fg=(210,73,57)))
def make_cli():
    pass

@make_cli.command()
@click.option("-y",
              "--yamlfile",
              type = str,
              help = yamlfile_opt_help,
              required = True) # use click.option() over click.argument(), we want help statements
@click.option("-e",
              "--experiment",
              type = str,
              help = experiment_opt_help,
              required = True)
@click.option("-p",
              "--platform",
              multiple = True, # replaces nargs = -1, since click.option()
              type = str,
              help = platform_opt_help, required = True)
@click.option("-t", "--target",
              multiple = True, # replaces nargs = -1, since click.option()
              type = str,
              help = target_opt_help,
              required = True)
@click.option("-n",
              "--parallel",
              type = int,
              metavar = '',
              default = 1,
              help = parallel_opt_help)
@click.option("-j",
              "--jobs",
              type = int,
              metavar = '',
              default = 4,
              help = jobs_opt_help)
@click.option("-npc",
              "--no-parallel-checkout",
              is_flag = True,
              help = no_parallel_checkout_opt_help)
@click.option("-v",
              "--verbose",
              is_flag = True,
              help = verbose_opt_help)
@click.pass_context
def run_fremake(context, experiment, yamlfile, platform, target, parallel, jobs, no_parallel_checkout, verbose):
    """ - Perform all fremake functions to run checkout and compile model"""
    context.forward(fremake_run)

####
@make_cli.command()
@click.option("-y",
              "--yamlfile",
              type = str,
              help = yamlfile_opt_help,
              required = True) # use click.option() over click.argument(), we want help statements
@click.option("-e",
              "--experiment",
              type = str,
              help = experiment_opt_help,
              required = True)
@click.option("-p",
              "--platform",
              multiple = True, # replaces nargs = -1, since click.option()
              type = str,
              help = platform_opt_help,
              required = True)
@click.option("-t", "--target",
              multiple = True, # replaces nargs = -1, since click.option()
              type = str,
              help = target_opt_help,
              required = True)
@click.option("-j",
              "--jobs",
              type = int,
              metavar = '',
              default = 4,
              help = jobs_opt_help)
@click.option("-npc",
              "--no-parallel-checkout",
              is_flag = True,
              help = no_parallel_checkout_opt_help)
@click.option("--execute",
              is_flag = True,
              default = False,
              help = "Use this to run the created checkout script.")
@click.option("-v",
              "--verbose",
              is_flag = True,
              help = verbose_opt_help)
@click.pass_context
def create_checkout(context,yamlfile,experiment,platform,target,no_parallel_checkout,jobs,execute,verbose):
    """ - Write the checkout script """
    context.forward(checkout_create)

#####
@make_cli.command
@click.option("-y",
              "--yamlfile",
              type = str,
              help = yamlfile_opt_help,
              required = True) # use click.option() over click.argument(), we want help statements
@click.option("-e",
              "--experiment",
              type = str,
              help = experiment_opt_help,
              required = True)
@click.option("-p",
              "--platform",
              multiple = True, # replaces nargs = -1, since click.option()
              type = str,
              help = platform_opt_help, required = True)
@click.option("-t", "--target",
              multiple = True, # replaces nargs = -1, since click.option()
              type = str,
              help = target_opt_help,
              required = True)
@click.pass_context
def create_makefile(context,experiment,yamlfile,platform,target):
    """ - Write the makefile """
    context.forward(makefile_create)

#####

@make_cli.command
@click.option("-y",
              "--yamlfile",
              type = str,
              help = yamlfile_opt_help,
              required = True) # use click.option() over click.argument(), we want help statements
@click.option("-e",
              "--experiment",
              type = str,
              help = experiment_opt_help,
              required = True)
@click.option("-p",
              "--platform",
              multiple = True, # replaces nargs = -1, since click.option()
              type = str,
              help = platform_opt_help, required = True)
@click.option("-t", "--target",
              multiple = True, # replaces nargs = -1, since click.option()
              type = str,
              help = target_opt_help,
              required = True)
@click.option("-j",
              "--jobs",
              type = int,
              metavar = '',
              default = 4,
              help = jobs_opt_help)
@click.option("-n",
              "--parallel",
              type = int,
              metavar = '', default = 1,
              help = parallel_opt_help)
@click.option("--execute",
              is_flag = True,
              default = False,
              help = "Use this to run the created checkout script.")
@click.option("-v",
              "--verbose",
              is_flag = True,
              help = verbose_opt_help)
@click.pass_context
def create_compile(context,experiment,yamlfile,platform,target,jobs,parallel,execute,verbose):
    """ - Write the compile script """
    context.forward(compile_create)

@make_cli.command
@click.option("-y",
              "--yamlfile",
              type = str,
              help = yamlfile_opt_help,
              required = True) # use click.option() over click.argument(), we want help statements
@click.option("-e",
              "--experiment",
              type = str,
              help = experiment_opt_help,
              required = True) 
@click.option("-p",
              "--platform",
              multiple = True, # replaces nargs = -1, since click.option()
              type = str,
              help = platform_opt_help, required = True)
@click.option("-t", "--target",
              multiple = True, # replaces nargs = -1, since click.option()
              type = str,
              help = target_opt_help,
              required = True)
@click.option("--execute",
              is_flag = True,
              help = "Build Dockerfile that has been generated by create-docker.")
@click.pass_context
def create_dockerfile(context,experiment,yamlfile,platform,target,execute):
    """ - Write the dockerfile """
    context.forward(dockerfile_create)


if __name__ == "__main__":
    make_cli()
