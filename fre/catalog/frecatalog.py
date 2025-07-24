'''
entry point for fre catalog subcommands
'''

import click

from catalogbuilder.scripts import gen_intake_gfdl
from catalogbuilder.tests import compval
from catalogbuilder.scripts import combine_cats


@click.group(help=click.style(" - catalog subcommands", fg=(64,94,213)))
def catalog_cli():
    ''' entry point for click into fre catalog cli calls '''



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
@click.option('--verbose', is_flag = True, default = False)
@click.option('--overwrite', is_flag = True, default = False)
@click.option('--append', is_flag = True, default = False)
@click.option('--slow', is_flag = True, default = False,
    help = "Open NetCDF files to retrieve additional vocabulary (standard_name and intrafile static variables")
@click.option('--strict', is_flag = True, default = False,
    help = "Ensure output catalog is strictly compliant with schema")
@click.pass_context
def build(context, input_path = None, output_path = None, config = None, filter_realm = None,
          filter_freq = None, filter_chunk = None, verbose = False, overwrite = False, append = False, slow = False, strict = False):
    # pylint: disable=unused-argument
    """ - Generate .csv and .json files for catalog """
    context.forward(gen_intake_gfdl.create_catalog_cli)

@catalog_cli.command()
@click.argument('json_path', nargs = 1 , required = True)
@click.argument('json_template_path', nargs = 1 , required = False)
@click.option('-tf', '--test-failure', is_flag=True, default = False,
              help="Errors are only printed. Program will not exit.")
@click.pass_context
def validate(context, json_path, json_template_path, test_failure):
    # pylint: disable=unused-argument
    """ - Validate a catalog against catalog schema """
    context.forward(compval.main)

@catalog_cli.command()
@click.option('--input', required = True, multiple = True,
              help = 'Catalog json files to be merged, space-separated')
@click.option('--output', required = True, nargs = 1,
              help = 'Merged catalog')
@click.pass_context
def merge(context, input, output):
    """ - Merge two or more more catalogs into one """
    context.invoke(combine_cats.combine_cats, inputfiles=input, output_path=output)

if __name__ == "__main__":
    catalog_cli()
