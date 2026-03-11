import os
import tempfile

import pytest
import yaml

import fre
from fre.yamltools.helpers import yaml_load, check_fre_version


@pytest.fixture
def temp_path():
    """Fixture that creates a temporary YAML file and returns its path, then cleans up."""
    data = {'foo': 'bar', 'list': [1, 2, 3]}
    with tempfile.NamedTemporaryFile('w', delete=False, suffix=".yml") as tf:
        yaml.dump(data, tf)
        temp_path = tf.name
    yield temp_path
    os.remove(temp_path)

def test_yaml_load_reads_yaml_file_correctly(temp_path):
    loaded = yaml_load(temp_path)
    assert loaded == {'foo': 'bar', 'list': [1, 2, 3]}

def test_yaml_load_raises_file_not_found():
    with pytest.raises(FileNotFoundError):
        yaml_load("this_file_should_not_exist.yml")

## fre_version checks
@pytest.fixture
def yaml_with_matching_version(tmp_path):
    """Create a YAML file with the correct fre_version."""
    data = {'fre_version': fre.version, 'fre_properties': []}
    path = tmp_path / "matching_version.yaml"
    with open(path, 'w') as f:
        yaml.dump(data, f)
    return str(path)

@pytest.fixture
def yaml_with_wrong_version(tmp_path):
    """Create a YAML file with an incorrect fre_version."""
    data = {'fre_version': '0000.00', 'fre_properties': []}
    path = tmp_path / "wrong_version.yaml"
    with open(path, 'w') as f:
        yaml.dump(data, f)
    return str(path)

@pytest.fixture
def yaml_without_version(tmp_path):
    """Create a YAML file without fre_version."""
    data = {'fre_properties': []}
    path = tmp_path / "no_version.yaml"
    with open(path, 'w') as f:
        yaml.dump(data, f)
    return str(path)

def test_check_fre_version_matching(yaml_with_matching_version):
    """check_fre_version should pass when fre_version matches installed version."""
    check_fre_version(yaml_with_matching_version)

def test_check_fre_version_mismatch(yaml_with_wrong_version):
    """check_fre_version should raise ValueError when fre_version does not match."""
    with pytest.raises(ValueError, match="does not match the installed version"):
        check_fre_version(yaml_with_wrong_version)

def test_check_fre_version_missing(yaml_without_version, caplog):
    """check_fre_version should warn but not error when fre_version is missing."""
    import logging
    with caplog.at_level(logging.WARNING):
        check_fre_version(yaml_without_version)
    assert "fre_version not specified" in caplog.text
