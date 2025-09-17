''' fre app calls '''

import time

import click

from .mask_atmos_plevel.mask_atmos_plevel import mask_atmos_plevel_subtool
from .generate_time_averages.generate_time_averages import generate
from .regrid_xy.regrid_xy import regrid_xy
from .remap_pp_components.remap_pp_components import remap_pp_components

@click.group(help=click.style(" - app subcommands", fg=(250,154,90)))
def app_cli():
    ''' entry point to fre app click commands '''

@app_cli.command()
@click.option("-i", "--input-dir",
              type = str,
              help = "Input directory",
              required = True)
@click.option("-o", "--output-dir",
              type = str,
              help = "Output directory",
              required = True)
@click.option("-b", "--begin-date",
              type = str,
              help = "ISO8601 date format; date to begin post-processing data",
              required = True)
@click.option("-c", "--current-chunk",
              type = str,
              help = "Current chunk to post-process",
              required = True)
@click.option("-p", "--product",
              type = click.Choice(['ts', 'av', 'static']),
              help = " Variable to define time-series, time-averaging or static",
              required = True)
@click.option("-ppc", "--pp-component",
              type = str,
              help = "Component to be post-processed",
              required = True)
@click.option("-cp", "--copy-tool",
              type = click.Choice(['gcp','cp']),
              help = "Tool to use for copying files; gcp can be used in on gfdl systems where gcp is available",
              required = False)
@click.option("-y", "--yaml-config",
              type = str,
              help = "Path of yaml configuration file",
              required =  True)
@click.option("-em", "--ens-mem",
              type = str,
              help = "Ensemble member number as XX",
              required = False)
@click.option("-tsw", "--ts-workaround",
              type = click.Choice(['True','False']),
              default = None,
              help = "Time series workaround variable",
              required = False)

def remap(input_dir, output_dir, begin_date, current_chunk,
          product, pp_component, copy_tool, yaml_config,
          ts_workaround, ens_mem):
    ''' Remap netcdf files to an updated output directory structure '''
    remap_pp_components(input_dir, output_dir, begin_date, current_chunk,
                        product, pp_component, copy_tool, yaml_config,
                        ts_workaround, ens_mem)

@app_cli.command()
@click.option("--yamlfile",
              type = str,
              help = "Path to yaml configuration file",
              required = True)
@click.option("-i", "--input_dir",
              type = str,
              help = "`inputDir` / `input_dir` (env var) specifies input directory to regrid, " + \
                     "typically an untarred history file archive" ,
              required = True)
@click.option("-o", "--output_dir",
              type = str,
              help = "`outputDir` / `output_dir` (env var) specifies target location for output" + \
                     " regridded files",
              required = True)
@click.option("-w", "--work_dir",
              type = str,
              help = "`TMPDIR` / `workdir_dir` (env var) work directory for location of file " + \
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
@click.option("-id", "--input_date",
              type = str,
              help = "`input_date` / `input_date` (env var) ISO8601 datetime format specification for" + \
                     " starting date of data, part of input target file name")
def regrid(yamlfile, input_dir, output_dir, work_dir,
           remap_dir, source, input_date):
    ''' regrid target netcdf file '''
    regrid_xy(yamlfile, input_dir, output_dir, work_dir,
              remap_dir, source, input_date)


@app_cli.command()
@click.option("-i", "--infile",
              type = str,
              help = "Input NetCDF file containing pressure-level output to be masked",
              required = True)
@click.option("-o", "--outfile",
              type = str,
              help = "Output file",
              required = True)
@click.option("-p", "--psfile",
              help = "Input NetCDF file containing surface pressure (ps)",
              type = str,
              required = True)
def mask_atmos_plevel(infile, psfile, outfile):
    """Mask diagnostic 'infile' below surface pressure 'psfile'"""
    mask_atmos_plevel_subtool(infile, psfile, outfile)


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
    """
    start_time = time.perf_counter()
    generate(inf, outf, pkg, var, unwgt, avg_type)
    click.echo(f'Finished in total time {round(time.perf_counter() - start_time , 2)} second(s)')
