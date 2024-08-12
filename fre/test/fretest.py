'''
entry point for fre test subcommands
'''

import click
from .fretestexample import test_test_function

@click.group(help=click.style(" - access fre test subcommands", fg=(92,164,29)))
def test_cli():
    ''' entry point to fre test click commands '''

@test_cli.command()
@click.option('--uppercase', '-u', is_flag=True, help = 'Print statement in uppercase.')
@click.pass_context
def function(context, uppercase):
    # pylint: disable=unused-argument
    """ - Execute fre test test """
    context.forward(test_test_function)

if __name__ == "__main__":
    test_cli()
