"""
experimentation file for integrating one file's functions into main prototype fre file
authored by Bennett.Chang@noaa.gov | bcc2761
NOAA | GFDL
"""

import click

"""
{frelist} subcommands to be processed
"""
@click.command()
@click.option('--uppercase', '-u', is_flag=True, help = 'Print statement in uppercase.')
def listFunction(uppercase):
    """ - Execute fre list checkout """
    statement = "execute fre list function script" 
    if uppercase:
        statement = statement.upper()
    click.echo(statement)

