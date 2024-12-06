from os import chdir, getcwd
from pathlib import Path
from subprocess import run
from sys import executable
from tempfile import TemporaryDirectory

from analysis_scripts import find_plugins, run_plugin
import click
from yaml import safe_load


def install(name, library_directory=None):
    """Helper function to install possibly using a target directory.

    Args:
        name: String name of the package to install.
        library_directory: Path to target directory you want to install the package in.
    """
    if library_directory:
        run([executable, "-m", "pip", "install", f"--target={library_directory}", name])
    else:
        run([executable, "-m", "pip", "install", name])


@click.command()
def install_analysis_package(url, name=None, library_directory=None):
    """Installs the analysis package.

    Args:
        url: URL to the github repository for the analysis package.
        name: String name of the analysis-script package.
        library_directory: Directory to install the package in.
    """
    if not url.startswith("https://"):
        url = f"https://{url}"
    if not url.endswith(".git"):
        url = f"{url}.git"

    if name:
        go_back_here = Path(getcwd())
        with TemporaryDirectory() as tmpdirname:
            chdir(tmpdirname)
            run(["git", "clone", url, "scripts"])
            chdir(go_back_here / "scripts" / "core" / "figure_tools")
            install(".", library_directory)
            chdir(go_back_here / "scripts" / "user-analysis-scripts" / name)
            install(".", library_directory)
            chdir(go_back_here)
    else:
        install(f"{url}@main", library_directory)


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
        library_directory: Directory where the analysis package is installed.
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
    """Uninstalls the analysis package.

    Args:
        name: String name of the analysis-script package.
        library_directory: Directory where the package was installed.
    """
    if library_directory:
        run(["python", "-m", "pip", "uninstall", f"--target={library_directory}", name])
    else:
        run(["python", "-m", "pip", "uninstall", name])
