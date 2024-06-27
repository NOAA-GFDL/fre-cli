import click
from .maskAtmosPlevel import maskAtmosPlevel_subtool
from .generate_time_averages.generate_time_averages import generate

@click.group(help=click.style(" - access fre app subcommands", fg=(250,154,90)))
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


@appCli.command()
@click.option("-i", "--inf",
              type=str,
              required=True,
              help="Input file name")
@click.option("-o", "--outf",
              type=str,
              required=True,
              help="Output file name")
@click.option("-p", "--pkg",
              type=click.Choice(["cdo","fre-nctools","fre-python-tools"]),
              default="cdo",
              help="Time average approach")
@click.option("-v", "--var",
              type=str,
              default=None,
              help="Specify variable to average")
@click.option("-u", "--unwgt",
              is_flag=True,
              default=False,
              help="Request unweighted statistics")
@click.option("-a", "--avg_type",
              type=click.Choice(["month","seas","all"]),
              default="all",
              help="Type of time average to generate. \n \
                    currently, fre-nctools and fre-python-tools pkg options\n \
                    do not support seasonal and monthly averaging.\n")
@click.option("-s", "--stddev_type",
              type=click.Choice(["samp","pop","samp_mean","pop_mean"]),
              default="samp",
              help="Compute standard deviations for time-averages as well")
@click.pass_context
def gen_time_averages(context, inf, outf, pkg, var, unwgt, avg_type, stddev_type):
    """
    generate time averages for specified set of netCDF files. Example: generate-time-averages.py /path/to/your/files/
    """
    import time
    start_time=time.perf_counter()
    context.forward(generate)
    print(f'Finished in total time {round(time.perf_counter() - start_time , 2)} second(s)') # need to change to a click.echo, not sure if echo supports f strings

if __name__ == "__main__":
    appCli()
