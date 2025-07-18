import json
import pytest
from pathlib import Path
from fre.cmor.cmor_helpers import update_calendar_type

# Sample data for testing
TEST_JSON_CONTENT = {
    "calendar": "original_calendar_type",
    "other_field": "some_value"
}

@pytest.fixture
def temp_json_file(tmp_path):
    """
    Fixture to create a temporary JSON file for testing.

    Args:
        tmp_path: pytest's fixture for temporary directories.

    Returns:
        Path to the temporary JSON file.
    """
    json_file = tmp_path / "test_file.json"
    with open(json_file, "w", encoding="utf-8") as file:
        json.dump(TEST_JSON_CONTENT, file, indent=4)
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