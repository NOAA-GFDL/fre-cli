"""
Click Command Line Interface for FRE Post-Processing (`fre pp`).

The frepp module registers all subcommands under the `fre pp` Click group for managing
post-processing workflow subtools: 
- checkout: Clones fre-workflow repository into ~/cylc-src/[WORKFLOW_ID]
- configure_yaml: Combines the model yaml, settings yaml, and postprocessing yaml files into one resolved yaml file that is then validated against an MSD-owned schema file and parsed to create the rose-suite.conf file
- validate: Validates the Cylc workflow definition (flow.cylc file)
- install: Installs the experiment workflow configuration into ~/cylc-run/[WORKFLOW_ID]
- run: Runs the experiment workflow configuration
- status: Shows the status of the Cylc workflow definition tasks
- trigger: Initiate a postprocessing task for a time chunk of history files
- nccheck: Confirms that a NetCDF file contains the expected number of time steps
- histval: Validates the time step counts of a NetCDF file compared to the FMS 'diag_manifest' yaml file during the "Stage-History" workflow step
- split_netcdf_wrapper: Runs the 'split-netcdf' tool on a pattern-matched list of NetCDF files within a directory
- split_netcdf: Split an individual NetCDF file by variable, as defined by the postprocessing yaml files
- pp_val: Determines estimated number of timesteps from a postprocessed time-series filename and runs nccheck
- all: Executes all postprocessing tasks (checkout, configure, install, run, optional triggering, and status reporting) sequentially
- rename_split: Reorganizes data according to their frequency and time interval
"""

import logging
import click
fre_logger = logging.getLogger(__name__)

# The following imports are fre tools
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



@click.group(help=click.style(" - pp subcommands", fg=(57,139,210)))
def pp_cli():
    """Entry point for all `fre pp` subcommands."""


@pp_cli.command()
@click.option("-e", "--experiment", type=str, 
              help="Experiment name",
              required=True)
@click.option("-p", "--platform", type=str, 
              help="Platform name",
              required=True)
@click.option("-t", "--target", type=str,
              help="Target name",
              required=True)
def status(experiment, platform, target):
    """Report the execution status of a post-processing Cylc workflow."""
    status_script.status_subtool(experiment, platform, target)


@pp_cli.command()
@click.option("-e", "--experiment", type=str,
              help="Experiment name",
              required=True)
@click.option("-p", "--platform", type=str,
              help="Platform name",
              required=True)
@click.option("-t", "--target", type=str,
              help="Target name",
              required=True)
@click.option("--pause", is_flag=True, default=False,
              help="Pause the workflow immediately after start up",
              required=False)
@click.option("--no_wait", is_flag=True, default=False,
              help="Do not wait to confirm workflow submission success with Cylc scheduler",
              required=False)
def run(experiment, platform, target, pause, no_wait):
    """Start or trigger execution of a Cylc-installed post-processing workflow."""
    run_script.pp_run_subtool(experiment, platform, target, pause, no_wait)


@pp_cli.command()
@click.option("-e", "--experiment", type=str,
              help="Experiment name",
              required=True)
@click.option("-p", "--platform", type=str,
              help="Platform name",
              required=True)
@click.option("-t", "--target", type=str,
              help="Target name",
              required=True)
def validate(experiment, platform, target):
    """Validate post-processing workflow directory configurations and suite definitions."""
    validate_script.validate_subtool(experiment, platform, target)


@pp_cli.command()
@click.option("-e", "--experiment", type=str,
              help="Experiment name",
              required=True)
@click.option("-p", "--platform", type=str,
              help="Platform name",
              required=True)
@click.option("-t", "--target", type=str,
              help="Target name",
              required=True)
def install(experiment, platform, target):
    """Install a workflow configuration from ~/cylc-src to ~/cylc-run."""
    install_script.install_subtool(experiment, platform, target)


@pp_cli.command()
@click.option("-y", "--yamlfile", type=str,
              help="YAML file to be used for parsing",
              required=True)
@click.option("-e", "--experiment", type=str,
              help="Experiment name",
              required=True)
@click.option("-p", "--platform", type=str,
              help="Platform name",
              required=True)
@click.option("-t", "--target", type=str,
              help="Target name",
              required=True)
def configure_yaml(yamlfile, experiment, platform, target):
    """Generate rose-suite.conf and consolidated YAML in ~/cylc-src from input YAML."""
    configure_script_yaml.yaml_info(yamlfile, experiment, platform, target)


@pp_cli.command()
@click.option("-e", "--experiment", type=str,
              help="Experiment name",
              required=True)
@click.option("-p", "--platform", type=str,
              help="Platform name",
              required=True)
@click.option("-t", "--target", type=str,
              help="Target name",
              required=True)
@click.option("-b", "--branch", type=str,
              required=False, default = None,
              help="fre-workflows branch/tag to clone; default is $(fre --version)")
def checkout(experiment, platform, target, branch=None):
    """Clone or verify fre-workflows repository template in ~/cylc-src."""
    checkout_script.checkout_template(experiment, platform, target, branch)


@pp_cli.command()
@click.option("--file_path", "-f", type=str, required=True, help="Path to netCDF (.nc) file")
@click.option("--num_steps", "-n", type=str, required=True, help="Number of expected timesteps")
def nccheck(file_path, num_steps):
    """Verify that a netCDF (.nc) file contains the expected number of timesteps."""
    nccheck_script.check(file_path,num_steps)


@pp_cli.command()
@click.option('--history','-hist', required=True, help="Path to directory containing history files")
@click.option('--date_string','-d', required=True, help="Date string as written in netCDF (.nc) filename")
@click.option('--warn', '-w', is_flag=True, default=False, 
              help="Issue warning log instead of raising exception if diag_manifest files are missing")
def histval(history,date_string,warn):
    """Validate timestep counts across history NetCDF files using diag_manifest metadata."""
    histval_script.validate(history,date_string,warn)


@pp_cli.command()
@click.option('-i', '--inputdir', required=True,
              help='Path to a directory in which to search for netcdf files to split. Files matching the pattern in $history-source will be split.')
@click.option('-o', '--outputdir', required=True,
             help='Path to a directory to which to write split netcdf files.')
@click.option('-c', '--component', required=False, default=None,
              help='component specified in yamlfile under postprocess:components. Needs to be the same component that contains the sources:history-file. Conflicts with --split-all-vars.')
@click.option('-s', '--history-source', required=True, default=None,
              help='history-file specification under postprocess:components:type=component:sources in the fre postprocess config yamlfile. Used to match files in inputdir.')
@click.option('-y', '--yamlfile', required=False, default=None,
              help='fre postprocessing .yml file from which to get the variable filtering list under postprocess:components:type=component:variables. Conflicts with --split-all-vars.')
@click.option('--use-subdirs', '-u', is_flag=True, default=False,
              help="Whether to search subdirs underneath $inputdir for netcdf files. Defaults to false. This option is used in flow.cylc when regridding.")
@click.option('--split-all-vars', '-a', is_flag=True, default=False,
              help="Whether to ignore other config options and split all vars in the file. Defaults to false. Conflicts with -c, -s and -y options.")
def split_netcdf_wrapper(inputdir, outputdir, component, history_source, use_subdirs, yamlfile, split_all_vars):
    """Split multi-variable NetCDF history files into single-variable files matching workflow specs."""
    if split_all_vars:
        none_args = [component, yamlfile]
        if any([el is not None for el in none_args]):
            fre_logger.error('''Error in split_netcdf_wrapper arg parsing: --split-all-vars was set and one or more of
mutually exclusive options --component and --yamlfile was also set!
Either unset --split-all-vars or parse the varlist from the yaml - do not try do do both!''')
    split_netcdf_script.split_netcdf(inputdir, outputdir, component, history_source, use_subdirs, yamlfile, split_all_vars)

@pp_cli.command()
@click.option('-f', '--file', type = str, required=True, help='path to a netcdf file')
@click.option('-o', '--outputdir', type = str, required=True, help='path to a directory to which to write single-data-variable output files')
@click.option('-v', '--variables', type = str, required=True,
              help='''Specifies which variables in $file are split and written to $outputdir.
                     Either a string "all" or a comma-separated string of variable names ("tasmax,tasmin,pr")''')
def split_netcdf(file, outputdir, variables):
    """Split a single NetCDF file into individual per-variable NetCDF files."""
    var_list = variables.split(",")
    split_netcdf_script.split_file_xarray(file, outputdir, variables)


@pp_cli.command()
@click.option('--path', '-p', required=True, help="Path to postprocessed time-series file")
def ppval(path):
    """Estimate expected timesteps from filename date range/frequency and run nccheck validation."""
    ppval_script.validate(path)


@pp_cli.command()
@click.option("-e", "--experiment", type=str,
              help="Experiment name",
              required=True)
@click.option("-p", "--platform", type=str,
              help="Platform name",
              required=True)
@click.option("-T", "--target", type=str,
              help="Target name",
              required=True)
@click.option("-c", "--config-file", type=str,
              help="Path to a configuration file in either XML or YAML",
              required=True)
@click.option("-b", "--branch",
              required=False, default=None,
              help="fre-workflows branch/tag to clone; default is $(fre --version)")
@click.option("-t", "--time",
              required=False, default=None,
              help="Time whose history files are ready")
def all(experiment, platform, target, config_file, branch, time):
    """Execute all FRE post-processing pipeline steps in sequential order."""
    fre_logger.info('(frepp.wrapper) forwarding context to wrapper.run_all_fre_pp_steps via click...')
    wrapper_script.run_all_fre_pp_steps(experiment, platform, target, config_file, branch, time)
    fre_logger.info('(frepp.wrapper) done forwarding context to wrapper.run_all_fre_pp_steps via click.')


@pp_cli.command()
@click.option("-e", "--experiment", type=str,
              help="Experiment name",
              required=True)
@click.option("-p", "--platform", type=str,
              help="Platform name",
              required=True)
@click.option("-T", "--target", type=str,
              help="Target name",
              required=True)
@click.option("-t", "--time",
              required=True,
              help="Time whose history files are ready")
def trigger(experiment, platform, target, time):
    """Trigger post-processing workflow execution for a specific time chunk of history files."""
    trigger_script.trigger(experiment, platform, target, time)


@pp_cli.command()
@click.option("-i", "--input-dir", type=str,
              help="Input directory", required=True)
@click.option("-o", "--output-dir", type=str,
              help="Output directory", required=True)
@click.option("-c", "--component", type=str,
              help="Component name to process", required=True)
@click.option("-u", '--use-subdirs', is_flag=True, default=False,
              help="Whether to search subdirs underneath $inputdir for netcdf files. Defaults to false. This option is used in flow.cylc when regridding.")
@click.option("-d", "--diag-manifest", multiple=True, type=click.Path(exists=True),
              help="Path to FMS diag manifest associated with the component (history file). Optional, but required when the history file has one timestep and no time bounds. If there are multiple manifests, specify multiple --diag-manifest options.")
def rename_split(input_dir, output_dir, component, use_subdirs, diag_manifest):
    """Create per-variable time-series files from split intermediate shards."""
    rename_split_script.rename_split(input_dir, output_dir, component, use_subdirs, diag_manifest)
