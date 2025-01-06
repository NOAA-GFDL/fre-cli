''' fre check '''

import click

from .frecheckexample import check_test_function

@click.group(help=click.style(" - access fre check subcommands", fg=(162,91,232)))
def check_cli():
    ''' entry point to fre check click commands '''

@check_cli.command()
@click.option('--uppercase', '-u', is_flag=True, help = 'Print statement in uppercase.')
def function(uppercase):
    """ - Execute fre check test """
    check_test_function(uppercase)

if __name__ == "__main__":
    check_cli()
