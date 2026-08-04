""" This module defines the ``fre catalog`` click subcommands.

The frecatalog module generates CSV and JSON files to catalog the database of climate model output files and metadata generated,
for example, from an experiment run or from post-processing. Both CSV and JSON files can be used with Intake_ESM APIs to discover,
query, and load data consistently.

The cataloging ecosystem is composed of three main components:

1. Catalog Specification (JSON): A single file that provides metadata about 
   the catalog (variable_id, experiment, file paths, etc.).
2. Catalog (CSV): A file that acts as the index file for the data collection, providing 
   the paths to the data files and their associated metadata at a user-defined granularity.
   (Additional information to be added)
3. Intake-ESM API: Provides a Pythonic interface to query the catalog's contents and 
   automatically loads the queried results into an xarray dataset object for analysis."""

import click

from catalogbuilder.scripts import gen_intake_gfdl
from catalogbuilder.scripts import compval
from catalogbuilder.scripts import combine_cats


@click.group(help=click.style(" - catalog subcommands", fg=(64,94,213)))
def catalog_cli():
    """This click command group contains the ``fre catalog`` subcommands."""



@catalog_cli.command()
#TODO arguments dont have help message. So consider changing arguments to options?
@click.argument('input_path', required = False, nargs = 1)
#, help = 'The directory path with the datasets to be cataloged. E.g a GFDL PP path till /pp')
@click.argument('output_path', required = False, nargs = 1)
#, help = 'Specify output filename suffix only. e.g. catalog')
@click.option('--config', required = False, type = click.Path(exists = True), nargs = 1,
              help = 'Path to your yaml config, Use the config_template in intakebuilder repo')
@click.option('--filter_realm',  nargs = 1)
@click.option('--filter_freq',  nargs = 1)
@click.option('--filter_chunk',  nargs = 1)
@click.option('--verbose', is_flag = True, default = False, help = "Prints additional diagnostic information during catalog generation")
@click.option('--overwrite', is_flag = True, default = False, help = "Overwrite existing catalog output files")
@click.option('--append', is_flag = True, default = False, help = "Append to existing catalog output CSV file")
@click.option('--slow', is_flag = True, default = False,
    help = "Open NetCDF files to retrieve additional vocabulary (standard_name and intrafile static variables")
@click.option('--strict', is_flag = True, default = False,
    help = "Ensure output catalog is strictly compliant with schema")
@click.pass_context
def build(context, input_path = None, output_path = None, config = None, filter_realm = None,
          filter_freq = None, filter_chunk = None, verbose = False, overwrite = False,
          append = False, slow = False, strict = False):
    # pylint: disable=unused-argument
    """Build catalog CVS and JSON files. The input_path contains the files that make up the database and can be accessed by Intake-ESM."""
    context.forward(gen_intake_gfdl.create_catalog_cli)

@catalog_cli.command()
@click.argument('json_path', nargs = 1 , required = True)
@click.argument('json_template_path', nargs = 1 , required = False)
@click.option('--vocab', is_flag=True, default = False,
              help="Validates catalog vocabulary")
@click.option('-pg','--proper_generation', is_flag=True, default = False,
              help="Ensures that catalog has been 'properly generated' (No empty columns, reflects template)")
@click.option('-tf', '--test-failure', is_flag=True, default = False,
              help="Errors are only printed. Program will not exit.")
@click.pass_context
def validate(context, json_path, json_template_path, vocab, proper_generation, test_failure):
    # pylint: disable=unused-argument
    """Validate catalogs against controlled vocabulary as provided by particular JSON schemas
    per vocabulary type (vocabulary validation) OR Validate a catalog against catalog schema
    template (proper generation checking) """
    context.forward(compval.main)

@catalog_cli.command()
@click.option('--input', required = True, multiple = True,
              help = 'Catalog json files to be merged, space-separated')
@click.option('--output', required = True, nargs = 1,
              help = 'Merged catalog')
@click.pass_context
def merge(context, input, output):
    """Merge two or more catalogs into one catalog file."""
    context.invoke(combine_cats.combine_cats, inputfiles=input, output_path=output)
