"""
prototype file for fre CLI
authored by Bennett Chang | bcc2761
"""

import click

"""
click group allows for multiple functions to be called via same script
"""
@click.group()
def fre():
    pass

"""
this is a nested group within the {fre} group that allows commands to be processed
"""
@fre.group('list')
def frelist():
    pass

@fre.group('make')
def fremake():
    pass

@fre.group('run')
def frerun():
    pass

@fre.group('postprocess')
def frepostprocess():
    pass

@fre.group('check')
def frecheck():
    pass

"""
{fremake} subcommands to be processed
"""
@fremake.command()
@click.option('--uppercase', '-u', is_flag=True, help = 'Print name in uppercase.')
def checkout(uppercase):
    statement = "execute fre make checkout script" 
    if uppercase:
        statement = statement.upper()
    click.echo(statement)

@fremake.command()
def compile():
    click.echo("execute fre make compile script")

@fremake.command()
def container():
    click.echo("execute fre make container script")

@fremake.command()
def list():
    click.echo("execute fre make list script")
    

if __name__ == '__main__':
    fre()