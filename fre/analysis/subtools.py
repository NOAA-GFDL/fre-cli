from os import environ, getenv
from pathlib import Path
from subprocess import run
from sys import executable

from analysis_scripts import find_plugins, run_plugin
import click
from yaml import safe_load


@click.command()
def install_analysis_package(url, library_directory=None):
    """Installs the analysis package.

    Args:
        url: URL to the github repository for the analysis package.
        env_path: Path to a virtual environment that contains the installed analysis script.
    """
    if not url.startswith("https://"):
        url = f"https://{url}"

    if library_directory:
        run([executable, "-m", "pip", "install", f"--target={library_directory}",
             f"git+{url}.git@main"])
    else:
        run([executable, "-m", "pip", "install", f"git+{url}.git@main"])


@click.command()
def run_analysis(name, catalog, output_directory, output_yaml, experiment_yaml,
                 library_directory=None):
    """Runs the analysis script and writes the paths to the created figures to a yaml file.

    Args:
        name: String name of the analysis script.
        catalog: Path to the data catalog.
        output_directory: Path to the output directory.
        output_yaml:  Path to the output yaml.
        experiment: Path to the experiment yaml.
        env_path: Path to a virtual environment that contains the installed analysis script.
    """

    # Create the directory for the figures.
    Path(output_directory).mkdir(parents=True, exist_ok=True)

    # Parse the configuration out of the experiment yaml file.
    with open(experiment_yaml) as file_:
        config_yaml = safe_load(file_)
        try:
            configuration = config_yaml["analysis"][name]["required"]
        except KeyError:
            configuration = None

    # If using plugins installed in a custom directory, have python try to find them.
    if library_directory:
        find_plugins(library_directory)

    # Run the analysis.
    figure_paths = run_plugin(name, catalog, output_directory, config=configuration)

    # Write out the figure paths to a file.
    with open(output_yaml, "w") as output:
        output.write("figure_paths:\n")
        for path in figure_paths:
            output.write("  -{Path(path).resolve()}\n")


@click.command()
def uninstall_analysis_package(name, library_directory=None):
    if library_directory:
        run(["python", "-m", "pip", "uninstall", f"--target={library_directory}", name])
    else:
        run(["python", "-m", "pip", "uninstall", name])
