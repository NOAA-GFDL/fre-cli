'''
tests for fre.app.regrid_xy submodule
'''

import os
from pathlib import Path
import shutil
from shutil import which

import pytest
import numpy as np
import xarray as xr

import fre.app.regrid_xy.regrid_xy as regrid_xy
import fre.app.regrid_xy.tests.generate_files as generate_files

WHICH_FREGRID = which('fregrid')
HAVE_FREGRID = WHICH_FREGRID is not None and WHICH_FREGRID.split('/')[-1] == 'fregrid'

nxy = 20
date = "20250729"

curr_dir = os.getcwd()
yamlfile = Path(curr_dir)/"test_yaml.yaml"
grid_spec_tar = Path(curr_dir)/"grid_spec.tar"
input_dir = Path(curr_dir)/"test_inputs"
output_dir = Path(curr_dir)/"test_outputs"
remap_dir= Path(curr_dir)/"test_remap"
work_dir = Path(curr_dir)/"test_work"

components = []
pp_input_files = [{"history_file":"pemberley"}, {"history_file":"longbourn"}]
components.append({"xyInterp": f"{nxy},{nxy}",
                   "interpMethod": "conserve_order2",
                   "inputRealm": "atmos",
                   "type": f"pride_and_prejudice",
                   "sources": pp_input_files,
                   "postprocess_on": True}
)
emma_input_files = [{"history_file":"hartfield"}, {"history_file":"donwell_abbey"}]
components.append({"xyInterp": f"{nxy},{nxy}",
                   "interpMethod": "conserve_order2",
                   "inputRealm": "atmos",
                   "type": f"emma",
                   "sources": emma_input_files,
                   "postprocess_on": True}
)
here_input_files = [{"history_file":"gfdl"}, {"history_file":"princeton"}]
components.append({"xyInterp": f"{nxy},{nxy}",
                   "interpMethod": "conserve_order2",
                   "inputRealm": "atmos",
                   "type": "here",
                   "sources": here_input_files,
                   "postprocess_on": False}
)


def setup_test():
    ''' setup test directories and generate test files '''
    input_dir.mkdir(exist_ok=True)
    output_dir.mkdir(exist_ok=True)
    remap_dir.mkdir(exist_ok=True)
    work_dir.mkdir(exist_ok=True)

    #generate test files
    generate_files.set_test(components_in=components,
                            date_in=date,
                            grid_spec_tar_in=str(grid_spec_tar),
                            yamlfile_in=str(yamlfile),
                            input_dir_in=str(input_dir))
    generate_files.make_all()


def cleanup_test():
    ''' remove test directories '''
    if output_dir.exists():
        shutil.rmtree(output_dir)
    if remap_dir.exists():
        shutil.rmtree(remap_dir)
    if work_dir.exists():
        shutil.rmtree(work_dir)
    generate_files.cleanup()

@pytest.mark.skipif(not HAVE_FREGRID,
                    reason='fregrid not in env. it was removed from package reqs. you must load it externally')
def test_regrid_xy():
    """
    Tests the main function regrid_xy and ensures
    data is regridded correctly
    """

    setup_test()

    #modify generate_files to change sources
    for source_dict in pp_input_files + emma_input_files + here_input_files:
        source = source_dict["history_file"]
        regrid_xy.regrid_xy(yamlfile=str(yamlfile),
                            input_dir=str(input_dir),
                            output_dir=str(output_dir),
                            work_dir=str(work_dir),
                            remap_dir=str(remap_dir),
                            source=source,
                            input_date=date+"TTTT")

    #check answers
    for source_dict in pp_input_files + emma_input_files:
        # Files are now output to a subdirectory based on grid size and interpolation method
        output_subdir = output_dir/f"{nxy}_{nxy}.conserve_order2"
        outfile = output_subdir/f"{date}.{source_dict['history_file']}.nc"

        test = xr.load_dataset(outfile)

        assert "wet_c" not in test
        assert "mister" in test
        assert "darcy" in test
        assert "wins" in test

        assert np.all(test["mister"].values==np.float64(1.0))
        assert np.all(test["darcy"].values==np.float64(2.0))
        assert np.all(test["wins"].values==np.float64(3.0))

    #check answers, these shouldn't have been regridded
    for source_dict in here_input_files:
        ifile = source_dict["history_file"]
        assert not (output_dir/f"{date}.{ifile}.nc").exists()

    #check remap_file exists and is not empty
    remap_file = remap_dir/f"C{nxy}_mosaicX{nxy}by{nxy}_conserve_order2.nc"
    assert remap_file.exists()

    cleanup_test()

@pytest.mark.skipif(not HAVE_FREGRID,
                    reason='fregrid not in env. it was removed from package reqs. you must load it externally')
def test_get_input_mosaic():
    """
    Tests get_input_mosaic correctly copies the mosaic file to the input directory
    """

    grid_spec = Path("grid_spec.nc")
    mosaic_file = Path("ocean_mosaic.nc")

    generate_files.make_grid_spec()
    mosaic_file.touch()

    datadict=dict(grid_spec=grid_spec, inputRealm="ocean")

    assert regrid_xy.get_input_mosaic(datadict) == str(mosaic_file)

    mosaic_file.unlink()  #clean up
    grid_spec.unlink()  #clean up

@pytest.mark.skipif(not HAVE_FREGRID,
                    reason='fregrid not in env. it was removed from package reqs. you must load it externally')
def test_get_input_file():
    """
    Tests get_input_file
    """

    input_date = "20250807"
    source = "pemberley"
    datadict = {"input_date": input_date}
    assert regrid_xy.get_input_file(datadict, source) == input_date + "." + source

    datadict["input_date"] = None
    assert regrid_xy.get_input_file(datadict, source) == source

@pytest.mark.skipif(not HAVE_FREGRID,
                    reason='fregrid not in env. it was removed from package reqs. you must load it externally')
def test_get_remap_file():
    """
    Tests get_remap_file
    """

    remap_dir = Path("remap_dir")
    input_mosaic = "C20_mosaic"
    nlon = 40
    nlat = 10
    interp_method = "conserve_order1"

    datadict = {"remap_dir": remap_dir.name,
                "input_mosaic": input_mosaic+".nc",
                "output_nlon": nlon,
                "output_nlat": nlat,
                "interp_method": interp_method}

    #check remap file from current directory is copied to input directory
    remap_file = Path(f"remap_dir/{input_mosaic}X{nlon}by{nlat}_{interp_method}.nc")
    assert regrid_xy.get_remap_file(datadict) == str(remap_dir/remap_file)

    remap_dir.mkdir(exist_ok=True)
    remap_file.touch()
    assert regrid_xy.get_remap_file(datadict) == str(remap_dir/remap_file)

    Path(remap_file).unlink()
    shutil.rmtree(remap_dir)
