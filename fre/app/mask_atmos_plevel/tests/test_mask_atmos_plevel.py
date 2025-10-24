"""
tests for the underlying python module behind fre app mask-atmos-plevel functionality
"""


import shutil
import subprocess
from pathlib import Path

import pytest
import xarray as xr

from fre.app.mask_atmos_plevel import mask_atmos_plevel

@pytest.fixture()
def tmp_input(tmp_path):
    # write netcdf files from the cdfs
    # data (ua)
    input_ = Path('fre/tests/test_files/reduced_ascii_files/atmos_cmip.ua_unmsk.cdl')
    assert Path(input_).exists()

    # create temporary directory
    tmp_dir = tmp_path
    tmp_dir.mkdir(exist_ok=True)
    tmp_input = Path(tmp_dir / "input.nc")

    # ncgen
    command = [ 'ncgen', '-o', tmp_input, input_ ]
    sp = subprocess.run(command, check = True)
    assert sp.returncode == 0
    assert tmp_input.exists()

    yield tmp_input

@pytest.fixture()
def tmp_case2input(tmp_path):
    # write netcdf files from the cdfs
    # data (ua)
    input_ = Path('fre/tests/test_files/reduced_ascii_files/atmos_cmip.ua_unmsk.case2.cdl')
    assert Path(input_).exists()

    # create temporary directory
    tmp_dir = tmp_path
    tmp_dir.mkdir(exist_ok=True)
    tmp_case2input = Path(tmp_dir / "input.nc")

    # ncgen
    command = [ 'ncgen', '-o', tmp_case2input, input_ ]
    sp = subprocess.run(command, check = True)
    assert sp.returncode == 0
    assert tmp_case2input.exists()

    yield tmp_case2input


@pytest.fixture()
def tmp_ps(tmp_path):
    # write netcdf files from the cdfs
    # data (ps)
    ps     = Path('fre/tests/test_files/reduced_ascii_files/atmos_cmip.ps.cdl')
    assert Path(ps).exists()

    # create temporary directory
    tmp_dir = tmp_path
    tmp_dir.mkdir(exist_ok=True)
    tmp_ps = Path(tmp_dir / "ps.nc")

    # ncgen
    command = [ 'ncgen', '-o', tmp_ps, ps ]
    sp = subprocess.run(command, check = True)
    assert sp.returncode == 0
    assert tmp_ps.exists()

    yield tmp_ps

@pytest.fixture()
def tmp_ref(tmp_path):
    # write netcdf files from the cdfs
    # data (ua)
    ref = Path('fre/tests/test_files/reduced_ascii_files/atmos_cmip.ua_masked.cdl')
    assert Path(ref).exists()

    # create temporary directory
    tmp_dir = tmp_path
    tmp_dir.mkdir(exist_ok=True)
    tmp_ref = Path(tmp_dir / "ref.nc")

    command = [ 'ncgen', '-o', tmp_ref, ref ]
    sp = subprocess.run(command, check = True)
    assert sp.returncode == 0
    assert tmp_ref.exists()

    yield tmp_ref

@pytest.fixture()
def tmp_case2ref(tmp_path):
    # write netcdf files from the cdfs
    # data (ua)
    ref = Path('fre/tests/test_files/reduced_ascii_files/atmos_cmip.ua_masked.case2.cdl')
    assert Path(ref).exists()

    # create temporary directory
    tmp_dir = tmp_path
    tmp_dir.mkdir(exist_ok=True)
    tmp_case2ref = Path(tmp_dir / "case2ref.nc")

    command = [ 'ncgen', '-o', tmp_case2ref, ref ]
    sp = subprocess.run(command, check = True)
    assert sp.returncode == 0
    assert tmp_case2ref.exists()

    yield tmp_case2ref

def test_mask_atmos_plevel(tmp_input, tmp_ps, tmp_ref, tmp_path): # pylint: disable=redefined-outer-name
    """
    Do the pressure masking on the test input file,
    and then compare to a previously generated output file.
    """
    tmp_output = Path(tmp_path / "output.nc")

    mask_atmos_plevel.mask_atmos_plevel_subtool(tmp_input, tmp_ps, tmp_output)
    assert tmp_output.exists()

    ds = xr.open_dataset(tmp_output)
    ds_ref = xr.open_dataset(tmp_ref)

    assert ds['ua_unmsk'].values.all() == ds_ref['ua_unmsk'].values.all()

def test_mask_atmos_plevel_case2(tmp_case2input, tmp_ps, tmp_case2ref, tmp_path): # pylint: disable=redefined-outer-name
    """
    Do the pressure masking on the test input file,
    and then compare to a previously generated output file.
    """
    tmp_output = Path(tmp_path / "output.nc")

    mask_atmos_plevel.mask_atmos_plevel_subtool(tmp_case2input, tmp_ps, tmp_output)
    assert tmp_output.exists()

    ds = xr.open_dataset(tmp_output)
    ds_ref = xr.open_dataset(tmp_case2ref)

    assert ds['ua_unmsk'].values.all() == ds_ref['ua_unmsk'].values.all()
    assert ds['ua'].values.all() == ds_ref['ua'].values.all()


def test_mask_atmos_plevel_recreate_output(tmp_input, tmp_ps, tmp_ref, tmp_path): # pylint: disable=redefined-outer-name
    """
    Do the pressure masking on the test input file, remaking an existing output file
    and then compare to a previously generated output file.
    """
    tmp_output = Path(tmp_path / "output.nc")

    # copy the reference output to the output path, it should be re-created
    shutil.copy(str(tmp_ref), str(tmp_output))

    mask_atmos_plevel.mask_atmos_plevel_subtool(tmp_input, tmp_ps, tmp_output)
    assert tmp_output.exists()

    ds = xr.open_dataset(tmp_output)
    ds_ref = xr.open_dataset(tmp_ref)

    assert ds['ua_unmsk'].values.all() == ds_ref['ua_unmsk'].values.all()


def test_mask_atmos_plevel_nopsfile_noop(tmp_input, tmp_ps, tmp_path): # pylint: disable=redefined-outer-name
    """
    if the input file exists, but the ps file does not, then no-op gracefully
    without raising an exception or throwing an error
    """
    tmp_output = Path(tmp_path / "output.nc")

    # remove the ps file
    tmp_ps.unlink()
    assert not tmp_ps.exists()

    mask_atmos_plevel.mask_atmos_plevel_subtool(infile = tmp_input,
                                                psfile = tmp_ps,
                                                outfile = tmp_output)
    assert not tmp_output.exists()


def test_mask_atmos_plevel_nops_error(tmp_input, tmp_path): # pylint: disable=redefined-outer-name
    """
    if the input and ps files exist, but the ps file does not have ps within it, raise ValueError
    """
    tmp_ps = tmp_input # this is OK, it just has to NOT have ps
    tmp_output = Path(tmp_path / "output.nc")

    with pytest.raises(ValueError):
        mask_atmos_plevel.mask_atmos_plevel_subtool(infile = tmp_input,
                                                    psfile = tmp_ps,
                                                    outfile = tmp_output,
                                                    warn_no_ps = False)
    assert not tmp_output.exists()


def test_mask_atmos_plevel_nops_warn(tmp_input, tmp_path): # pylint: disable=redefined-outer-name
    """
    if the input file exists, but the ps file does not, then no-op gracefully
    without raising an exception or throwing an error while warn_no_ps = True
    """
    tmp_ps = tmp_input # this is OK, it just has to NOT have ps
    tmp_output = Path(tmp_path / "output.nc")

    mask_atmos_plevel.mask_atmos_plevel_subtool(infile = tmp_input,
                                                psfile = tmp_ps,
                                                outfile = tmp_output,
                                                warn_no_ps = True)
    assert not tmp_output.exists()


def test_mask_atmos_plevel_exception():
    """ if the input file doesnt exist, error """
    with pytest.raises(FileNotFoundError):
        mask_atmos_plevel.mask_atmos_plevel_subtool(infile = 'Does not exist',
                                                    psfile = 'does not exist',
                                                    outfile = 'will not be created')
