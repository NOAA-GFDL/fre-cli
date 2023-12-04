import click

@click.command()
@click.option('--uppercase', '-u', is_flag=True, help = 'Print statement in uppercase.')
def test(uppercase):
    """ - Execute fre pp test """
    statement = "execute fre pp test script" 
    if uppercase:
        statement = statement.upper()
    click.echo(statement)