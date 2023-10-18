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
@click.option('--uppercase', '-u', is_flag=True, help = 'Print statement in uppercase.')
def checkout(uppercase):
    statement = "execute fre make checkout script" 
    if uppercase:
        statement = statement.upper()
    click.echo(statement)

@fremake.command()
@click.option('--uppercase', '-u', is_flag=True, help = 'Print statement in uppercase.')
def compile(uppercase):
    statement = "execute fre make compile script" 
    if uppercase:
        statement = statement.upper()
    click.echo(statement)

@fremake.command()
@click.option('--uppercase', '-u', is_flag=True, help = 'Print statement in uppercase.')
def container(uppercase):
    statement = "execute fre make container script" 
    if uppercase:
        statement = statement.upper()
    click.echo(statement)

@fremake.command()
@click.option('--uppercase', '-u', is_flag=True, help = 'Print statement in uppercase.')
def list(uppercase):
    statement = "execute fre make list script" 
    if uppercase:
        statement = statement.upper()
    click.echo(statement)

# def execute_all_subcommands():
#     checkout(False)  # Call checkout with uppercase option set to False
#     compile(False)   # Call compile with uppercase option set to False
#     container(False) # Call container with uppercase option set to False
#     list(False)      # Call list with uppercase option set to False

# @fremake.command()
# def execute_all():
#     execute_all_subcommands


if __name__ == '__main__':
    fre()