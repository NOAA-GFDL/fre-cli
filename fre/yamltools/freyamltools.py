''' fre yamltools '''

import logging
fre_logger = logging.getLogger(__name__)

import click
from fre.yamltools import combine_yamls_script
from fre.yamltools import check_yaml_script


@click.group(help = click.style(" - access fre yamltools subcommands", fg = (202,177,95) ))
def yamltools_cli():
    ''' entry point to fre yamltools click commands '''

@yamltools_cli.command()
@click.option("-y", "--yamlfile", type = str,
              help = "YAML file to be used for parsing",
              required = True )
@click.option("-e", "--experiment", type = str,
              help = "Experiment name",
              required = True )
@click.option("-p", "--platform", type = str,
              help = "Platform name",
              required = True )
@click.option("-t", "--target", type = str,
              help = "Target name",
              required = True )
@click.option("--use", type = click.Choice(['compile','pp', 'cmor']),
              help = "Process user is combining yamls for. Can pass 'compile' or 'pp'",
              required = True )
@click.option("-o", "--output", type = str, default = None,
              help = "Output file if desired", required = False)
def combine_yamls(yamlfile,
                  experiment, platform, target,
                  use, output):
    """
    - Combine the model yaml with the compile, platform,
    experiment, and analysis yamls
    """
    fre_logger.info('calling combine_yamls_script.consolidate_yamls')
    combine_yamls_script.consolidate_yamls( yamlfile,
                                            experiment, platform, target,
                                            use, output )


@yamltools_cli.command()
@click.option("-y", "--yamlfile", type = str,
              help = "YAML file to be used for parsing",
              required = True )
def check_yaml(yamlfile):
    '''
    print a yamlfile to screen in a readable manner. this will not de-alias anchors-
    the yamlfile must have all of it's contents explicitly de-referenced and static
    '''
    check_yaml_script.yaml_check(yamlfile)

if __name__ == "__main__":
    yamltools_cli()
