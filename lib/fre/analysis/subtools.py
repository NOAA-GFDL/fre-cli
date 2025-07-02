""" holds subtool commands and related modules for 'fre analysis'  routines"""

from pathlib import Path
from subprocess import run
from tempfile import TemporaryDirectory

from analysis_scripts import available_plugins, run_plugin, VirtualEnvManager
from yaml import safe_load


def install_analysis_package(url, name=None, library_directory=None):
    """Installs the analysis package.

    Args:
        url: URL to the github repository for the analysis package.
        name: String name of the analysis-script package.
        library_directory: Directory to install the package in.
    """
    # Clean up the url if necessary.
    if not url.startswith("https://"):
        url = f"https://{url}"
    if not url.endswith(".git"):
        url = f"{url}.git"

    # Get the absolute path of the input library_directory.
    if library_directory:
        library_directory = Path(library_directory).resolve()

    if name:
        # If a name is given, then expect that the analysis script is part or the noaa-gfdl
        # github repository.
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            run(["git", "clone", url, str(tmp_path / "scripts")], check=True)

            if library_directory:
                # If a library directory is given, install the analysis script in a virtual
                # environment.
                env = VirtualEnvManager(library_directory)
                env.create_env()
                env.install_package(str(tmp_path / "scripts" / "core" / "analysis_scripts"))
                env.install_package(str(tmp_path / "scripts" / "core" / "figure_tools"))
                env.install_package(str(tmp_path / "scripts" / "user-analysis-scripts" / name))
            else:
                run(["pip", "install", str(tmp_path / "scripts" / "core" / "figure_tools")],
                    check=True)
                run(["pip", "install", str(tmp_path / "scripts" / "user-analysis-scripts" / name)],
                    check=True)
    else:
        if library_directory:
            env = VirtualEnvManager(library_directory)
            env.create_env()
            env.install_package(str(tmp_path / "scripts" / "core" / "analysis_scripts"))
            env.install_package(f"{url}@main")
        else:
            run(["pip", "install", f"{url}@main"])


def list_plugins(library_directory=None):
    """Finds the list of analysis scripts.

    Args:
        library_directory: Directory where the analysis package is installed.

    Returns:
        List of string plugin names.
    """
    if library_directory:
        env = VirtualEnvManager(library_directory)
        return env.list_plugins()
    else:
        return available_plugins()


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

    # Run the analysis.
    if library_directory:
        env = VirtualEnvManager(library_directory)
        figure_paths = env.run_analysis_plugin(name, catalog, output_directory,
                                               config=configuration)
    else:
        figure_paths = run_plugin(name, catalog, output_directory, config=configuration)

    # Write out the figure paths to a file.
    with open(output_yaml, "w") as output:
        output.write("figure_paths:\n")
        for path in figure_paths:
            output.write(f"  -{Path(path).resolve()}\n")


def uninstall_analysis_package(name, library_directory=None):
    """Uninstalls the analysis package.

    Args:
        name: String name of the analysis-script package.
        library_directory: Directory where the package was installed.
    """
    if library_directory:
        env = VirtualEnvManager(library_directory)
        env.uninstall_package(name)
    else:
        run(["pip", "uninstall", name], check=True)
