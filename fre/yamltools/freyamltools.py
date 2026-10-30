''' click entry-point to 'fre yamltools' calls'''
import sys
import logging
#import ast
import click
from fre.yamltools import combine_yamls_script
fre_logger = logging.getLogger(__name__)

@click.group(help=click.style(" - yamltools subcommands", fg=(202,177,95)))
def yamltools_cli():
    ''' entry point to fre yamltools click commands '''

@yamltools_cli.command()
@click.option("-y", "--yamls",
              type=str,
              help="Comma separated string of paths of YAML file to be combined")
@click.option("-e", "--experiment",
              type=str,
              help="Experiment name")
@click.option("-p", "--platform",
              type=str,
              help="Platform name")
@click.option("-t", "--target",
              type=str,
              help="Target name")
@click.option("-o", "--output", type=str,
              help="Output")
@click.option("--no-clean", type=bool,
              help="Do not remove anything from the combined, resolved YAML file.")
def combine(yamls, experiment, platform, target, output, no_clean): 
    """
    - Combine the model yaml with the compile, platform,
    experiment, and analysis yamls
    """
    # if not piped from fre list yamls
    yaml_paths = []
    if yamls:
        fre_logger.info("NOT PIPED")
        yaml_paths = yamls
    else:
        fre_logger.info("PIPED")
        # stdout from last tool adds a newline for some reason
        yaml_paths = sys.stdin.read().strip()

    combine_yamls_script.yamltools_combine_subtool(yaml_paths, experiment, platform, target, output, no_clean)

#@yamltools_cli.command()
#@click.option("-y", "--yaml",
#              type=str,
#              help="Combined, resolved YAML file to be used for parsing",
#              required=True)
#@click.option("-js", "--json-schema",
#              type=str,
#              help="JSON schema file used to validate the YAML",
#              required=True)
#def validate(yaml, schema):
#    """
#    - Validate the combined, resolved YAML file against a JSON schema
#    """
#    validate_script.validate_subtool(yaml, schema)
