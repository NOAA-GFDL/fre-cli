import json
import pytest
from pathlib import Path
from fre.cmor.cmor_helpers import update_calendar_type

@pytest.fixture
def temp_json_file(tmp_path):
    """
    Fixture to create a temporary JSON file for testing.

    Args:
        tmp_path: pytest's fixture for temporary directories.

    Returns:
        Path to the temporary JSON file.
    """
    # Sample data for testing
    test_json_content = {
        "calendar": "original_calendar_type",
        "other_field": "some_value"
    }

    json_file = tmp_path / "test_file.json"
    with open(json_file, "w", encoding="utf-8") as file:
        json.dump(test_json_content, file, indent=4)
    return json_file

def test_update_calendar_type_success(temp_json_file):
    """
    Test successful update of 'grid_label' and 'grid' fields.
    """
    # Arrange
    new_calendar_type = "365_day"

    # Act
    update_calendar_type(temp_json_file, new_calendar_type)

    # Assert
    with open(temp_json_file, "r", encoding="utf-8") as file:
        data = json.load(file)
        assert data["calendar"] == new_calendar_type
        assert data["other_field"] == "some_value"

def test_update_calendar_type_valerr_raise(temp_json_file):
    """
    Test error raising when the input calendar is None
    """
    with pytest.raises(ValueError):
        update_calendar_type(temp_json_file, None)

def test_update_calendar_type_unknown_err():
    """
    Test raising an exception not caught by the other ones
    """
    bad_path = 12345
    with pytest.raises(Exception):
        update_calendar_type( bad_path, '365_day')

@pytest.fixture
def temp_keyerr_json_file(tmp_path):
    """
    Fixture to create a temporary JSON file for testing.

    Args:
        tmp_path: pytest's fixture for temporary directories.

    Returns:
        Path to the temporary JSON file.
    """
    # Sample data for testing
    test_json_content = {
        "clendar": "original_calendar_type", #oops spelling error  # cspell:disable-line
        "other_field": "some_value"
    }

    json_file = tmp_path / "test_file.json"
    with open(json_file, "w", encoding="utf-8") as file:
        json.dump(test_json_content, file, indent=4)
    return json_file

def test_update_calendar_type_keyerror_raise(temp_keyerr_json_file):
    """
    Test error raising when the calendar key doesn't exist
    """
    with pytest.raises(KeyError):
        update_calendar_type(temp_keyerr_json_file,'365_day')

@pytest.fixture
def temp_jsondecodeerr_json_file(tmp_path):
   # Create a file with invalid JSON content
    invalid_json_file = tmp_path / "invalid.json"
    invalid_content = '{ "calendar": "original_calendar_type", "other_field": "some_value" '  # missing closing }
    with open(invalid_json_file, "w", encoding="utf-8") as f:
        f.write(invalid_content)
    return invalid_json_file

def test_update_calendar_type_jsondecode_raise(temp_jsondecodeerr_json_file):
    """
    Test raising a JSONDecodeError
    """
    with pytest.raises(json.JSONDecodeError):
        update_calendar_type(temp_jsondecodeerr_json_file, '365_day')

def test_update_calendar_type_jsonDNE_raise():
    """
    Test error raising when the input experiment json doesn't exist
    """
    with pytest.raises(FileNotFoundError):
        update_calendar_type('DOES_NOT_EXIST.json','365_day')
