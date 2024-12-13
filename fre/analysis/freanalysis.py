from analysis_scripts import available_plugins
import click

from .subtools import install_analysis_package, run_analysis, uninstall_analysis_package


@click.group(help=click.style(" - access fre analysis subcommands", fg=(250, 154, 90)))
def analysis_cli():
    """Entry point to fre analysis click commands."""
    pass


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
    for name in sorted(available_plugins(library_directory)):
        print(name)


@analysis_cli.command()
@click.option("--name", type=str, required=True, help="Name of the analysis script.")
@click.option("--catalog", type=str, required=True, help="Path to the data catalog.")
@click.option("--output-directory", type=str, required=True,
              help="Path to the output directory.")
@click.option("--output-yaml", type=str, required=True, help="Path to the output yaml.")
@click.option("--experiment-yaml", type=str, required=True, help="Path to the experiment yaml.")
@click.option("--library-directory", type=str, required=False,
              help="Path to a custom lib directory.")
def run(name, catalog, output_directory, output_yaml, experiment_yaml,
        library_directory):
    """Runs the analysis script and writes the paths to the created figures to a yaml file."""
    run_analysis(name, catalog, output_directory, output_yaml, experiment_yaml,
                 library_directory)


@analysis_cli.command()
@click.option("--name", type=str, required=True, help="Name of package to uninstall.")
@click.option("--library-directory", type=str, required=False,
              help="Path to a custom lib directory.")
def uninstall(name, library_directory):
    """Uninstall an analysis package."""
    uninstall_analysis_package(name, library_directory)


if __name__ == "__main__":
    analysis_cli()
