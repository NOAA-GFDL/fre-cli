''' fre yamltools '''

import click
from .freyamltoolsexample import yamltools_test_function

@click.group(help=click.style(" - access fre yamltools subcommands", fg=(202,177,95)))
def yamltools_cli():
    ''' entry point to fre yamltools click commands '''

@yamltools_cli.command()
@click.option('--uppercase', '-u', is_flag=True, help = 'Print statement in uppercase.')
@click.pass_context
def function(context, uppercase):
    # pylint: disable=unused-argument
    """ - Execute fre yamltools test """
    context.forward(yamltools_test_function)

if __name__ == "__main__":
    yamltools_cli()
