''' fre pp '''

import click
import logging
fre_logger = logging.getLogger(__name__)

from fre.pp import checkout_script
from fre.pp import configure_script_yaml
from fre.pp import configure_script_xml
from fre.pp import validate_script
from fre.pp import histval_script
from fre.pp import install_script
from fre.pp import run_script
from fre.pp import nccheck_script
from fre.pp import trigger_script
from fre.pp import status_script
from fre.pp import wrapper_script

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
    """ - Report status of PP configuration"""
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
    """ - Run PP configuration"""
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
    """ - Validate PP configuration"""
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
    """ - Install PP configuration"""
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
def configure_yaml(yamlfile,experiment,platform,target):
    """ - Execute fre pp configure """
    configure_script_yaml.yaml_info(yamlfile,experiment,platform,target)

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
    """ - Execute fre pp checkout """
    checkout_script.checkout_template(experiment, platform, target, branch)

@pp_cli.command()
@click.option('-x', '--xml',
              required=True,
              help="Required. The Bronx XML")
@click.option('-p', '--platform',
              required=True,
              help="Required. The Bronx XML Platform")
@click.option('-t', '--target',
              required=True,
              help="Required. The Bronx XML Target")
@click.option('-e', '--experiment',
              required=True,
              help="Required. The Bronx XML Experiment")
@click.option('--do_analysis',
              is_flag=True,
              default=False,
              help="Optional. Runs the analysis scripts.")
@click.option('--historydir',
              help="Optional. History directory to reference. " \
                   "If not specified, the XML's default will be used.")
@click.option('--refinedir',
              help="Optional. History refineDiag directory to reference. " \
                   "If not specified, the XML's default will be used.")
@click.option('--ppdir',
              help="Optional. Postprocessing directory to reference. " \
                   "If not specified, the XML's default will be used.")
@click.option('--do_refinediag',
              is_flag=True,
              default=False,
              help="Optional. Process refineDiag scripts")
@click.option('--pp_start', type=str, default='0000',
              help="Optional. Starting year of postprocessing. " \
                   "If not specified, a default value of '0000' " \
                   "will be set and must be changed in rose-suite.conf")
@click.option('--pp_stop', type=str, default='0000',
              help="Optional. Ending year of postprocessing. " \
                    "If not specified, a default value of '0000' " \
                    "will be set and must be changed in rose-suite.conf")
@click.option('--validate',
              is_flag=True,
              help="Optional. Run the Cylc validator " \
                    "immediately after conversion")
@click.option('-v', '--verbose',
              is_flag=True,
              help="Optional. Display detailed output")
@click.option('-q', '--quiet',
              is_flag=True,
              help="Optional. Display only serious messages and/or errors")
@click.option('--dual',
              is_flag=True,
              help="Optional. Append '_canopy' to pp, analysis, and refinediag dirs")
def configure_xml(xml, platform, target, experiment, do_analysis, historydir, refinedir,
                  ppdir, do_refinediag, pp_start, pp_stop, validate, verbose, quiet, dual):
    """ - Converts a Bronx XML to a Canopy rose-suite.conf """
    configure_script_xml.convert(xml, platform, target, experiment, do_analysis, historydir, refinedir,
                                 ppdir, do_refinediag, pp_start, pp_stop, validate, verbose, quiet, dual)

#fre pp nccheck
@pp_cli.command()
@click.option("--file_path", "-f", type=str, required=True, help="Path to netCDF (.nc) file")
@click.option("--num_steps", "-n", type=str, required=True, help="Number of expected timesteps")
def nccheck(file_path, num_steps):
    """ - Check that a netCDF (.nc) file contains expected number of timesteps - """
    nccheck_script.check(file_path,num_steps)

#fre pp histval
@pp_cli.command()
@click.option('--history','-hist', required=True, help="Path to directory containing history files")
@click.option('--date_string','-d', required=True, help="Date string as written in netCDF (.nc) filename")
@click.option('--warn', '-w', is_flag=True, default=False, help="Warn mode. Instead of raising an error, a warning will be printed in the fre log if no diag manifest files are present")
def histval(history,date_string,warn):
    """ Finds diag manifest files in directory containing history files then runs nccheck to validate timesteps for all files in that directory """
    histval_script.validate(history,date_string,warn)
    
#fre pp split-netcdf-wrapper
@pp_cli.command()
#fre pp split-netcdf-wrapper -i $inputDir -o outputDir -c $component -s $history_file --use-subdirs
@click.option('-i', '--inputDir', required=True, help='directory in which to search for the postprocess files')
@click.option('-o', '--outputDir', required=True, help='directory to which to write postprocessed files')
@click.option('-c', '--component', required=True, help='component')
@click.option('-s', '--history-source', required=True, help='source')
@click.option('-use-subdirs', '-u', is_flag=True, default=False, 
              help="whether to use subdirs. defaults to false. option most often used for regridding.")
def split_netcdf_wrapper(inputDir, outputDir, component, history_source)
    ''' '''
    split_netcdf_script.split_netcdf()

#fre pp split-netcdf
@pp_cli.command()
@click.option('-f', '--file', required=True, help='netcdf file to split')
@click.option('-o', '--outputDir', required=True, help='directory to which to write postprocessed files')
@click.option('-v', '--varlist', required=True, help='list of variables to filter on')
def split_netcdf(infile, outputDir, var_list)
    ''' '''
    split_netcdf_script.split_file_xarray(infile, outputDir, var_list)


#fre pp wrapper
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
def wrapper(experiment, platform, target, config_file, branch, time):
    """ - Execute fre pp steps in order """
    fre_logger.info('(frepp.wrapper) about to foward context to wrapper.run_all_fre_pp_steps via click...')
    wrapper_script.run_all_fre_pp_steps(experiment, platform, target, config_file, branch, time)
    fre_logger.info('(frepp.wrapper) done fowarding context to wrapper.run_all_fre_pp_steps via click.')

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
    """ - Start postprocessing for a particular time """
    trigger_script.trigger(experiment, platform, target, time)

if __name__ == "__main__":
    ''' entry point for click to fre pp commands '''
    pp_cli()
