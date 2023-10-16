import click
    
# click group allows for multiple functions to be called via same script
@click.group()
@click.help_option(help = 'Choose what food you would like to get started.')
def food():
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
burger.add_command(hello)

if __name__ == '__main__':
    food()