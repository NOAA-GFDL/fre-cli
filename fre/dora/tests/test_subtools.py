from pathlib import Path
from tempfile import TemporaryDirectory

from fre.dora.subtools import add_experiment_to_dora, get_dora_experiment_id, \
                              publish_analysis_figures
import pytest


def _make_experiment_yaml(path, name, whitespace="  "):
    """Creates an experiment yaml configuration file for testing.

    Args:
        path: Path to the experiment yaml file that will be created.
        name: String name of the analysis package.
        whitespace: Amount of whitespace each block will be indented by.
    """
    analysis_path = ""
    history_path = ""
    pp_path = ""
    pp_start = 1980
    pp_stop = 1981
    with open(path, "w") as yaml_:
        yaml_.write("directories:\n")
        yaml_.write(f"{whitespace}analysis_dir: {analysis_path}\n")
        yaml_.write(f"{whitespace}history_dir: {history_path}\n")
        yaml_.write(f"{whitespace}pp_dir: {pp_path}\n")
        yaml_.write(f"name: {name}\n")
        yaml_.write("postprocess:\n")
        yaml_.write(f"{whitespace}settings:\n")
        yaml_.write(f"{2*whitespace}pp_start: {pp_start}\n")
        yaml_.write(f"{2*whitespace}pp_start: {pp_stop}\n")


def _make_figures_yaml(path, whitespace="  "):
    """Creates and experiment yaml configuration file for testing.

    Args:
        path: Path to the figures yaml file that will be created.
        whitespace: Amount of whitespace each block will be indented by.
    """
    figure_paths = ["foo", "bar"]
    with open(path, "w") as yaml_:
        yaml_.write("figure_paths:\n")
        for path in figure_paths:
            yaml_.write(f"{whitespace}-{Path(path).resolve()}\n")


def test_add_experiment_to_dora():
    name = "freanalysis_clouds"
    with TemporaryDirectory() as tmp:
        experiment_yaml = Path(tmp) / "experiment.yaml"
        _make_experiment_yaml(experiment_yaml, name)
        id_ = add_experiment_to_dora(experiment_yaml, "https://dora-dev.gfdl.noaa.gov")


def test_get_dora_experiment_id():
    name = "freanalysis_clouds"
    with TemporaryDirectory() as tmp:
        experiment_yaml = Path(tmp) / "experiment.yaml"
        _make_experiment_yaml(experiment_yaml, name)
        id_ = get_dora_experiment_id(experiment_yaml, "https://dora-dev.gfdl.noaa.gov")


def test_publish_analysis_figures():
    name = "freanalysis_clouds"
    with TemporaryDirectory() as tmp:
        experiment_yaml = Path(tmp) / "experiment.yaml"
        _make_experiment_yaml(experiment_yaml, name)
        figures_yaml = Path(tmp) / "figures.yml"
        _make_figures_yaml(figures_yaml)
        publish_analysis_figures(name, experiment_yaml, figures_yaml,
                                 "https://dora-dev.gfdl.noaa.gov")
