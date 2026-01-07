''' fre analysis '''

# a third party package
import click
import logging
fre_logger = logging.getLogger(__name__)

## a diff gfdl package
#from analysis_scripts import available_plugins

# this package
from .subtools import install_analysis_package, list_plugins, run_analysis, \
                      uninstall_analysis_package


@click.group(help=click.style(" - analysis subcommands", fg=(250, 154, 90)))
def analysis_cli():
    """Entry point to fre analysis click commands."""



@analysis_cli.command()
@click.option("--url", type=str, required=True, help="URL of the github repository.")
@click.option("--name", type=str, required=False, help="Subdirectory to pip install.")
@click.option("--library-directory", type=str, required=False,
              help="Path to a custom lib directory.")
def install(url, name, library_directory):
    """Installs an analysis package."""
    install_analysis_package(url, name, library_directory)


@analysis_cli.command()
@click.option("--library-directory", type=str, required=False,
              help="Path to a custom lib directory.")
def list(library_directory):
    """List available plugins."""
    plugins = list_plugins(library_directory)
    if plugins:
        fre_logger.info("Installed analysis packages:\n")
        for plugin in plugins:
            fre_logger.info(plugin)
    else:
        fre_logger.info("No analysis packages found.")


@analysis_cli.command()
@click.option("--yaml", type=str, required=True, help="Path to the model yaml")
@click.option("--name", type=str, required=True, help="Name of the analysis script")
@click.option("--date_range", type=str, required=True, help="Time span to use for analysis (YYYY-MM-DD,YYYY-MM-DD)")
@click.option("--scripts_dir", type=str, required=True, help="Path to a directory to save intermediate scripts")
@click.option("--output_dir", type=str, required=True, help="Path to a directory to save figures")
@click.option("--output_yaml", type=str, required=True, help="Path to use as an structured output yaml file")
def run(yaml, name, date_range, scripts_dir, output_dir, output_yaml):
    """Runs the analysis and generates all plots and associated datasets.
    """
    run_analysis(yaml, name, date_range, scripts_dir, output_dir, output_yaml)


@analysis_cli.command()
@click.option("--name", type=str, required=True, help="Name of package to uninstall.")
@click.option("--library-directory", type=str, required=False,
              help="Path to a custom lib directory.")
def uninstall(name, library_directory):
    """Uninstall an analysis package."""
    uninstall_analysis_package(name, library_directory)
