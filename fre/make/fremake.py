import click
from .createCheckout import checkout_create
from .createCompile import compile_create
from .createDocker import dockerfile_create
from .createMakefile import makefile_create
from .runFremake import fremake_run

@click.group(help=click.style(" - access fre make subcommands", fg=(210,73,57)))
def makeCli():
    pass

@makeCli.command()
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
@makeCli.command()
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
@makeCli.command
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

@makeCli.command
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

@makeCli.command
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


if __name__ == "__main__":
    makeCli()
