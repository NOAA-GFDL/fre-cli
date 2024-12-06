from os import environ, getenv
from pathlib import Path
from subprocess import run
from sys import executable
from venv import create
import tempfile
import os

from analysis_scripts import find_plugins, run_plugin
import click
from yaml import safe_load


class VirtualEnvironment(object):
    def __init__(self, path):
        self.new_path = path
        self.old_path = getenv("PATH")

    def __enter__(self):
        environ["PATH"] = f"{self.new_path}:{self.old_path}"
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        environ["PATH"] = self.old_path


@click.command()
def create_virtual_environment(path):
    """Creates a virtual environment at the input path.

    Args:
        path: Path where the virtual environment will be created.
    """
    create(path)


@click.command()
def install_analysis_package(url, env_path=None, name=None):
    """Installs the analysis package.

    Args:
        url: URL to the github repository for the analysis package.
        env_path: Path to a virtual environment that contains the installed analysis script.
    """
    if not url.startswith("https://"):
        url = f"https://{url}"

    if not url.endswith(".git"):
        url = f"{url}.git"

    if name is None:
        if env_path:
            with VirtualEnvironment(env_path):
                run(["python", "-m", "pip", "install", f"git+{url}@main"])
        else:
            run(["python", "-m", "pip", "install", f"git+{url}@main"])
    else:
        go_back_here = os.getcwd()

        print("Activating", env_path)
        with VirtualEnvironment(env_path):
            with tempfile.TemporaryDirectory() as tmpdirname:
                os.chdir(tmpdirname)
                run(["git", "clone", url, 'scripts'])
                os.chdir(os.path.join('scripts', 'figure_tools'))
                run(['python', '-m', 'pip', 'install', '.'])
                os.chdir(os.path.join('..', name))
                run(['python', '-m', 'pip', 'install', '.'])

            os.chdir(go_back_here)


@click.command()
def run_analysis(name, catalog, output_directory, output_yaml, experiment_yaml,
                 env_path=None):
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

    # If using plugins installed in a virtual environment, have python try to find them.
    if env_path:
        with VirtualEnvironment(env_path):
            find_plugins()

            # Run the analysis.
            figure_paths = run_plugin(name, catalog, output_directory, config=configuration)
    else:
        figure_paths = run_plugin(name, catalog, output_directory, config=configuration)

    # Write out the figure paths to a file.
    with open(output_yaml, "w") as output:
        output.write("figure_paths:\n")
        for path in figure_paths:
            output.write("  -{Path(path).resolve()}\n")


@click.command()
def uninstall_analysis_package(name):
    if env_path:
        with VirtualEnvironment(env_path):
            run(["python", "-m", "pip", "uninstall", name])
    else:
        run(["python", "-m", "pip", "uninstall", name])
