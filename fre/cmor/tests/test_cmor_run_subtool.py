'''
tests for fre.cmor.cmor_run_subtool
'''

from datetime import date
import json
import os
from pathlib import Path
import subprocess
import shutil

import pytest

from fre.cmor import cmor_run_subtool

# import path constants from conftest
from .conftest import (
    ROOTDIR, INDIR, VARLIST, VARLIST_DIFF, VARLIST_MAPPED, VARLIST_EMPTY,
    EXP_CONFIG, GRID, GRID_LABEL, NOM_RES, CALENDAR_TYPE,
    DATETIMES_INPUTFILE, FULL_INPUTFILE,
    CMIP6_CMOR_CREATES_DIR, YYYYMMDD,
)


# ── case 1: successful CMORization (sos → sos) ─────────────────────────────

def test_setup_cmor_cmip_table_repo(cmip6_table_config):
    '''Verify the CMIP6 table repo and config exist.'''
    assert Path(cmip6_table_config).exists()

def test_setup_fre_cmor_run_subtool(sos_nc_file, capfd):
    '''Generate the sos NetCDF file via fixture.'''
    assert Path(sos_nc_file).exists()
    _out, _err = capfd.readouterr()

def test_fre_cmor_run_subtool_case1(sos_nc_file, cmip6_table_config, tmp_path, capfd):
    '''fre cmor run, test-use case: sos → sos (key == value).'''
    outdir = str(tmp_path / 'outdir')

    result = cmor_run_subtool(
        indir = str(INDIR),
        json_var_list = str(VARLIST),
        json_table_config = cmip6_table_config,
        json_exp_config = str(EXP_CONFIG),
        outdir = outdir,
        run_one_mode = True,
        grid_label = GRID_LABEL,
        grid = GRID,
        nom_res = NOM_RES,
        calendar_type = CALENDAR_TYPE
    )
    assert result == 0, f'expected success (0), got {result}'

    # verify output was produced somewhere under outdir
    output_ncs = list(Path(outdir).rglob('sos_Omon_*.nc'))
    assert len(output_ncs) > 0, 'no output sos file found'
    assert Path(sos_nc_file).exists(), 'input file should still exist'
    _out, _err = capfd.readouterr()


def test_fre_cmor_run_subtool_case1_output_compare_data(sos_nc_file, cmip6_table_config, tmp_path, capfd):
    '''I/O data-only comparison of test case1.'''
    outdir = str(tmp_path / 'outdir')

    cmor_run_subtool(
        indir = str(INDIR),
        json_var_list = str(VARLIST),
        json_table_config = cmip6_table_config,
        json_exp_config = str(EXP_CONFIG),
        outdir = outdir,
        run_one_mode = True,
        grid_label = GRID_LABEL,
        grid = GRID,
        nom_res = NOM_RES,
        calendar_type = CALENDAR_TYPE
    )

    output_ncs = list(Path(outdir).rglob('sos_Omon_*.nc'))
    assert len(output_ncs) > 0, 'no output sos file found'
    full_outputfile = str(output_ncs[0])

    nccmp_cmd = ['nccmp', '-f', '-d', sos_nc_file, full_outputfile]
    result = subprocess.run(' '.join(nccmp_cmd), shell=True, check=False, capture_output=True)

    err_list = result.stderr.decode().split('\n')
    expected_err = "DIFFER : FILE FORMATS : NC_FORMAT_NETCDF4 <> NC_FORMAT_NETCDF4_CLASSIC"
    assert result.returncode == 1
    assert len(err_list) == 2
    assert '' in err_list
    assert expected_err in err_list
    _out, _err = capfd.readouterr()


def test_fre_cmor_run_subtool_case1_output_compare_metadata(sos_nc_file, cmip6_table_config, tmp_path, capfd):
    '''I/O metadata-only comparison of test case1.'''
    outdir = str(tmp_path / 'outdir')

    cmor_run_subtool(
        indir = str(INDIR),
        json_var_list = str(VARLIST),
        json_table_config = cmip6_table_config,
        json_exp_config = str(EXP_CONFIG),
        outdir = outdir,
        run_one_mode = True,
        grid_label = GRID_LABEL,
        grid = GRID,
        nom_res = NOM_RES,
        calendar_type = CALENDAR_TYPE
    )

    output_ncs = list(Path(outdir).rglob('sos_Omon_*.nc'))
    assert len(output_ncs) > 0, 'no output sos file found'
    full_outputfile = str(output_ncs[0])

    nccmp_cmd = ['nccmp', '-f', '-m', '-g', sos_nc_file, full_outputfile]
    result = subprocess.run(' '.join(nccmp_cmd), shell=True, check=False)
    assert result.returncode == 1
    _out, _err = capfd.readouterr()


# ── case 2: error path (sosV2 filename but sos inside → mismatch) ──────────

def test_fre_cmor_run_subtool_case2(sosv2_nc_file, cmip6_table_config, tmp_path, capfd):
    '''fre cmor run, test-use case2: filename variable != file variable should error.
    The sosV2 file has variable "sos" inside, but the varlist expects "sosV2" as the
    modeler variable name (in both the filename and inside the file). This mismatch
    should cause cmor_run_subtool to return a non-zero status.'''
    outdir = str(tmp_path / 'outdir')

    result = cmor_run_subtool(
        indir = str(INDIR),
        json_var_list = str(VARLIST_DIFF),
        json_table_config = cmip6_table_config,
        json_exp_config = str(EXP_CONFIG),
        outdir = outdir,
        run_one_mode = True,
        grid_label = GRID_LABEL,
        grid = GRID,
        nom_res = NOM_RES,
        calendar_type = CALENDAR_TYPE
    )
    assert result != 0, f'expected non-zero return status for filename/variable mismatch, got {result}'
    _out, _err = capfd.readouterr()


# ── case 3: mapped variable (sea_sfc_salinity → sos) ──────────────────────

def test_fre_cmor_run_subtool_case3(mapped_nc_file, cmip6_table_config, tmp_path, capfd):
    '''fre cmor run, test-use case3: modeler variable "sea_sfc_salinity" mapped to MIP
    table variable "sos". The file is named with sea_sfc_salinity and contains the
    variable sea_sfc_salinity inside. CMORization should succeed because the filename
    variable matches the file variable.'''
    outdir = str(tmp_path / 'outdir')

    result = cmor_run_subtool(
        indir = str(INDIR),
        json_var_list = str(VARLIST_MAPPED),
        json_table_config = cmip6_table_config,
        json_exp_config = str(EXP_CONFIG),
        outdir = outdir,
        run_one_mode = True,
        grid_label = GRID_LABEL,
        grid = GRID,
        nom_res = NOM_RES,
        calendar_type = CALENDAR_TYPE
    )
    assert result == 0, f'expected success (0) for mapped variable, got {result}'

    # verify output was produced — CMOR should have created a file with the MIP table name "sos"
    output_ncs = list(Path(outdir).rglob('sos_Omon_*.nc'))
    assert len(output_ncs) > 0, 'no output sos file found for mapped variable case'
    assert Path(mapped_nc_file).exists(), 'input file should still exist'
    _out, _err = capfd.readouterr()


def test_fre_cmor_run_subtool_case3_output_compare_data(mapped_nc_file, cmip6_table_config, tmp_path, capfd):
    '''I/O data-only comparison of case3 — mapped variable (sea_sfc_salinity → sos).
    Since the input variable name (sea_sfc_salinity) differs from the output variable
    name (sos), nccmp -d reports additional "variable not found" diffs beyond the
    format difference. We verify those additional diffs correspond to the expected
    variable name mismatch.'''
    outdir = str(tmp_path / 'outdir')

    cmor_run_subtool(
        indir = str(INDIR),
        json_var_list = str(VARLIST_MAPPED),
        json_table_config = cmip6_table_config,
        json_exp_config = str(EXP_CONFIG),
        outdir = outdir,
        run_one_mode = True,
        grid_label = GRID_LABEL,
        grid = GRID,
        nom_res = NOM_RES,
        calendar_type = CALENDAR_TYPE
    )

    output_ncs = list(Path(outdir).rglob('sos_Omon_*.nc'))
    assert len(output_ncs) > 0, 'no output sos file found for mapped variable case'
    full_outputfile = str(output_ncs[0])

    nccmp_cmd = ['nccmp', '-f', '-d', mapped_nc_file, full_outputfile]
    result = subprocess.run(' '.join(nccmp_cmd), shell=True, check=False, capture_output=True)

    err_list = result.stderr.decode().split('\n')
    expected_format_err = "DIFFER : FILE FORMATS : NC_FORMAT_NETCDF4 <> NC_FORMAT_NETCDF4_CLASSIC"
    assert result.returncode == 1
    assert expected_format_err in err_list
    # variable names differ (sea_sfc_salinity vs sos), so nccmp also reports
    # that each variable is missing from the other file — this is expected
    assert any('sea_sfc_salinity' in line for line in err_list), \
        'expected nccmp to mention the mapped variable name sea_sfc_salinity'
    _out, _err = capfd.readouterr()


def test_fre_cmor_run_subtool_case3_output_compare_metadata(mapped_nc_file, cmip6_table_config, tmp_path, capfd):
    '''I/O metadata-only comparison of case3 — mapped variable (sea_sfc_salinity → sos).'''
    outdir = str(tmp_path / 'outdir')

    cmor_run_subtool(
        indir = str(INDIR),
        json_var_list = str(VARLIST_MAPPED),
        json_table_config = cmip6_table_config,
        json_exp_config = str(EXP_CONFIG),
        outdir = outdir,
        run_one_mode = True,
        grid_label = GRID_LABEL,
        grid = GRID,
        nom_res = NOM_RES,
        calendar_type = CALENDAR_TYPE
    )

    output_ncs = list(Path(outdir).rglob('sos_Omon_*.nc'))
    assert len(output_ncs) > 0, 'no output sos file found for mapped variable case'
    full_outputfile = str(output_ncs[0])

    nccmp_cmd = ['nccmp', '-f', '-m', '-g', mapped_nc_file, full_outputfile]
    result = subprocess.run(' '.join(nccmp_cmd), shell=True, check=False)
    assert result.returncode == 1
    _out, _err = capfd.readouterr()


# ── git cleanup ────────────────────────────────────────────────────────────

def test_git_cleanup():
    '''
    Performs a git restore on EXP_CONFIG to avoid false positives from
    git's record of changed files. It's supposed to change as part of the test.
    '''
    is_ci = os.environ.get("GITHUB_WORKSPACE") is not None
    if not is_ci:
        git_cmd = f"git restore {EXP_CONFIG}"
        restore = subprocess.run(git_cmd, shell=True, check=False)
        check_cmd = f"git status | grep {EXP_CONFIG}"
        check = subprocess.run(check_cmd, shell=True, check=False)
        assert all([restore.returncode == 0,
                    check.returncode == 1])


# ── error path tests ──────────────────────────────────────────────────────

def test_cmor_run_subtool_raise_value_error():
    '''test that ValueError raised when required args are absent'''
    with pytest.raises(ValueError):
        cmor_run_subtool( indir = None,
                          json_var_list = None,
                          json_table_config = None,
                          json_exp_config = None,
                          outdir = None )

def test_fre_cmor_run_subtool_no_exp_config(cmip6_table_config):
    '''fre cmor run, exception, json_exp_config DNE'''
    with pytest.raises(FileNotFoundError):
        cmor_run_subtool(
            indir = str(INDIR),
            json_var_list = str(VARLIST_DIFF),
            json_table_config = cmip6_table_config,
            json_exp_config = 'DOES NOT EXIST',
            outdir = str(ROOTDIR / 'outdir')
        )

def test_fre_cmor_run_subtool_empty_varlist(cmip6_table_config):
    '''fre cmor run, exception, variable list is empty'''
    with pytest.raises(ValueError):
        cmor_run_subtool(
            indir = str(INDIR),
            json_var_list = str(VARLIST_EMPTY),
            json_table_config = cmip6_table_config,
            json_exp_config = str(EXP_CONFIG),
            outdir = str(ROOTDIR / 'outdir')
        )

def test_fre_cmor_run_subtool_opt_var_name_not_in_table(cmip6_table_config):
    '''fre cmor run, exception, opt_var_name not in table'''
    with pytest.raises(ValueError):
        cmor_run_subtool(
            indir = str(INDIR),
            json_var_list = str(VARLIST),
            json_table_config = cmip6_table_config,
            json_exp_config = str(EXP_CONFIG),
            outdir = str(ROOTDIR / 'outdir'),
            opt_var_name="difmxybo"
        )


def test_fre_cmor_run_subtool_missing_mip_era(cmip6_table_config, tmp_path):
    '''KeyError when the exp config JSON has no mip_era entry.'''
    bad_exp = tmp_path / 'no_mip_era.json'
    exp_data = {"institution_id": "TEST", "source_id": "TEST-1-0"}
    bad_exp.write_text(json.dumps(exp_data))

    with pytest.raises(KeyError, match='noncompliant'):
        cmor_run_subtool(
            indir = str(INDIR),
            json_var_list = str(VARLIST),
            json_table_config = cmip6_table_config,
            json_exp_config = str(bad_exp),
            outdir = str(ROOTDIR / 'outdir'),
        )


def test_fre_cmor_run_subtool_unsupported_mip_era(cmip6_table_config, tmp_path):
    '''ValueError when mip_era is present but not CMIP6 or CMIP7.'''
    bad_exp = tmp_path / 'bad_mip_era.json'
    with open(str(EXP_CONFIG), 'r', encoding='utf-8') as f:
        exp_data = json.load(f)
    exp_data['mip_era'] = 'CMIP99'
    bad_exp.write_text(json.dumps(exp_data))

    with pytest.raises(ValueError, match='only supports CMIP6 and CMIP7'):
        cmor_run_subtool(
            indir = str(INDIR),
            json_var_list = str(VARLIST),
            json_table_config = cmip6_table_config,
            json_exp_config = str(bad_exp),
            outdir = str(ROOTDIR / 'outdir'),
        )
