import json
import pytest
from pathlib import Path
from fre.cmor.cmor_helpers import update_grid_and_label

# Sample data for testing
TEST_JSON_CONTENT = {
    "grid_label": "original_label",
    "grid": "original_grid",
    "nominal_resolution": "original_nom_res",
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

def test_update_grid_label_and_grid_success(temp_json_file):
    """
    Test successful update of 'grid_label' and 'grid' fields.
    """
    # Arrange
    new_grid = "updated_grid"
    new_grid_label = "updated_label"
    new_nom_res = "updated_nom_res"

    # Act
    update_grid_and_label(temp_json_file, new_grid_label, new_grid, new_nom_res)

    # Assert
    with open(temp_json_file, "r", encoding="utf-8") as file:
        data = json.load(file)
        assert data["grid"] == new_grid
        assert data["grid_label"] == new_grid_label
        assert data["nominal_resolution"] == new_nom_res
        assert data["other_field"] == "some_value"  # Ensure other fields are untouched

def test_missing_grid_label_field(temp_json_file):
    """
    Test behavior when the 'grid_label' field is missing in the JSON file.
    """
    # Arrange
    with open(temp_json_file, "r+", encoding="utf-8") as file:
        data = json.load(file)
        del data["grid_label"]  # Remove the 'grid_label' field
        file.seek(0)
        json.dump(data, file, indent=4)
        file.truncate()

    new_grid_label = "updated_label"
    new_grid = "updated_grid"
    new_nom_res = "updated_nom_res"

    # Act & Assert
    with pytest.raises(KeyError, match="Error while updating 'grid_label'"):
        update_grid_and_label(temp_json_file, new_grid_label, new_grid, new_nom_res)

def test_missing_grid_field(temp_json_file):
    """
    Test behavior when the 'grid' field is missing in the JSON file.
    """
    # Arrange
    with open(temp_json_file, "r+", encoding="utf-8") as file:
        data = json.load(file)
        del data["grid"]  # Remove the 'grid' field
        file.seek(0)
        json.dump(data, file, indent=4)
        file.truncate()

    new_grid_label = "updated_label"
    new_grid = "updated_grid"
    new_nom_res = "updated_nom_res"

    # Act & Assert
    with pytest.raises(KeyError, match="Error while updating 'grid'"):
        update_grid_and_label(temp_json_file, new_grid_label, new_grid, new_nom_res)

def test_invalid_json_file(tmp_path):
    """
    Test behavior when the input file is not a valid JSON file.
    """
    # Arrange
    invalid_json_file = tmp_path / "invalid_file.json"
    with open(invalid_json_file, "w", encoding="utf-8") as file:
        file.write("This is not a valid JSON!")

    new_grid_label = "updated_label"
    new_grid = "updated_grid"
    new_nom_res = "updated_nom_res"

    # Act & Assert
    with pytest.raises(json.JSONDecodeError):
        update_grid_and_label(invalid_json_file, new_grid_label, new_grid, new_nom_res)

def test_nonexistent_file():
    """
    Test behavior when the specified JSON file does not exist.
    """
    # Arrange
    nonexistent_file = Path("nonexistent.json")
    new_grid_label = "updated_label"
    new_grid = "updated_grid"
    new_nom_res = "updated_nom_res"

    # Act & Assert
    with pytest.raises(FileNotFoundError):
        update_grid_and_label(nonexistent_file, new_grid_label, new_grid, new_nom_res)
