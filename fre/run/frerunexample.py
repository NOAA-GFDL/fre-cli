"""
experimentation file for integrating one file's functions into main prototype fre file
authored by Bennett.Chang@noaa.gov | bcc2761
NOAA | GFDL
"""

import click

@click.command()
def run_test_function(uppercase):
    """Execute fre list testfunction2."""
    statement = "testingtestingtestingtesting"
    if uppercase:
        statement = statement.upper()
    click.echo(statement)

if __name__ == '__main__':
    run_test_function()
