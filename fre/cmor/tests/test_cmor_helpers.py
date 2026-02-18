'''
tests for fre.cmor helper functions in cmor_helpers
'''

import json
from pathlib import Path

import numpy as np
import pytest

from fre.cmor.cmor_helpers import ( find_statics_file, print_data_minmax,
                                    find_gold_ocean_statics_file,
                                    create_lev_bnds, get_iso_datetime_ranges, iso_to_bronx_chunk,
                                    create_tmp_dir, get_json_file_data,
                                    update_grid_and_label, get_bronx_freq_from_mip_table, #update_outpath,
                                    filter_brands )

def test_iso_to_bronx_chunk():
    ''' tests value error raising by iso_to_bronx_chunk '''
    with pytest.raises(ValueError,
                       match='problem with converting to bronx chunk from the cmor chunk. check cmor_yamler.py'):
        iso_to_bronx_chunk('foo')

def test_find_statics_file_success():
    ''' what happens when no statics file is found given a bronx directory structure '''
    target_file = 'fre/tests/test_files/ascii_files/mock_archive/' + \
                  'USER/CMIP7/ESM4/DEV/ESM4.5v01_om5b04_piC/' + \
                  'gfdl.ncrc5-intel23-prod-openmp/pp/ocean_monthly/ts/monthly/5yr/ocean_monthly.000101-000102.sos.nc'
    if not Path(target_file).exists():
        Path(target_file).touch()
    assert Path(target_file).exists()

    expected_answer_statics_file = 'fre/tests/test_files/ascii_files/mock_archive/' + \
                                   'USER/CMIP7/ESM4/DEV/ESM4.5v01_om5b04_piC/' + \
                                   'gfdl.ncrc5-intel23-prod-openmp/pp/ocean_monthly/ocean_monthly.static.nc'
    if not Path(expected_answer_statics_file).exists():
        Path(expected_answer_statics_file).touch()
    assert Path(expected_answer_statics_file).exists

    statics_file = find_statics_file( bronx_file_path = target_file
                                      )
    assert Path(statics_file).exists()
    assert statics_file == expected_answer_statics_file


def test_find_statics_file_nothing_found():
    ''' what happens when a statics file is found given a bronx directory structure '''
    statics_file = find_statics_file(
        bronx_file_path = 'fre/tests/test_files/ascii_files/' + \
                          'mock_archive/USER/CMIP7/ESM4/DEV/ESM4.5v01_om5b04_piC/' + \
                          'gfdl.ncrc5-intel23-prod-openmp/pp/land/ts/monthly/5yr/land.000101-000512.lai.nc' )
    assert statics_file is None


def test_print_data_minmax_no_exception_case1():
    ''' checks to make sure this doesn't raise an exception '''
    print_data_minmax(None, None)

def test_print_data_minmax_no_exception_case2():
    ''' checks to make sure this doesn't raise an exception '''
    print_data_minmax(np.ma.core.MaskedArray( data=(0, 10, 20, 30) ), None)

def test_print_data_minmax_no_exception_case3():
    ''' checks to make sure this doesn't raise an exception '''
    print_data_minmax(np.ma.core.MaskedArray( data=(0, 10, 20, 30) ), 'foo')


# ---- find_gold_ocean_statics_file tests ----

def test_find_gold_ocean_statics_file_none_arg():
    ''' put_copy_here=None should return None immediately '''
    result = find_gold_ocean_statics_file(put_copy_here=None)
    assert result is None


def test_find_gold_ocean_statics_file_archive_missing(tmp_path):
    '''
    when the archive gold file does not exist on disk (i.e. not at PPAN),
    the function should create the local directory tree but return None
    because there's nothing to copy.
    '''
    result = find_gold_ocean_statics_file(put_copy_here=str(tmp_path))
    # on dev boxes the archive path won't exist, so we get None
    if result is None:
        # it should have still created the directory tree
        # the function strips the first 3 path components (['', 'archive', 'gold'])
        # from '/archive/gold/datasets/...' so the mirrored tree starts at 'datasets/'
        expected_subdir = tmp_path / 'datasets' / 'OM5_025' / 'ocean_mosaic_v20250916_unpacked'
        assert expected_subdir.is_dir()
    else:
        # if we happen to be at PPAN and it succeeded, just check it's a real file
        assert Path(result).is_file()


def test_find_gold_ocean_statics_file_mock_copy(tmp_path):
    '''
    exercise the full copy path by creating a fake archive gold file in tmp_path
    and monkeypatching ARCHIVE_GOLD_DATA_DIR so the function finds it.
    '''
    import fre.cmor.cmor_helpers as _helpers_mod
    import fre.cmor.cmor_constants as _const_mod

    # build a fake archive layout:  <tmp>/gold/datasets/OM5_025/.../ocean_static.nc
    fake_archive_root = tmp_path / 'fake_archive' / 'gold' / 'datasets'
    fake_gold_file = fake_archive_root / 'OM5_025' / 'ocean_mosaic_v20250916_unpacked' / 'ocean_static.nc'
    fake_gold_file.parent.mkdir(parents=True, exist_ok=True)
    fake_gold_file.write_text('placeholder')

    staging_dir = tmp_path / 'staging'

    # monkeypatch the constant in both cmor_constants and cmor_helpers (where it's already imported)
    original_val = _const_mod.ARCHIVE_GOLD_DATA_DIR
    try:
        _const_mod.ARCHIVE_GOLD_DATA_DIR = str(fake_archive_root)
        _helpers_mod.ARCHIVE_GOLD_DATA_DIR = str(fake_archive_root)
        result = find_gold_ocean_statics_file(put_copy_here=str(staging_dir))
    finally:
        _const_mod.ARCHIVE_GOLD_DATA_DIR = original_val
        _helpers_mod.ARCHIVE_GOLD_DATA_DIR = original_val

    assert result is not None
    assert Path(result).is_file()
    assert 'ocean_static.nc' in result


# ---- create_lev_bnds failure case ----

def test_create_lev_bnds_length_mismatch():
    ''' create_lev_bnds should raise ValueError when len(with_these) != len(bound_these)+1 '''
    bound_these = np.array([10.0, 20.0, 30.0])
    with_these = np.array([5.0, 15.0])  # wrong: should be len 4 (=3+1)
    with pytest.raises(ValueError, match='failed creating bnds'):
        create_lev_bnds(bound_these=bound_these, with_these=with_these)


def test_create_lev_bnds_length_mismatch_too_long():
    ''' same check, but with_these is too long instead of too short '''
    bound_these = np.array([10.0, 20.0])
    with_these = np.array([5.0, 15.0, 25.0, 35.0])  # wrong: should be len 3 (=2+1)
    with pytest.raises(ValueError, match='failed creating bnds'):
        create_lev_bnds(bound_these=bound_these, with_these=with_these)


# ---- get_iso_datetime_ranges with stop_yr ----

# helper filenames that look like FRE-bronx time-series files
_SAMPLE_FILENAMES = [
    'ocean_monthly.19900101-19941231.sos.nc',
    'ocean_monthly.19950101-19991231.sos.nc',
    'ocean_monthly.20000101-20041231.sos.nc',
    'ocean_monthly.20050101-20091231.sos.nc',
    'ocean_monthly.20100101-20141231.sos.nc',
]


def test_get_iso_datetime_ranges_no_filter():
    ''' all 5 date ranges should appear when start/stop are None '''
    result = []
    get_iso_datetime_ranges(var_filenames=_SAMPLE_FILENAMES,
                            iso_daterange_arr=result)
    assert len(result) == 5
    assert '19900101-19941231' in result
    assert '20100101-20141231' in result


def test_get_iso_datetime_ranges_with_stop():
    ''' only date ranges whose end-year <= 2004 should survive '''
    result = []
    get_iso_datetime_ranges(var_filenames=_SAMPLE_FILENAMES,
                            iso_daterange_arr=result,
                            stop='2004')
    # ranges ending in 1994, 1999, 2004 qualify; 2009, 2014 do not
    assert '19900101-19941231' in result
    assert '19950101-19991231' in result
    assert '20000101-20041231' in result
    assert '20050101-20091231' not in result
    assert '20100101-20141231' not in result
    assert len(result) == 3


def test_get_iso_datetime_ranges_with_start():
    ''' only date ranges whose start-year >= 2000 should survive '''
    result = []
    get_iso_datetime_ranges(var_filenames=_SAMPLE_FILENAMES,
                            iso_daterange_arr=result,
                            start='2000')
    assert '19900101-19941231' not in result
    assert '19950101-19991231' not in result
    assert '20000101-20041231' in result
    assert '20050101-20091231' in result
    assert '20100101-20141231' in result
    assert len(result) == 3


def test_get_iso_datetime_ranges_with_start_and_stop():
    ''' start=1995 stop=2004 should give exactly two ranges '''
    result = []
    get_iso_datetime_ranges(var_filenames=_SAMPLE_FILENAMES,
                            iso_daterange_arr=result,
                            start='1995',
                            stop='2004')
    assert result == ['19950101-19991231', '20000101-20041231']


def test_get_iso_datetime_ranges_none_arr_raises():
    ''' passing iso_daterange_arr=None should raise ValueError '''
    with pytest.raises(ValueError, match='requires the list'):
        get_iso_datetime_ranges(var_filenames=_SAMPLE_FILENAMES,
                                iso_daterange_arr=None)


def test_get_iso_datetime_ranges_no_matches_raises():
    ''' if the filter excludes everything, ValueError should be raised '''
    result = []
    with pytest.raises(ValueError, match='length 0'):
        get_iso_datetime_ranges(var_filenames=_SAMPLE_FILENAMES,
                                iso_daterange_arr=result,
                                start='2050',
                                stop='2060')


# ---- create_tmp_dir tests ----

def test_create_tmp_dir_success(tmp_path):
    ''' create_tmp_dir should create a tmp/ subdirectory and return its path '''
    result = create_tmp_dir(outdir=str(tmp_path))
    assert Path(result).is_dir()
    assert result.endswith('/CMOR_tmp')


def test_create_tmp_dir_with_exp_config(tmp_path):
    ''' when json_exp_config has an outpath key, a subdirectory should also be created '''
    exp_config = tmp_path / 'exp_config.json'
    exp_config.write_text(json.dumps({"outpath": "CMIP7/output"}))
    result = create_tmp_dir(outdir=str(tmp_path), json_exp_config=str(exp_config))
    assert Path(result).is_dir()
    assert Path(result, 'CMIP7/output').is_dir()


def test_create_tmp_dir_oserror(tmp_path):
    ''' create_tmp_dir should raise OSError when directory creation fails '''
    # /dev/null is not a directory; we can't mkdir inside it
    with pytest.raises(OSError, match='problem creating tmp output directory'):
        create_tmp_dir(outdir='/dev/null/impossible_path')


# ---- get_json_file_data tests ----

def test_get_json_file_data_success(tmp_path):
    ''' should load and return JSON content '''
    f = tmp_path / 'data.json'
    payload = {"key": "value", "num": 42}
    f.write_text(json.dumps(payload))
    assert get_json_file_data(str(f)) == payload


def test_get_json_file_data_nonexistent():
    ''' should raise FileNotFoundError for a missing file '''
    with pytest.raises(FileNotFoundError, match='cannot be opened'):
        get_json_file_data('/nonexistent/path/file.json')


def test_get_json_file_data_invalid_json(tmp_path):
    ''' should raise FileNotFoundError (wrapping JSONDecodeError) for invalid JSON '''
    f = tmp_path / 'bad.json'
    f.write_text('NOT JSON {{{{')
    with pytest.raises(FileNotFoundError, match='cannot be opened'):
        get_json_file_data(str(f))


# ---- update_grid_and_label None-args test ----

def test_update_grid_and_label_none_grid_label(tmp_path):
    ''' should raise ValueError when new_grid_label is None '''
    f = tmp_path / 'exp.json'
    f.write_text(json.dumps({"grid_label": "gr", "grid": "g", "nominal_resolution": "50 km"}))
    with pytest.raises(ValueError):
        update_grid_and_label(str(f), None, "new_grid", "100 km")


def test_update_grid_and_label_none_grid(tmp_path):
    ''' should raise ValueError when new_grid is None '''
    f = tmp_path / 'exp.json'
    f.write_text(json.dumps({"grid_label": "gr", "grid": "g", "nominal_resolution": "50 km"}))
    with pytest.raises(ValueError):
        update_grid_and_label(str(f), "gn", None, "100 km")


def test_update_grid_and_label_none_nom_res(tmp_path):
    ''' should raise ValueError when new_nom_res is None '''
    f = tmp_path / 'exp.json'
    f.write_text(json.dumps({"grid_label": "gr", "grid": "g", "nominal_resolution": "50 km"}))
    with pytest.raises(ValueError):
        update_grid_and_label(str(f), "gn", "new_grid", None)


# ---- get_bronx_freq_from_mip_table tests ----

def test_get_bronx_freq_from_mip_table_success(tmp_path):
    ''' should return the bronx-equivalent frequency for a valid table '''
    table = {
        "variable_entry": {
            "sos": {"frequency": "mon", "other": "stuff"}
        }
    }
    f = tmp_path / 'Omon.json'
    f.write_text(json.dumps(table))
    assert get_bronx_freq_from_mip_table(str(f)) == "monthly"

def test_get_bronx_freq_from_mip_table_no_freq(tmp_path):
    ''' should raise bronx-equivalent frequency for a valid table '''
    table = {
        "variable_entry": {
            "sos": {"other": "stuff"}
        }
    }
    f = tmp_path / 'Omon.json'
    f.write_text(json.dumps(table))
    with pytest.raises(KeyError,
                       match='no frequency in table under variable_entry. this may be a CMIP7 table.'):
        get_bronx_freq_from_mip_table(str(f))

def test_get_bronx_freq_from_mip_table_invalid_freq(tmp_path):
    ''' should raise KeyError when the table frequency is not a valid MIP frequency '''
    table = {
        "variable_entry": {
            "sos": {"frequency": "bogus_freq"}
        }
    }
    f = tmp_path / 'Obogus.json'
    f.write_text(json.dumps(table))
    with pytest.raises(KeyError, match='not a valid MIP frequency'):
        get_bronx_freq_from_mip_table(str(f))

## ---- update_outpath tests ----
#
#def test_update_outpath_none_json_path():
#    ''' should raise ValueError when json_file_path is None '''
#    with pytest.raises(ValueError):
#        update_outpath(None, '/some/output/path')
#
#
#def test_update_outpath_none_output_path(tmp_path):
#    ''' should raise ValueError when output_file_path is None '''
#    f = tmp_path / 'exp.json'
#    f.write_text(json.dumps({"outpath": "/old/path"}))
#    with pytest.raises(ValueError):
#        update_outpath(str(f), None)


# ---- filter_brands tests ----

def _make_mip_var_cfgs(var_brands_dims):
    '''helper: build a minimal mip_var_cfgs dict from {mip_key: dims_string} pairs'''
    return {"variable_entry": {k: {"dimensions": v} for k, v in var_brands_dims.items()}}


def test_filter_brands_time_filter_selects_mean():
    ''' brand with time (mean) should be selected when input has time_bnds '''
    mip = _make_mip_var_cfgs({
        "sos_mean-2d":  "longitude latitude time",
        "sos_inst-2d":  "longitude latitude time1",
    })
    result = filter_brands(
        brands=["mean-2d", "inst-2d"],
        target_var="sos",
        mip_var_cfgs=mip,
        has_time_bnds=True,
        input_vert_dim=0,
    )
    assert result == "mean-2d"


def test_filter_brands_time_filter_selects_inst():
    ''' brand with time1 (instantaneous) should be selected when input lacks time_bnds '''
    mip = _make_mip_var_cfgs({
        "sos_mean-2d":  "longitude latitude time",
        "sos_inst-2d":  "longitude latitude time1",
    })
    result = filter_brands(
        brands=["mean-2d", "inst-2d"],
        target_var="sos",
        mip_var_cfgs=mip,
        has_time_bnds=False,
        input_vert_dim=0,
    )
    assert result == "inst-2d"


def test_filter_brands_vertical_filter():
    ''' vertical filter should select the brand whose MIP dims contain the expected vert dim '''
    mip = _make_mip_var_cfgs({
        "temp_mean-3d-native-sea": "longitude latitude olevel time",
        "temp_mean-2d":            "longitude latitude time",
    })
    result = filter_brands(
        brands=["mean-3d-native-sea", "mean-2d"],
        target_var="temp",
        mip_var_cfgs=mip,
        has_time_bnds=True,
        input_vert_dim="z_l",
    )
    assert result == "mean-3d-native-sea"


def test_filter_brands_all_eliminated():
    ''' should raise ValueError when all brands are filtered out '''
    mip = _make_mip_var_cfgs({
        "sos_a": "longitude latitude time1",
        "sos_b": "longitude latitude time1",
    })
    with pytest.raises(ValueError, match='none survived'):
        filter_brands(
            brands=["a", "b"],
            target_var="sos",
            mip_var_cfgs=mip,
            has_time_bnds=True,
            input_vert_dim=0,
        )


def test_filter_brands_multiple_remain():
    ''' should raise ValueError when multiple brands survive filtering '''
    mip = _make_mip_var_cfgs({
        "sos_a": "longitude latitude time",
        "sos_b": "longitude latitude time",
    })
    with pytest.raises(ValueError, match='remain for sos'):
        filter_brands(
            brands=["a", "b"],
            target_var="sos",
            mip_var_cfgs=mip,
            has_time_bnds=True,
            input_vert_dim=0,
        )
