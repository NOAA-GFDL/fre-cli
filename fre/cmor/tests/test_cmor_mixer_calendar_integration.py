import json
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from fre.cmor.cmor_mixer import cmor_run_subtool

@pytest.fixture
def mock_json_exp_config(tmp_path):
    """
    Create a mock JSON experiment config file for testing.
    """
    config_data = {
        "calendar": "360_day",
        "grid": "test_grid",
        "grid_label": "gn",
        "nominal_resolution": "1 km"
    }
    config_file = tmp_path / "exp_config.json"
    with open(config_file, "w") as f:
        json.dump(config_data, f)
    return str(config_file)

@pytest.fixture
def mock_json_var_list(tmp_path):
    """
    Create a mock JSON variable list file for testing.
    """
    var_data = {"temp": "temp", "salt": "salt"}
    var_file = tmp_path / "var_list.json"
    with open(var_file, "w") as f:
        json.dump(var_data, f)
    return str(var_file)

@pytest.fixture
def mock_json_table_config(tmp_path):
    """
    Create a mock JSON table config file for testing.
    """
    table_data = {
        "variable_entry": {
            "temp": {"frequency": "mon"},
            "salt": {"frequency": "mon"}
        }
    }
    table_file = tmp_path / "table_config.json"
    with open(table_file, "w") as f:
        json.dump(table_data, f)
    return str(table_file)

@patch('fre.cmor.cmor_mixer.update_calendar_type')
@patch('fre.cmor.cmor_mixer.cmorize_all_variables_in_dir')
@patch('fre.cmor.cmor_mixer.glob.glob')
def test_cmor_run_w_cal_type( mock_glob,
                              mock_cmorize_all_variables_in_dir,
                              mock_update_calendar_type,
                              mock_json_exp_config,
                              mock_json_var_list,
                              mock_json_table_config,
                              tmp_path):
    """
    Test that cmor_run_subtool calls update_calendar_type when calendar_type is provided.
    """
    # Arrange
    mock_glob.return_value = [
        str(tmp_path / "mock_test_file.00010101-00041231.temp.nc") ,
        str(tmp_path / "mock_test_file.00010101-00041231.salt.nc")   ]

    mock_cmorize_all_variables_in_dir.return_value = 0

    indir = str(tmp_path)
    outdir = str(tmp_path / "output")
    calendar_type = "noleap"

    # Act
    cmor_run_subtool(
        indir = indir,
        json_var_list = mock_json_var_list,
        json_table_config = mock_json_table_config,
        json_exp_config = mock_json_exp_config,
        outdir = outdir,
        calendar_type = calendar_type
    )

    ## Assert
    mock_update_calendar_type.assert_called_once_with(
        mock_json_exp_config, calendar_type, output_file_path=None )



@patch('fre.cmor.cmor_mixer.update_calendar_type')
@patch('fre.cmor.cmor_mixer.cmorize_all_variables_in_dir')
@patch('fre.cmor.cmor_mixer.glob.glob')
def test_cmor_run_no_cal_type( mock_glob,
                               mock_cmorize_all_variables_in_dir,
                               mock_update_calendar_type,
                               mock_json_exp_config,
                               mock_json_var_list,
                               mock_json_table_config,
                               tmp_path):
    """
    Test that cmor_run_subtool does not call update_calendar_type when calendar_type is None.
    """
    # Arrange
    mock_glob.return_value = [
        str(tmp_path / "mock_test_file.00010101-00041231.temp.nc") ,
        str(tmp_path / "mock_test_file.00010101-00041231.salt.nc")   ]

    mock_cmorize_all_variables_in_dir.return_value = 0

    indir = str(tmp_path)
    outdir = str(tmp_path / "output")
    calendar_type = None

    # Act - calendar_type is None (default)
    cmor_run_subtool(
        indir = indir,
        json_var_list = mock_json_var_list,
        json_table_config = mock_json_table_config,
        json_exp_config = mock_json_exp_config,
        outdir = outdir,
        calendar_type  =  None
    )

    # Assert
    mock_update_calendar_type.assert_not_called()
