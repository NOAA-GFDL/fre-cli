import click
from createCheckout import checkout_create

@click.group(help="Fre fake lazy group for testing")
def fre_fake():
    pass

@fre_fake.command()
def

@fre_fake.command()
@click.option("-y",                                                                                                "--yamlfile",
              type=str,                                                                                            help="Experiment yaml compile FILE",
              required=True) # used click.option() instead of click.argument() because we want to have help statements
@click.option("-p",
              "--platform",                                                                                        multiple=True, #replaces nargs=-1 since we are using click.option() instead of click.argument()                                                                                                           type=str,
              help="Hardware and software FRE platform space separated list of STRING(s). This sets platform-specific data and instructions", required=True)
@click.option("-t", "--target",
              multiple=True, #replaces nargs=-1 since we are using click.option() instead of click.argument()
              type=str,
              help="FRE target space separated list of STRING(s) that defines compilation settings and linkage directives for experiments. Predefined targets refer to groups of directives that exist in the mkmf template file (referenced in buildDocker.py). Possible predefined targets include 'prod', 'openmp', 'repro', 'debug, 'hdf5'; however 'prod', 'repro', and 'debug' are mutually exclusive (cannot not use more than one of these in the target list). Any number of targets can be used.",
              required=True)
@click.option("-j",
              "--jobs",
              type=int,
              metavar='',                                                                                          default=4,
              help="Number of jobs to run simultaneously. Used for make -jJOBS and git clone recursive --jobs=JOBS")                                                                                      @click.option("-npc",
              "--no-parallel-checkout",                                                                            is_flag=True,
              help="Use this option if you do not want a parallel checkout. The default is to have parallel checkouts.")
@click.option("-e",
              "--execute",                                                                                         is_flag=True,                                                                                        default=False,                                                                                       help="Use this to run the created checkout script.")
@click.option("-v",                                                                                                "--verbose",
              is_flag=True,
              help="Get verbose messages (repeat the option to increase verbosity level)")
@click.pass_context
def create_checkout(context,yamlfile,platform,target,no_parallel_checkout,jobs,execute,verbose):
    """ - Write the checkout script """
    context.forward(checkout_create)

if __name__ == "__main__":
    fre_fake()
