"""
prototype file for FRE CLI
authored by Bennett Chang | bcc2761
NOAA | GFDL
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
def freList():
    """ - Execute fre list """
    pass

@fre.group('make')
def freMake():
    """ - Execute fre make """
    pass

@fre.group('run')
def freRun():
    """ - Execute fre run """
    pass

@fre.group('postprocess')
def frePostProcess():
    """ - Execute fre postprocess """
    pass

@fre.group('check')
def freCheck():
    """ - Execute fre check """
    pass

"""
{fremake} subcommands to be processed
"""
@freMake.command()
@click.option('--uppercase', '-u', is_flag=True, help = 'Print statement in uppercase.')
def checkout(uppercase):
    """ - Execute fre make checkout """
    statement = "execute fre make checkout script" 
    if uppercase:
        statement = statement.upper()
    click.echo(statement)

@freMake.command()
@click.option('--uppercase', '-u', is_flag=True, help = 'Print statement in uppercase.')
def compile(uppercase):
    """ - Execute fre make compile """
    statement = "execute fre make compile script" 
    if uppercase:
        statement = statement.upper()
    click.echo(statement)

@freMake.command()
@click.option('--uppercase', '-u', is_flag=True, help = 'Print statement in uppercase.')
def container(uppercase):
    """ - Execute fre make container """
    statement = "execute fre make container script" 
    if uppercase:
        statement = statement.upper()
    click.echo(statement)

@freMake.command()
@click.option('--uppercase', '-u', is_flag=True, help = 'Print statement in uppercase.')
def list(uppercase):
    """ - Execute fre make list """
    statement = "execute fre make list script" 
    if uppercase:
        statement = statement.upper()
    click.echo(statement)

# this is the command that will execute all of `fre make`, but I need to test whether it will be able to pass specific flags to different areas when it they each have different flags
@freMake.command()
@click.option('--uppercase', '-u', is_flag=True, help = 'Print statement in uppercase.')
@click.pass_context
def executeAll(context, uppercase):
    """ - Execute all commands under fre make"""
    context.forward(checkout)
    context.forward(compile)
    context.forward(container)
    context.forward(list)

# @fremake.command()
# def execute_all():
#     fremake_execute_all()

# @click.group()
# def fremake_execute_all():
#     compile()
#     checkout()
#     container()
#     list()

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