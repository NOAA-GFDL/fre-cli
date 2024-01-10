import click

@click.command()
@click.option('--uppercase', '-u', is_flag=True, help = 'Print statement in uppercase.')
def function(uppercase):
    """ - Execute fre yamltools function """
    statement = "execute fre yamltools function" 
    if uppercase:
        statement = statement.upper()
    click.echo(statement)

if __name__ == "__main__":
    function()
