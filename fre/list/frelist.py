''' fre list '''

import click

from .frelistexample import list_test_function

@click.group(help=click.style(" - access fre list subcommands (not implemented yet!)", fg=(232,204,91)))
def list_cli():
    ''' entry point to fre list click commands '''

@list_cli.command()
@click.option('--uppercase', '-u', is_flag=True, help = 'Print statement in uppercase.')
def function(uppercase):
    """ - Execute fre list test """
    list_test_function(uppercase)
    raise NotImplementedError('fre list has not been implemented yet!')

if __name__ == "__main__":
    list_cli()
