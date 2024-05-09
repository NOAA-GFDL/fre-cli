import click
from .frerunexample import run_test_function

@click.group(help=" - access fre run subcommands")
def runCli():
    pass

@runCli.command()
@click.option('--uppercase', '-u', is_flag=True, help = 'Print statement in uppercase.')
@click.pass_context
def function(context, uppercase):
    """ - Execute fre run test """
    context.forward(run_test_function)

if __name__ == "__main__":
    runCli()
