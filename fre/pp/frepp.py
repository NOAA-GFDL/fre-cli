''' fre pp '''

import click
import logging
fre_logger = logging.getLogger(__name__)

#fre tools
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

# fre pp
@click.group(help=click.style(" - pp subcommands", fg=(57,139,210)))
def pp_cli():
    ''' entry point to fre pp click commands '''


# fre pp status
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
    """
    Report status of PP configuration
    """
    status_script.status_subtool(experiment, platform, target)

# fre pp run
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
              help="Pause the workflow immediately on start up",
              required=False)
@click.option("--no_wait", is_flag=True, default=False,
              help="after submission, do not wait to ping the scheduler and confirm success",
              required=False)
def run(experiment, platform, target, pause, no_wait):
    """
    Run PP configuration
    """
    run_script.pp_run_subtool(experiment, platform, target, pause, no_wait)

# fre pp validate
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
    """
    Validate PP configuration
    """
    validate_script.validate_subtool(experiment, platform, target)

# fre pp install
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
    """
    Install PP configuration
    """
    install_script.install_subtool(experiment, platform, target)

#fre pp configure
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
def configure_yaml(yamlfile,experiment,platform,target):
    """
    Execute fre pp configure
    """
    configure_script_yaml.yaml_info(yamlfile,experiment,platform,target)

#fre pp checkout
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
@click.option("-b", "--branch", type =str,
              required=False, default = None,
              help="fre-workflows branch/tag to clone; default is $(fre --version)")
def checkout(experiment, platform, target, branch=None):
    """
    Execute fre pp checkout
    """
    checkout_script.checkout_template(experiment, platform, target, branch)

#fre pp nccheck
@pp_cli.command()
@click.option("--file_path", "-f", type=str, required=True, help="Path to netCDF (.nc) file")
@click.option("--num_steps", "-n", type=str, required=True, help="Number of expected timesteps")
def nccheck(file_path, num_steps):
    """
    Check that a netCDF (.nc) file contains expected number of timesteps
    """
    nccheck_script.check(file_path,num_steps)

#fre pp histval
@pp_cli.command()
@click.option('--history','-hist', required=True, help="Path to directory containing history files")
@click.option('--date_string','-d', required=True, help="Date string as written in netCDF (.nc) filename")
@click.option('--warn', '-w', is_flag=True, default=False,
              help = "Warn mode. Instead of raising an error, a warning will be printed in the fre log if no " \
                     "diag manifest files are present")
def histval(history,date_string,warn):
    """
    Finds diag manifest files in directory containing history files then runs nccheck to validate timesteps
    for all files in that directory
    """
    histval_script.validate(history,date_string,warn)

#fre pp split-netcdf-wrapper
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
    ''' Splits all netcdf files matching the pattern specified by $history_source in $inputdir
        into files with a single data variable written to $outputdir. If $yamlfile contains
        variable filtering settings under $component, only those variables specified will
        be split into files for $outdir. If no variables in the variable filtering match
        vars in the netcdf files, no files will be written to $outdir. If --use-subdirs
        is set, netcdf files will be searched for in subdirs under $outdir.

        This tool is intended for use in fre-workflows and assumes files to split have
        fre-specific naming conventions. For a more general tool, look at split-netcdf.'''
    if split_all_vars:
        none_args = [component, yamlfile]
        if any([el is not None for el in none_args]):
            fre_logger.error('''Error in split_netcdf_wrapper arg parsing: --split-all-vars was set and one or more of
mutually exclusive options --component and --yamlfile was also set!
Either unset --split-all-vars or parse the varlist from the yaml - do not try do do both!''')
    split_netcdf_script.split_netcdf(inputdir, outputdir, component, history_source, use_subdirs, yamlfile, split_all_vars)

#fre pp split-netcdf
@pp_cli.command()
@click.option('-f', '--file', type = str, required=True, help='path to a netcdf file')
@click.option('-o', '--outputdir', type = str, required=True, help='path to a directory to which to write single-data-variable output files')
@click.option('-v', '--variables', type = str, required=True,
              help='''Specifies which variables in $file are split and written to $outputdir.
                     Either a string "all" or a comma-separated string of variable names ("tasmax,tasmin,pr")''')
def split_netcdf(file, outputdir, variables):
    ''' Splits a single netcdf file into one netcdf file per data variable and writes
        files to $outputdir.
        $variables is an option to filter the variables split out of $file and
        written to $outputdir. If set to "all" (the default), all data variables
        in $file are split and written to $outputdir; if set to a comma-separated
        string of variable names, only the variable names in the string will be
        split and written to $outputdir. If no variable names in $variables match
        variables in $file, no files will be written to $outputdir.'''
    var_list = variables.split(",")
    split_netcdf_script.split_file_xarray(file, outputdir, variables)


#fre pp ppval
@pp_cli.command()
@click.option('--path','-p', required=True, help="Path to postprocessed time-series file")
def ppval(path):
    """ Determines an estimated number of timesteps from a postprocessed time-series file's name and run nccheck on it """
    ppval_script.validate(path)

#fre pp all
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
    """
    Execute fre pp steps in order
    """
    fre_logger.info('(frepp.wrapper) about to forward context to wrapper.run_all_fre_pp_steps via click...')
    wrapper_script.run_all_fre_pp_steps(experiment, platform, target, config_file, branch, time)
    fre_logger.info('(frepp.wrapper) done forwarding context to wrapper.run_all_fre_pp_steps via click.')

#fre pp trigger
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
    """
    Start postprocessing history files that represent a specific chunk of time
    """
    trigger_script.trigger(experiment, platform, target, time)

if __name__ == "__main__":
    ''' entry point for click to fre pp commands '''
    pp_cli()
