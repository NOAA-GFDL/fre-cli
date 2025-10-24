import pytest
import tempfile
import os
import yaml

from fre.yamltools.helpers import yaml_load

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
