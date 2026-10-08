import os
import tempfile

import pytest
import yaml

import fre
from fre.yamltools.helpers import yaml_load, check_fre_version, experiment_check


@pytest.fixture
def temp_yaml_and_path():
    """Fixture that creates a temporary YAML file and returns its path, then cleans up."""
    data = {'foo': 'bar', 'list': [1, 2, 3]}
    with tempfile.NamedTemporaryFile('w', delete=False, suffix=".yml") as tf:
        yaml.dump(data, tf)
        temp_yaml_and_path = tf.name
    yield temp_yaml_and_path
    os.remove(temp_yaml_and_path)

## fre_cli_version checks
@pytest.fixture
def yaml_with_matching_version(tmp_path):
    """Create a YAML file with the correct fre_cli_version."""
    data = {'fre_cli_version': fre.version, 'fre_properties': []}
    path = tmp_path / "matching_version.yaml"
    with open(path, 'w') as f:
        yaml.dump(data, f)
    return str(path)

@pytest.fixture
def yaml_with_wrong_version(tmp_path):
    """Create a YAML file with an incorrect fre_cli_version."""
    data = {'fre_cli_version': '0000.00', 'fre_properties': []}
    path = tmp_path / "wrong_version.yaml"
    with open(path, 'w') as f:
        yaml.dump(data, f)
    return str(path)

@pytest.fixture
def yaml_without_version(tmp_path):
    """Create a YAML file without fre_cli_version."""
    data = {'fre_properties': []}
    path = tmp_path / "no_version.yaml"
    with open(path, 'w') as f:
        yaml.dump(data, f)
    return str(path)

def test_yaml_load_reads_yaml_file_correctly(temp_yaml_and_path):
    loaded = yaml_load(temp_yaml_and_path)
    assert loaded == {'foo': 'bar', 'list': [1, 2, 3]}

def test_yaml_load_raises_file_not_found():
    with pytest.raises(FileNotFoundError):
        yaml_load("this_file_should_not_exist.yml")

def test_check_fre_version_matching(yaml_with_matching_version):
    """check_fre_version should pass when fre_cli_version matches installed version."""
    check_fre_version(yaml_with_matching_version)

def test_check_fre_version_mismatch(yaml_with_wrong_version):
    """check_fre_version should raise ValueError when fre_cli_version does not match."""
    with pytest.raises(ValueError, match="does not match the installed version"):
        check_fre_version(yaml_with_wrong_version)

def test_check_fre_version_missing(yaml_without_version, caplog):
    """check_fre_version should log info but not error when fre_cli_version is missing."""
    import logging
    with caplog.at_level(logging.WARNING):
        check_fre_version(yaml_without_version)
    assert "fre_cli_version not specified" in caplog.text, f"i'd suspect the 'import fre' in fre/yamltools/helpers"


def test_experiment_check_returns_experiment_and_analysis_paths(tmp_path):
    """experiment_check should resolve all YAML paths for the requested experiment."""
    for filename in ("first_pp.yaml", "second_pp.yaml", "analysis.yaml"):
        (tmp_path / filename).touch()

    loaded_yaml = {
        "experiments": [
            {"name": "other", "pp": ["other.yaml"]},
            {
                "name": "target",
                "pp": ["first_pp.yaml", "second_pp.yaml"],
                "analysis": ["analysis.yaml"],
            },
        ]
    }

    pp_paths, analysis_paths = experiment_check(
        mainyaml_dir=tmp_path,
        experiment="target",
        loaded_yaml=loaded_yaml,
    )

    assert pp_paths == [tmp_path / "first_pp.yaml", tmp_path / "second_pp.yaml"]
    assert analysis_paths == [tmp_path / "analysis.yaml"]


@pytest.mark.parametrize("analysis", [{}, {"analysis": None}])
def test_experiment_check_without_analysis_returns_none(tmp_path, analysis):
    """experiment_check should return None when analysis YAML paths are not defined."""
    (tmp_path / "experiment.yaml").touch()
    loaded_yaml = {
        "experiments": [{"name": "target", "pp": ["experiment.yaml"], **analysis}]
    }

    pp_paths, analysis_paths = experiment_check(
        mainyaml_dir=tmp_path,
        experiment="target",
        loaded_yaml=loaded_yaml,
    )

    assert pp_paths == [tmp_path / "experiment.yaml"]
    assert analysis_paths is None


def test_experiment_check_rejects_unknown_experiment(tmp_path):
    loaded_yaml = {"experiments": [{"name": "known", "pp": ["experiment.yaml"]}]}

    with pytest.raises(NameError, match="missing is not in the list of experiments"):
        experiment_check(
            mainyaml_dir=tmp_path,
            experiment="missing",
            loaded_yaml=loaded_yaml,
        )


def test_experiment_check_requires_experiment_yaml_path(tmp_path):
    loaded_yaml = {"experiments": [{"name": "target", "pp": None}]}

    with pytest.raises(ValueError, match="No experiment yaml path given"):
        experiment_check(
            mainyaml_dir=tmp_path,
            experiment="target",
            loaded_yaml=loaded_yaml,
        )


def test_experiment_check_rejects_nonexistent_experiment_yaml(tmp_path):
    loaded_yaml = {"experiments": [{"name": "target", "pp": ["target"]}]}

    with pytest.raises(
        ValueError,
        match=r"^Experiment yaml path given \(target\) does not exist\.$",
    ):
        experiment_check(
            mainyaml_dir=tmp_path,
            experiment="target",
            loaded_yaml=loaded_yaml,
        )


def test_experiment_check_rejects_nonexistent_analysis_yaml(tmp_path):
    (tmp_path / "experiment.yaml").touch()
    loaded_yaml = {
        "experiments": [
            {"name": "target", "pp": ["experiment.yaml"], "analysis": ["missing.yaml"]}
        ]
    }

    with pytest.raises(
        ValueError,
        match="Incorrect analysis yaml path given; does not exist\\.",
    ):
        experiment_check(
            mainyaml_dir=tmp_path,
            experiment="target",
            loaded_yaml=loaded_yaml,
        )
