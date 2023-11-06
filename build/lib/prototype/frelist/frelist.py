"""
experimentation file for integrating one file's functions into main prototype fre file
authored by Bennett.Chang@noaa.gov | bcc2761
NOAA | GFDL
"""

import click

# Create a CLI group and add the subcommands to it
@click.group()
def list():
    pass

@list.command()
@click.option('--uppercase', '-u', is_flag=True, help='Print statement in uppercase.')
def testfunction1(uppercase):
    """Execute fre list testfunction1."""
    statement = "testingtestingtestingtesting"
    if uppercase:
        statement = statement.upper()
    click.echo(statement)

@list.command()
@click.option('--uppercase', '-u', is_flag=True, help='Print statement in uppercase.')
def testfunction2(uppercase):
    """Execute fre list testfunction2."""
    statement = "testingtestingtestingtesting"
    if uppercase:
        statement = statement.upper()
    click.echo(statement)

if __name__ == '__main__':
    list()