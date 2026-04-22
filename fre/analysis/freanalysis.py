"""
The package analysis-scripts (https://github.com/NOAA-GFDL/analysis-scripts.git) contains
user-defined analysis scripts/plug-ins and the core engine to run the scripts/plug-ins.  
This module defines the Click `fre analysis` command and the following subcommands to interface
with the analysis-scripts package:
* fre analysis install [ARGS]:  installs NOAA-GFDL/analysis-scripts package.  If specified,
  also installs the user-analysis-script plug-ins, and a venv virtual environment
* fre analysis list [ARGS]:  lists all the installed user-analysis-script plug-ins
* fre analysis run [ARGS]: runs the user-analysis-script plug-in
* fre analysis uninstall [ARGS]: uninstalls the specified user-analysis-script plug-in


"""

import logging

import click

# this package
from .subtools import (
    install_analysis_package,
    list_plugins,
    run_analysis,
    uninstall_analysis_package
)

fre_logger = logging.getLogger(__name__)


@click.group(help=click.style(" - analysis subcommands", fg=(250, 154, 90)))
def analysis_cli():
    """
    Click entrypoint to the command `fre analysis`.
    """
    pass


@analysis_cli.command('install', short_help="Installs 'NOAA-GFDL'-based analysis-scripts")
@click.option("--url", type=str, required=True, help="""
  Github repository URL to the NOAA-GFDL/analysis-scripts package or to its fork/variants.
  For example, url = https://github.com/NOAA-GFDL/analysis-scripts.git
""")
@click.option("--name", type=str, required=False, help="""
  Name of the user-analysis-script to pip install in addition as a plug-in.
  If not specified, only the core analysis-scripts engine in 
  analysis_scripts/core/analysis_scripts will be installed 
""")
@click.option("--library-directory", type=str, required=False, help="""
  venv target directory if installing the analysis-scripts
  package in a venv virtual environment.  If not provided, the analysis-script
  package and the plug-ins will be installed in the current/default environment.
""")
def install(url, name, library_directory):
    """
    Install the analysis-scripts package from the Github url.
    If specified, install the user-analysis-script plug-ins.
    If specified, create a venv environment
    """
    install_analysis_package(url, name, library_directory)


@analysis_cli.command()
@click.option("--library-directory", type=str, required=False, help="""
  venv target directory from which to list all installed user-analysis-script plug-ins
""")
def list(library_directory):
    """
    list all installed user-analysis-script plug-ins
    """
    plugins = list_plugins(library_directory)
    if plugins:
        fre_logger.info("Installed analysis plug-ins:\n")
        for plugin in plugins:
            fre_logger.info(plugin)
    else:
        fre_logger.info("No analysis plug-ins were found.")


@analysis_cli.command()
@click.option("--name", type=str, required=True, help="Name of the user-analysis-script plug-in")
@click.option("--catalog", type=str, required=True, help="Path to the data catalog")
@click.option("--output-directory", type=str, required=True, help="""
   Path to the output directory where figures from the plug-in will be saved
""")
@click.option("--output-yaml", type=str, required=True, help="""
  Name of the output yaml file.  A yaml file listing the paths to all the
  generated images will be generated at the end of the run to the output-directory.
"""
@click.option("--experiment-yaml", type=str, required=True, help="""
  Path to the experiment yaml file containing the configurations required by the 
  user-analysis-script plug-in.  Configurations must be specified under the key
  analysis/name/required
""")
@click.option("--library-directory", type=str, required=False, help="""
  Path to the venv target directory if the analysis-script package was
  installed in a virtual environment
""")
def run(name, catalog, output_directory, output_yaml, experiment_yaml,
        library_directory):
    """
    Runs the user-analysis-script plug-in and generates a yaml file
    cataloging the paths to the generated figures
    """
    run_analysis(name, catalog, output_directory, output_yaml, experiment_yaml,
                 library_directory)


@analysis_cli.command()
@click.option("--name", type=str, required=True, help="""
  Name of user-analysis-script plug-in to uninstall.
""")
@click.option("--library-directory", type=str, required=False, help="""
  Path to the venv target directory if the user-analysis-script plug-in 
  was installed in a virtual environment
""")
def uninstall(name, library_directory):
    """
    Uninstall user-anlaysis-script plug-in
    """
    uninstall_analysis_package(name, library_directory)
