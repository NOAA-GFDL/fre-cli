"""
Calendar-type integration tests for cmor_run_subtool
=====================================================

These tests verify that cmor_run_subtool correctly handles the
``calendar_type`` parameter:

- When a calendar_type is provided  → ``update_calendar_type`` is called.
- When calendar_type is None        → ``update_calendar_type`` is NOT called.

Heavy internal work (file globbing, CMORization, outpath updating) is
mocked so the tests focus exclusively on the calendar-type routing logic.
"""

import json
from unittest.mock import patch

import pytest

from fre.cmor.cmor_mixer import cmor_run_subtool


# ---------------------------------------------------------------------------
# shared fixtures – minimal JSON configs written to tmp_path
# ---------------------------------------------------------------------------

@pytest.fixture
def exp_config_file(tmp_path):
    """Minimal CMIP6 experiment configuration JSON (with outpath for update_outpath)."""
    config = {
        "mip_era": "cmip6",
        "calendar": "360_day",
        "grid": "test_grid",
        "grid_label": "gn",
        "nominal_resolution": "1 km",
        "outpath": "."
    }
    path = tmp_path / "exp_config.json"
    path.write_text(json.dumps(config))
    return str(path)


@pytest.fixture
def var_list_file(tmp_path):
    """Variable-list JSON mapping local names to target names."""
    path = tmp_path / "var_list.json"
    path.write_text(json.dumps({"temp": "temp", "salt": "salt"}))
    return str(path)


@pytest.fixture
def table_config_file(tmp_path):
    """MIP-table JSON with two stub variable entries."""
    table = {
        "variable_entry": {
            "temp": {"frequency": "mon"},
            "salt": {"frequency": "mon"}
        }
    }
    path = tmp_path / "table_config.json"
    path.write_text(json.dumps(table))
    return str(path)


@pytest.fixture
def fake_nc_filenames(tmp_path):
    """Return a list of fake NetCDF filenames that glob would find."""
    return [
        str(tmp_path / "mock_test_file.00010101-00041231.temp.nc"),
        str(tmp_path / "mock_test_file.00010101-00041231.salt.nc")
    ]


# ---------------------------------------------------------------------------
# tests
# ---------------------------------------------------------------------------

# Shared set of mocks – everything that would touch the filesystem or CMOR
_MOCKS = [
    'fre.cmor.cmor_mixer.update_calendar_type',
    'fre.cmor.cmor_mixer.cmorize_all_variables_in_dir',
    'fre.cmor.cmor_mixer.glob.glob',
]


@patch(_MOCKS[0])
@patch(_MOCKS[1])
@patch(_MOCKS[2])
def test_cmor_run_w_cal_type(
    mock_glob,
    mock_cmorize,
    mock_update_cal,
    exp_config_file,
    var_list_file,
    table_config_file,
    fake_nc_filenames,
    tmp_path
):
    """When calendar_type is provided, update_calendar_type must be called."""

    mock_glob.return_value = fake_nc_filenames
    mock_cmorize.return_value = 0
    calendar_type = "noleap"

    cmor_run_subtool(
        indir            = str(tmp_path),
        json_var_list    = var_list_file,
        json_table_config = table_config_file,
        json_exp_config  = exp_config_file,
        outdir           = str(tmp_path / "output"),
        calendar_type    = calendar_type
    )

    mock_update_cal.assert_called_once_with(
        exp_config_file, calendar_type, output_file_path=None
    )


@patch(_MOCKS[0])
@patch(_MOCKS[1])
@patch(_MOCKS[2])
def test_cmor_run_no_cal_type(
    mock_glob,
    mock_cmorize,
    mock_update_cal,
    exp_config_file,
    var_list_file,
    table_config_file,
    fake_nc_filenames,
    tmp_path
):
    """When calendar_type is None (default), update_calendar_type must NOT be called."""

    mock_glob.return_value = fake_nc_filenames
    mock_cmorize.return_value = 0

    cmor_run_subtool(
        indir            = str(tmp_path),
        json_var_list    = var_list_file,
        json_table_config = table_config_file,
        json_exp_config  = exp_config_file,
        outdir           = str(tmp_path / "output"),
        calendar_type    = None
    )

    mock_update_cal.assert_not_called()
