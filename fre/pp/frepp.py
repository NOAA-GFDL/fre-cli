"""
Click Command Line Interface for FRE Post-Processing (`fre pp`).

This module registers all subcommands under the `fre pp` Click group for managing
post-processing workflow lifecycles (checkout, configure, validate, install, run,
status, trigger, validation, and NetCDF processing).
"""

import logging
import click

from . import checkout_script
from . import configure_script_yaml
from . import validate_script
from . import histval_script
from . import ppval_script
from . import install_script
from . import run_script
from . import nccheck_script
from . import trigger_script
from . import status_script
from . import wrapper_script
from . import split_netcdf_script
from . import rename_split_script

fre_logger = logging.getLogger(__name__)


@click.group(help=click.style(" - Post-processing (pp) workflow tools and subcommands", fg=(57, 139, 210)))
def pp_cli():
    """Entry point for all `fre pp` subcommands."""


@pp_cli.command()
@click.option("-e", "--experiment", type=str, required=True, help="Post-processing experiment name (e.g., c96L65_am5f4b4r0_amip)")
@click.option("-p", "--platform", type=str, required=True, help="Platform name (e.g., gfdl.ncrc5-deploy)")
@click.option("-t", "--target", type=str, required=True, help="Target options (e.g., prod-openmp)")
def status(experiment, platform, target):
    """Report the execution status of a post-processing Cylc workflow."""
    status_script.status_subtool(experiment, platform, target)


@pp_cli.command()
@click.option("-e", "--experiment", type=str, required=True, help="Post-processing experiment name")
@click.option("-p", "--platform", type=str, required=True, help="Platform name")
@click.option("-t", "--target", type=str, required=True, help="Target options")
@click.option("--pause", is_flag=True, default=False, help="Pause the workflow immediately upon start up")
@click.option("--no_wait", is_flag=True, default=False, help="Do not wait to confirm workflow submission success with Cylc scheduler")
def run(experiment, platform, target, pause, no_wait):
    """Start or trigger execution of an installed post-processing workflow."""
    run_script.pp_run_subtool(experiment, platform, target, pause, no_wait)


@pp_cli.command()
@click.option("-e", "--experiment", type=str, required=True, help="Post-processing experiment name")
@click.option("-p", "--platform", type=str, required=True, help="Platform name")
@click.option("-t", "--target", type=str, required=True, help="Target options")
def validate(experiment, platform, target):
    """Validate post-processing workflow directory configurations and suite definitions."""
    validate_script.validate_subtool(experiment, platform, target)


@pp_cli.command()
@click.option("-e", "--experiment", type=str, required=True, help="Post-processing experiment name")
@click.option("-p", "--platform", type=str, required=True, help="Platform name")
@click.option("-t", "--target", type=str, required=True, help="Target options")
def install(experiment, platform, target):
    """Install a workflow configuration from ~/cylc-src to ~/cylc-run."""
    install_script.install_subtool(experiment, platform, target)


@pp_cli.command()
@click.option("-y", "--yamlfile", type=str, required=True, help="Path to input post-processing YAML file")
@click.option("-e", "--experiment", type=str, required=True, help="Post-processing experiment name")
@click.option("-p", "--platform", type=str, required=True, help="Platform name")
@click.option("-t", "--target", type=str, required=True, help="Target options")
def configure_yaml(yamlfile, experiment, platform, target):
    """Generate rose-suite.conf and consolidated YAML in ~/cylc-src from input YAML."""
    configure_script_yaml.yaml_info(yamlfile, experiment, platform, target)


@pp_cli.command()
@click.option("-e", "--experiment", type=str, required=True, help="Post-processing experiment name")
@click.option("-p", "--platform", type=str, required=True, help="Platform name")
@click.option("-t", "--target", type=str, required=True, help="Target options")
@click.option("-b", "--branch", type=str, required=False, default=None, help="Git branch/tag to checkout from fre-workflows (defaults to fre package version)")
def checkout(experiment, platform, target, branch=None):
    """Clone or verify fre-workflows repository template in ~/cylc-src."""
    checkout_script.checkout_template(experiment, platform, target, branch)


@pp_cli.command()
@click.option("--file_path", "-f", type=str, required=True, help="Path to target netCDF (.nc) file")
@click.option("--num_steps", "-n", type=str, required=True, help="Expected number of time records")
def nccheck(file_path, num_steps):
    """Verify that a netCDF (.nc) file contains the expected number of timesteps."""
    nccheck_script.check(file_path, num_steps)


@pp_cli.command()
@click.option('--history', '-hist', required=True, help="Path to directory containing history output files")
@click.option('--date_string', '-d', required=True, help="Date prefix string as formatted in NetCDF filenames (e.g., 00010101)")
@click.option('--warn', '-w', is_flag=True, default=False, help="Issue warning log instead of raising exception if diag_manifest files are missing")
def histval(history, date_string, warn):
    """Validate timestep counts across history NetCDF files using diag_manifest metadata."""
    histval_script.validate(history, date_string, warn)


@pp_cli.command()
@click.option('-i', '--inputdir', required=True, help='Source directory containing multi-variable netCDF files to split')
@click.option('-o', '--outputdir', required=True, help='Target directory for output single-variable netCDF files')
@click.option('-c', '--component', required=False, default=None, help='Post-processing YAML component name (conflicts with --split-all-vars)')
@click.option('-s', '--history-source', required=True, default=None, help='History source file pattern from post-processing YAML')
@click.option('-y', '--yamlfile', required=False, default=None, help='Post-processing YAML file with variable filtering criteria')
@click.option('--use-subdirs', '-u', is_flag=True, default=False, help="Search subdirectories under inputdir for netCDF files")
@click.option('--split-all-vars', '-a', is_flag=True, default=False, help="Split all variables in matching files (conflicts with -c and -y)")
def split_netcdf_wrapper(inputdir, outputdir, component, history_source, use_subdirs, yamlfile, split_all_vars):
    """Split multi-variable NetCDF history files into single-variable files matching workflow specs."""
    if split_all_vars:
        none_args = [component, yamlfile]
        if any(el is not None for el in none_args):
            fre_logger.error(
                "Error in split_netcdf_wrapper arg parsing: --split-all-vars was set and "
                "one or more mutually exclusive options (--component, --yamlfile) were also set!"
            )
    split_netcdf_script.split_netcdf(
        inputdir, outputdir, component, history_source,
        use_subdirs, yamlfile, split_all_vars
    )


@pp_cli.command()
@click.option('-f', '--file', type=str, required=True, help='Path to target multi-variable netCDF file')
@click.option('-o', '--outputdir', type=str, required=True, help='Directory to store split single-variable files')
@click.option('-v', '--variables', type=str, required=True, help='Comma-separated variable names to extract, or "all"')
def split_netcdf(file, outputdir, variables):
    """Split a single NetCDF file into individual per-variable NetCDF files."""
    split_netcdf_script.split_file_xarray(file, outputdir, variables)


@pp_cli.command()
@click.option('--path', '-p', required=True, help="Path to post-processed time-series NetCDF file")
def ppval(path):
    """Estimate expected timesteps from filename date range/frequency and run nccheck validation."""
    ppval_script.validate(path)


@pp_cli.command()
@click.option("-e", "--experiment", type=str, required=True, help="Post-processing experiment name")
@click.option("-p", "--platform", type=str, required=True, help="Platform name")
@click.option("-T", "--target", type=str, required=True, help="Target options")
@click.option("-c", "--config-file", type=str, required=True, help="Path to XML or YAML post-processing configuration file")
@click.option("-b", "--branch", required=False, default=None, help="fre-workflows branch/tag to clone")
@click.option("-t", "--time", required=False, default=None, help="Target time chunk to trigger post-processing")
def all(experiment, platform, target, config_file, branch, time):
    """Execute all FRE post-processing pipeline steps in sequential order."""
    fre_logger.info('(frepp.wrapper) forwarding context to wrapper.run_all_fre_pp_steps via click...')
    wrapper_script.run_all_fre_pp_steps(experiment, platform, target, config_file, branch, time)
    fre_logger.info('(frepp.wrapper) done forwarding context to wrapper.run_all_fre_pp_steps via click.')


@pp_cli.command()
@click.option("-e", "--experiment", type=str, required=True, help="Post-processing experiment name")
@click.option("-p", "--platform", type=str, required=True, help="Platform name")
@click.option("-T", "--target", type=str, required=True, help="Target options")
@click.option("-t", "--time", required=True, help="Target time chunk string (e.g., 00010101)")
def trigger(experiment, platform, target, time):
    """Trigger post-processing workflow execution for a specific time chunk of history files."""
    trigger_script.trigger(experiment, platform, target, time)


@pp_cli.command()
@click.option("-i", "--input-dir", type=str, required=True, help="Input directory containing split files")
@click.option("-o", "--output-dir", type=str, required=True, help="Output directory for renamed time-series files")
@click.option("-c", "--component", type=str, required=True, help="Component name to process")
@click.option("-u", '--use-subdirs', is_flag=True, default=False, help="Search subdirectories under inputdir")
@click.option("-d", "--diag-manifest", multiple=True, type=click.Path(exists=True), help="Path(s) to FMS diag manifest file(s)")
def rename_split(input_dir, output_dir, component, use_subdirs, diag_manifest):
    """Create per-variable time-series files from split intermediate shards."""
    rename_split_script.rename_split(input_dir, output_dir, component, use_subdirs, diag_manifest)