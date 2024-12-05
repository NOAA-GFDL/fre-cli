import click

from .subtools import create_virtual_environment, install_analysis_package, \
                      run_analysis, uninstall_analysis_package


@click.group(help=click.style(" - access fre analysis subcommands", fg=(250, 154, 90)))
def analysis_cli():
    """Entry point to fre analysis click commands."""
    pass


@analysis_cli.command()
@click.option("--url", type=str, required=True, help="URL of the github repository.")
@click.option("--env-path", type=str, required=False, help="Path for the virtual environment.")
@click.pass_context
def install(context, url, env_path):
    """Installs an analysis package."""
    context.forward(install_analysis_package)


@analysis_cli.command()
@click.option("--path", type=str, required=True, help="Path for the virtual environment.")
@click.pass_context
def create_venv(context, path):
    """Creates a virtual environment at the input path."""
    context.forward(create_virtual_environment)


@analysis_cli.command()
@click.option("--name", type=str, required=True, help="Name of the analysis script.")
@click.option("--catalog", type=str, required=True, help="Path to the data catalog.")
@click.option("--output-directory", type=str, required=True,
              help="Path to the output directory.")
@click.option("--output-yaml", type=str, required=True, help="Path to the output yaml.")
@click.option("--experiment-yaml", type=str, required=True, help="Path to the experiment yaml.")
@click.pass_context
def run(context, name, catalog, output_directory, output_yaml, experiment_yaml):
    """Runs the analysis script and writes the paths to the created figures to a yaml file."""
    context.forward(run_analysis)


@analysis_cli.command()
@click.option("--name", type=str, required=True, help="Name of package to uninstall.")
@click.pass_context
def uninstall(context, name):
    """Uninstall an analysis package."""
    context.forward(uninstall_analysis_package)


if __name__ == "__main__":
    analysis_cli()
