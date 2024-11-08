''' fre yamltools '''

import click
from .combine_yamls import _consolidate_yamls

@click.group(help=click.style(" - access fre yamltools subcommands", fg=(202,177,95)))
def yamltools_cli():
    ''' entry point to fre yamltools click commands '''

@yamltools_cli.command()
@click.option("-y",
              "--yamlfile",
              type=str,
              help="YAML file to be used for parsing",
              required=True)
@click.option("-e",
              "--experiment",
              type=str,
              help="Experiment name")
@click.option("-p",
              "--platform",
              type=str,
              help="Platform name",
              required=True)
@click.option("-t",
                "--target",
                type=str,
                help="Target name",
                required=True)
@click.option("--use",
              type=click.Choice(['compile','pp']),
              help="Process user is combining yamls for. Can pass 'compile' or 'pp'",
              required=True)
@click.pass_context
def combine_yamls(context,yamlfile,experiment,platform,target,use):
    """ 
    - Combine the model yaml with the compile, platform,
    experiment, and analysis yamls
    """
    context.forward(_consolidate_yamls)

if __name__ == "__main__":
    yamltools_cli()
