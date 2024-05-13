import click
from .maskAtmosPlevel import maskAtmosPlevel_subtool

@click.group(help=" - access fre app subcommands")
def appCli():
    pass

@appCli.command()
@click.option("-i", "--infile",
              type=str,
              help="Input NetCDF file containing pressure-level output to be masked",
              required=True)
@click.option("-o", "--outfile",
              type=str,
              help="Output file",
              required=True)
@click.option("-p", "--psfile",
              help="Input NetCDF file containing surface pressure (ps)",
              required=True)
@click.pass_context
def mask_atmos_plevel(context, infile, outfile, psfile):
    """Mask out pressure level diagnostic output below land surface"""
    context.forward(maskAtmosPlevel_subtool)

if __name__ == "__main__":
    appCli()
