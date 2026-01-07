""" holds subtool commands and related modules for 'fre analysis'  routines"""

from pathlib import Path
from subprocess import run
from tempfile import TemporaryDirectory

from .plugins.subtools import available_plugins, run_plugin
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


def run_analysis(yaml, name, date_range, scripts_dir, output_dir, output_yaml):
    """Runs the analysis and generates all plots and associated datasets.

    Args:
        yaml: Path to a model yaml
        name: Name of the analysis as specified in the yaml
        date_range: Time span to use for analysis (YYYY-MM-DD,YYYY-MM-DD)
        scripts_dir: Path to a directory to save intermediate scripts
        output_dir: Path to a directory to save figures
        output_yaml: Path to use as an structured output yaml file
    """

    # Create the directory for the figures, scripts, and output yaml
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    Path(scripts_dir).mkdir(parents=True, exist_ok=True)
    Path(output_yaml).parent.mkdir(parents=True, exist_ok=True)

    # Parse the pass-through configuration out of the experiment yaml file.
    with open(yaml) as file_:
        config_yaml = safe_load(file_)
        specific_config = config_yaml["analysis"][name]["specific_config"]
        script_type = config_yaml["analysis"][name]["script_type"]

    # Run the analysis.
    figure_paths = run_plugin(script_type, name, specific_config, date_range, scripts_dir, output_dir, output_yaml)


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
