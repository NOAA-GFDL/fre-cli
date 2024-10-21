''' fre list '''

import click

from .frelistexample import list_test_function

@click.group(help=click.style(" - access fre list subcommands", fg=(232,204,91)))
def list_cli():
    ''' entry point to fre list click commands '''

@list_cli.command()
@click.option('--uppercase', '-u', is_flag=True, help = 'Print statement in uppercase.')
@click.pass_context
def function(context, uppercase):
    # pylint: disable=unused-argument
    """ - Execute fre list test """
    context.forward(list_test_function)

if __name__ == "__main__":
    list_cli()
