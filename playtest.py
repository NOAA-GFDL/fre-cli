"""
Simple program hence 'playtest' to familiarize with Click in general, likely going to be moved to /brainstorming directory and replaced by actual prototype program
"""

import click

# click group allows for multiple functions to be called via same script
@click.group()
def cli():
    pass

# first function, hello
@click.command()
@click.argument('name')
@click.option('--uppercase', '-u', is_flag=True, help = 'Print name in uppercase.')
def hello(name, uppercase):
    #click.echo(f"Hello, {name}!")
    greeting = f"Hello, {name}!"
    if uppercase:
        greeting = greeting.upper()
    click.echo(greeting)

# second function, goodbye
@click.command()
@click.argument('name')
@click.option('--uppercase', '-u', is_flag=True, help = 'Print name in uppercase.')
def goodbye(name, uppercase):
    #click.echo(f"Hello, {name}!")
    farewell = f"Goodbye, {name}!"
    if uppercase:
        farewell = farewell.upper()
    click.echo(farewell)

# add your functions to the click group
cli.add_command(hello)
cli.add_command(goodbye)

if __name__ == '__main__':
    cli()