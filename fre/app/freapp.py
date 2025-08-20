''' fre app calls '''

import time

import click

from .mask_atmos_plevel import mask_atmos_plevel_subtool
from .generate_time_averages.generate_time_averages import generate
from .generate_time_averages.wrapper import generate_wrapper
from .regrid_xy.regrid_xy import regrid_xy
from .generate_time_averages.combine import combine

@click.group(help=click.style(" - app subcommands", fg=(250,154,90)))
def app_cli():
    ''' entry point to fre app click commands '''

@app_cli.command()
@click.option("-i", "--input_dir",
              type = str,
              help = "`inputDir` / `input_dir` (env var) specifies input directory to regrid, " + \
                     "typically an untarredv history file archive" ,
              required = True)
@click.option("-o", "--output_dir",
              type = str,
              help = "`outputDir` / `output_dir` (env var) specifies target location for output" + \
                     " regridded files",
              required = True)
@click.option("-b", "--begin",
              type = str,
              help = "`begin` / `begin` (env var) ISO8601 datetime format specification for" + \
                     " starting date of data, part of input target file name",
              required = True)
@click.option("-tmp", "--tmp_dir",
              type = str,
              help = "`TMPDIR` / `tmp_dir` (env var) temp directory for location of file " + \
                     "read/writes",
              required = True)
@click.option("-rd", "--remap_dir",
              type = str,
              help = "`fregridRemapDir` / `remap_dir` (env var) directory containing remap file" + \
                     " for regridding",
              required = True)
@click.option("-s", "--source",
              type = str,
              help = "`source` / `source` (env var) source name for input target file name " + \
                     "within input directory to target for regridding. the value for `source` " + \
                     "must be present in at least one component's configuration fields",
              required = True)
@click.option("-g", "--grid_spec",
              type = str,
              help = "`gridSpec` / `grid_spec` (env var) file containing mosaic for regridding",
              required = True)
@click.option("--rose_config",
              type = str,
              help = "Path to Rose app configuration (to be removed soon)",
              required = True)
def regrid( input_dir, output_dir, begin, tmp_dir,
            remap_dir, source, grid_spec, rose_config ):
    ''' regrid target netcdf file '''
    regrid_xy( input_dir, output_dir, begin, tmp_dir,
               remap_dir, source, grid_spec, rose_config )

@app_cli.command()
@click.option("-i", "--infile",
              type = str,
              help = "Input NetCDF file containing pressure-level output to be masked",
              required = True)
@click.option("-o", "--outfile",
              type = str,
              help = "Output file",
              required = True)
@click.option("-p", "--psfile", # surface pressure... ps? TODO
              help = "Input NetCDF file containing surface pressure (ps)",
              required = True)
def mask_atmos_plevel(infile, outfile, psfile):
    """Mask out pressure level diagnostic output below land surface"""
    mask_atmos_plevel_subtool(infile, outfile, psfile)


@app_cli.command()
@click.option("-i", "--inf",
              type = str,
              required = True,
              help = "Input file name")
@click.option("-o", "--outf",
              type = str,
              required = True,
              help = "Output file name")
@click.option("-p", "--pkg",
              type = click.Choice(["cdo","fre-nctools","fre-python-tools"]),
              default = "cdo",
              help = "Time average approach")
@click.option("-v", "--var",
              type = str,
              default = None,
              help = "Specify variable to average")
@click.option("-u", "--unwgt",
              is_flag = True,
              default = False,
              help = "Request unweighted statistics")
@click.option("-a", "--avg_type",
              type = click.Choice(["month","seas","all"]),
              default = "all",
              help = "Type of time average to generate. \n \
                     currently, fre-nctools and fre-python-tools pkg options\n \
                     do not support seasonal and monthly averaging.\n")
def gen_time_averages(inf, outf, pkg, var, unwgt, avg_type):
    """
    generate time averages for specified set of netCDF files. 
    Example: generate-time-averages.py /path/to/your/files/
    """
    start_time = time.perf_counter()
    generate(inf, outf, pkg, var, unwgt, avg_type)
    click.echo(f'Finished in total time {round(time.perf_counter() - start_time , 2)} second(s)')

@app_cli.command()
@click.option("--cycle-point",
              type = str,
              required = True,
              help = "Beginning cycle-point in ISO8601")
@click.option("--dir",
              type = str,
              required = True,
              help = "Root directory containing the shards")
@click.option("--sources",
              type = str,
              required = True,
              help = "Sources (history file) input file, comma-separated")
@click.option("--output-interval",
              type = str,
              required = True,
              help = "ISO interval of the desired climatology")
@click.option("--input-interval",
              type = str,
              required = True,
              help = "ISO interval of the input timeseries")
@click.option("--grid",
              type = str,
              required = True,
              help = "Grid label corresponding to the shards directory (e.g. 'native' and 'regrid-xy/180_288.conserve_order2'")
@click.option("--frequency",
              type = str,
              required = True,
              help = "Frequency of desired climatology: 'mon' or 'yr'")
def gen_time_averages_wrapper(cycle_point, dir, sources, output_interval, input_interval, grid, frequency):
    """
    Wrapper for climatology tool.
    Timeaverages all variables for a desired cycle point, source, and grid.
    """
    sources_list = sources.split(',')
    generate_wrapper(cycle_point, dir, sources_list, output_interval, input_interval, grid, frequency)

@app_cli.command()
@click.option("--in-dir",
              type = str,
              required = True,
              help = "Input directory")
@click.option("--out-dir",
              type = str,
              required = True,
              help = "Output directory")
@click.option("--component",
              type = str,
              required = True,
              help = "Component name to combine")
@click.option("--begin",
              type = str,
              required = True,
              help = "Beginning year")
@click.option("--end",
              type = str,
              required = True,
              help = "Ending year")
@click.option("--frequency",
              type = str,
              required = True,
              help = "Climatology frequency; 'mon' or 'yr'")
@click.option("--interval",
              type = str,
              required = True,
              help = "Climatology interval in ISO8601")
def combine_time_averages(in_dir, out_dir, component, begin, end, frequency, interval):
    """
    Combine per-variable climatologies into one file
    """
    combine(in_dir, out_dir, component, begin, end, frequency, interval)

if __name__ == "__main__":
    app_cli()
