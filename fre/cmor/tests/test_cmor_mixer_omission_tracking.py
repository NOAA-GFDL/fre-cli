"""
Tests for omission tracking in cmorize_all_variables_in_dir
===========================================================

Verifies that when cmorize_target_var_files raises an exception for one or
more variables, the failures are collected and a summary omission log is
emitted at the end of processing, including the expected file paths.
"""

import logging
from unittest.mock import patch

import pytest

from fre.cmor.cmor_mixer import cmorize_all_variables_in_dir


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

DUMMY_ARGS = dict(
    indir='/fake/indir',
    iso_datetime_range_arr=['00010101-00041231'],
    name_of_set='component',
    json_exp_config='/fake/exp.json',
    outdir='/fake/outdir',
    mip_var_cfgs={'variable_entry': {}},
    json_table_config='/fake/table.json',
    run_one_mode=False,
)


# ---------------------------------------------------------------------------
# tests
# ---------------------------------------------------------------------------

@patch('fre.cmor.cmor_mixer.cmorize_target_var_files')
def test_omission_tracking_single_failure(mock_cmorize, caplog):
    """A single variable failure is tracked and logged with variable name and file path."""
    mock_cmorize.side_effect = RuntimeError('test failure')

    with caplog.at_level(logging.WARNING, logger='fre.cmor.cmor_mixer'):
        status = cmorize_all_variables_in_dir(
            vars_to_run={'var_a': 'var_a'},
            **DUMMY_ARGS,
        )

    assert status == 1
    assert any('OMISSION LOG' in msg for msg in caplog.messages)
    assert any('var_a' in msg and 'test failure' in msg for msg in caplog.messages)
    # file path should appear in the omission log
    expected_path = '/fake/indir/component.00010101-00041231.var_a.nc'
    assert any(expected_path in msg for msg in caplog.messages)


@patch('fre.cmor.cmor_mixer.cmorize_target_var_files')
def test_omission_tracking_multiple_failures(mock_cmorize, caplog):
    """Multiple variable failures are each tracked and all appear in the summary with file paths."""
    mock_cmorize.side_effect = RuntimeError('kaboom')

    with caplog.at_level(logging.WARNING, logger='fre.cmor.cmor_mixer'):
        status = cmorize_all_variables_in_dir(
            vars_to_run={'alpha': 'alpha', 'beta': 'beta'},
            **DUMMY_ARGS,
        )

    assert status == 1
    assert any('2 variables could not be processed' in msg for msg in caplog.messages)
    assert any('alpha' in msg for msg in caplog.messages)
    assert any('beta' in msg for msg in caplog.messages)
    # both file paths should appear
    assert any('/fake/indir/component.00010101-00041231.alpha.nc' in msg for msg in caplog.messages)
    assert any('/fake/indir/component.00010101-00041231.beta.nc' in msg for msg in caplog.messages)


@patch('fre.cmor.cmor_mixer.cmorize_target_var_files')
def test_no_omission_log_when_all_succeed(mock_cmorize, caplog):
    """When every variable succeeds, no omission summary is logged."""
    mock_cmorize.return_value = None  # success

    with caplog.at_level(logging.WARNING, logger='fre.cmor.cmor_mixer'):
        status = cmorize_all_variables_in_dir(
            vars_to_run={'good_var': 'good_var'},
            **DUMMY_ARGS,
        )

    assert status == 0
    assert not any('OMISSION LOG' in msg for msg in caplog.messages)


@patch('fre.cmor.cmor_mixer.cmorize_target_var_files')
def test_omission_tracking_mixed_success_failure(mock_cmorize, caplog):
    """Only failed variables appear in the omission log with their file paths."""
    def side_effect(indir, target_var, local_var, *args, **kwargs):
        if local_var == 'bad_var':
            raise ValueError('bad variable error')

    mock_cmorize.side_effect = side_effect

    with caplog.at_level(logging.WARNING, logger='fre.cmor.cmor_mixer'):
        status = cmorize_all_variables_in_dir(
            vars_to_run={'good_var': 'good_var', 'bad_var': 'bad_var'},
            **DUMMY_ARGS,
        )

    assert status == 1
    assert any('1 variable could not be processed' in msg for msg in caplog.messages)
    assert any('bad_var' in msg and 'bad variable error' in msg for msg in caplog.messages)
    # bad_var file path should appear
    assert any('/fake/indir/component.00010101-00041231.bad_var.nc' in msg for msg in caplog.messages)
    # good_var should not appear in any omission log entry
    omission_entries = [msg for msg in caplog.messages if 'OMITTED' in msg or 'file:' in msg]
    assert not any('good_var' in entry for entry in omission_entries)
