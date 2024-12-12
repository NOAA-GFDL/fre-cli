from pathlib import Path
import pytest
from tempfile import TemporaryDirectory

from analysis_scripts import find_plugins, available_plugins, UnknownPluginError
from fre.analysis.subtools import install_analysis_package, run_analysis


def make_experiment_yaml(path, name, whitespace="  "):
    """Creates and experiment yaml configuration file for testing.

    Args:
        path: Path to the experiment yaml file that will be created.
        name: String name of the analysis package.
        whitespace: Amount of whitespace each block will be indented by.
    """
    with open(path, "w") as yaml_:
        yaml_.write("analysis:\n")
        yaml_.write(f"{whitespace}{name}:\n")
        yaml_.write(f"{2*whitespace}required:\n")
        yaml_.write(f"{3*whitespace}arg: value\n")


def test_install_analysis_package():
    """Tests installing an analysis package."""
    url = "github.com/noaa-gfdl/analysis-scripts"
    name = "freanalysis_clouds"
    with TemporaryDirectory() as tmp:
         install_analysis_package(url, name, tmp)
         assert Path(tmp) / name in [x for x  in Path(tmp).iterdir() if x.is_dir()]
         find_plugins(tmp)
         assert name in available_plugins()


def test_run_analysis():
    """Tests running an analysis package.  Expects to fail because we don't make a catalog."""
    name = "freanalysis_clouds"
    with TemporaryDirectory() as tmp:
        experiment_yaml = Path(tmp) / "experiment.yaml"
        make_experiment_yaml(experiment_yaml, name)
        library_directory = Path(tmp) / "lib"
        url = "github.com/noaa-gfdl/analysis-scripts"
        install_analysis_package(url, name, library_directory)
        find_plugins(str(library_directory))
        with pytest.raises(FileNotFoundError):
            run_analysis(name, "fake-catalog", ".", "output.yaml", experiment_yaml,
                         library_directory)


def test_run_unknown_analysis():
    """Get an UnknownPluginError when trying to run an uninstalled package."""
    name = "freanalysis_clouds"
    with TemporaryDirectory() as tmp:
        experiment_yaml = Path(tmp) / "experiment.yaml"
        make_experiment_yaml(experiment_yaml, name)
        with pytest.raises(UnknownPluginError):
            run_analysis(name, "fake-catalog", ".", "output.yaml", experiment_yaml, tmp)
