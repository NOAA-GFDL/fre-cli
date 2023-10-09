import click

@click.command()
@click.argument('name')
@click.option('--uppercase', '-u', is_falg=True, help = 'Print name in uppercase.')
def hello(name, uppercase):
    #click.echo(f"Hello, {name}!")
    greeting = f"Hello, {name}!"
    if uppercase:
        greeting = greeting.upper()
    click.echo(greeting)

if __name__ == '__main__':
    hello()
