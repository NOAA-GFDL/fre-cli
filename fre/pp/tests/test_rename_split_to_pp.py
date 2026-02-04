#tests rename_split_to_pp with a minimal python wrapper
#test cases: regrid/native, static/ts
#fail test cases: no files in your input directory/subdirs; input files are not named according to our very specific naming conventions


#https://stackoverflow.com/questions/67631/how-can-i-import-a-module-dynamically-given-the-full-path
#/archive/cew/CMIP7/ESM4/DEV/ESM4.5_staticfix/ppan-prod-openmp/history/00010101.nc.tar

import pytest
import sys
import os
from os import path as osp
import subprocess
import re
import pprint
from pathlib import Path
import cftime
from fre.pp.rename_split_script import *

def test_get_freq_and_format_from_two_dates():
    """
    Lookup some frequencies and formats between 2 dates
    """
    assert ("P1Y", "%Y")            == get_freq_and_format_from_two_dates(cftime.datetime(2009, 1, 1),       cftime.datetime(2010, 1, 1))
    assert ("P1M", "%Y%m")          == get_freq_and_format_from_two_dates(cftime.datetime(2009, 1, 1),       cftime.datetime(2009, 2, 1))
    assert ("P1D", "%Y%m%d")        == get_freq_and_format_from_two_dates(cftime.datetime(2009, 1, 1),       cftime.datetime(2009, 1, 2))
    assert ("PT1.0H", "%Y%m%d%H")   == get_freq_and_format_from_two_dates(cftime.datetime(2009, 1, 1, 0),    cftime.datetime(2009, 1, 1, 1))
    assert ("PT6.0H", "%Y%m%d%H")   == get_freq_and_format_from_two_dates(cftime.datetime(2009, 1, 1, 0),    cftime.datetime(2009, 1, 1, 6))
    assert ("PT0.5H", "%Y%m%d%H")   == get_freq_and_format_from_two_dates(cftime.datetime(2009, 1, 1, 0, 0), cftime.datetime(2009, 1, 1, 0, 30))

def test_get_duration_from_two_dates():
    """
    Lookup some durations between two dates
    """
    assert "P1M" == get_duration_from_two_dates(cftime.datetime(2009, 1, 1), cftime.datetime(2009, 2, 1))
    assert "P6M" == get_duration_from_two_dates(cftime.datetime(2009, 1, 1), cftime.datetime(2009, 7, 1))
    assert "P1Y" == get_duration_from_two_dates(cftime.datetime(2009, 1, 1), cftime.datetime(2010, 1, 1))
    assert "P5Y" == get_duration_from_two_dates(cftime.datetime(2000, 1, 1), cftime.datetime(2005, 1, 1))

ROOTDIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
print("Root directory: " + ROOTDIR)

TEST_DATA_DIR = os.path.join(ROOTDIR, "tests/test_files/rename-split")
print(TEST_DATA_DIR)
INDIR = os.path.join(TEST_DATA_DIR, "input")
OUTDIR = os.path.join(TEST_DATA_DIR, "output")
OG = os.path.join(TEST_DATA_DIR, "orig-output")

def test_rename_split_to_pp_setup():
    '''
    sets up the test files for the test cases
    '''
    nc_files = []; ncgen_commands = []
    for path,subdirs,files in os.walk(TEST_DATA_DIR):
      for name in files:
        if name.endswith("cdl"):
          name_out = re.sub(".cdl", ".nc", name)
          cdl_cmd = ["ncgen3", "-k", "netCDF-4", "-o", osp.join(path,name_out), osp.join(path,name)]
          nc_files.append(osp.join(path,name_out))
          ncgen_commands.append(cdl_cmd)
    for cmd in ncgen_commands:
      out0 = subprocess.run(cmd, capture_output=True)
      if out0.returncode != 0:
        print(out0.stdout)
    nc_exists = [osp.isfile(el) for el in nc_files]
    assert all(nc_exists)
    
def test_rename_split_to_pp_multiply():
  '''
  Takes every file with 'tile1' in the name and make 5 new copies.
  rename-split-to-pp needs 6 tile files - it throws an error if there are fewer -
  but it's not checking on whether the tiles match up with each other, so we can
  take one and copy it 5 times.
  '''
  nc_tile_files = []; t1 = 'tile1'; tile_patterns = ['tile2', 'tile3', 'tile4', 'tile5', 'tile6']
  for path,subdirs,files in os.walk(TEST_DATA_DIR):
    for name in files:
      if name.endswith(".nc") and re.search(t1, name) is not None:
        nc_tile_files.append(osp.join(path, name))
  assert len(nc_tile_files) == 8 #2 tile cases (daily,mon) * input,orig_output *regrid,native
  tp_files = []
  for nct in nc_tile_files:
    for tp in tile_patterns:
      tp_file = re.sub(t1, tp, nct)
      tp_files.append(tp_file)
      os.link(nct, tp_file)
  assert all([osp.isfile(el) for el in tp_files])
    
@pytest.mark.parametrize("hist_source,do_regrid,og_suffix", 
                          [ 
                          pytest.param("atmos_daily", False, "P1D/P6M/", id="day-native"),
                          pytest.param("atmos_daily", True, "P1D/P6M/", id="day-regrid"),
                          pytest.param("river_month", False, "P1M/P1Y/", id="mon-native"),
                          pytest.param("river_month", True, "P1M/P1Y/", id="mon-regrid"),
                          pytest.param("ocean_annual", False, "P1Y/P1Y/", id="year-native"),
                          pytest.param("ocean_annual", True, "P1Y/P1Y/", id="year-regrid"),
                          pytest.param("ocean_static", False, "P0Y/P0Y/", id="static-native"),
                          pytest.param("ocean_static", True, "P0Y/P0Y/", id="static-regrid"),
                          pytest.param("fail_filenames", False, "", id="fail-badfilename", marks=pytest.mark.xfail()),
                          pytest.param("fail_nofiles", False, "", id="fail-noinput", marks=pytest.mark.xfail()) ])
def test_rename_split_to_pp_run(hist_source, do_regrid, og_suffix):
    '''
    Tests the running of rename-split-to-pp, which takes 3 input args:
      hist_source: source of the history data, used to build input and output paths
      do_regrid: whether to do regridding, boolean, changes dir structure
      og_suffix: the frequency suffix that rename-split-to-pp should be adding to
         the output data dir structure
    rename-split-to-pp takes 4 arguments, which are set as env variables:
      inputDir (inputDir)  - location of your input files, output from split-netcdf
      outputDir (outputDir) - location to which to write your output files
      component (history_source) - VERY BADLY NAMED. What split-netcdf is calling the hist_source after the rewrite.
      use_subdirs (do_regrid) - either set to 1 or unset. 1 is used for the regridding case.
        * no longer set to 1 or unset, set to "True" or "False". Makes the if checks
        more sensitive, but makes the setup/teardown of unsetting env variables easier.
    These tests operate under 4 frequencies with regridding/no regridding cases:
      - success:
        - daily regrid/native, multiple tiles
        - monthly regird/native, multiple tiles (currently failing because of metadata)
        - annual regrid/native
        - static regrid/no regrid
      - failure:
        - files in input don't match naming convention, raises error TBD
        - no files in input dir, raises error TBD
    For the moment, rename=split-to-pp isn't doing any rewriting of files -
    it's copying files to new locations and verifying that they have the 
    right number of timesteps. 
    I've included hooks for functions that check on data + metadata, but we
    really don't need them yet.
    TODO:
      - when this is ported to python, the xfail tests should check for the python error that gets raised - 
      but until that point, not a whole lot of point in checking on a raised exception here
    '''
    # if not os.path.isdir(outputDir):
    #   os.mkdir(outputDir)
    # callstat = call_rename_split_to_pp(inputDir, outputDir, hist_source, do_regrid)
    # # #####
    
    print("do_regrid " + str(do_regrid))
    if do_regrid:
        print("do_regrid is set to True")
        os.environ["use_subdirs"] = "True"
        dir_suffix = hist_source + "-regrid"
        origDir = osp.join(OG, dir_suffix, "regrid", hist_source, og_suffix)
    else:
        #need to set in this branch b/c env variables aren't getting torn down - 
        #otherwise the 'True' from prior run sticks around
        os.environ["use_subdirs"] = "False"
        dir_suffix = hist_source + "-native"
        origDir = osp.join(OG, dir_suffix, hist_source, og_suffix)
    
    inputDir = osp.join(INDIR, dir_suffix)
    outputDir = osp.join(OUTDIR, dir_suffix)
    
    os.environ["inputDir"]  = inputDir
    os.environ["outputDir"] = outputDir
    os.environ["component"] = hist_source
    
    if not osp.exists(outputDir):
      os.makedirs(outputDir)

    # run the tool
    rename_split(inputDir, outputDir, hist_source, do_regrid)

    # check for expected output filepaths
    expected_files = [os.path.join(origDir, el) for el in os.listdir(origDir)]
    expected_files = [el for el in expected_files if el.endswith(".nc")]
    out_files = [re.sub(OG, OUTDIR, el) for el in expected_files]
    files_there = len(out_files) > 0
    if files_there:
        outdir = os.path.dirname(out_files[0])
        actual_out_files = [os.path.join(outdir,el) for el in os.listdir(outdir) if el.endswith(".nc")]
        out_files.sort()
        actual_out_files.sort()
        files_paired = all([el[0] == el[1] for el in zip(out_files, actual_out_files)])
    else:
        files_paired = False
    assert all([files_there, files_paired])

def test_rename_split_to_pp_cleanup():
    '''
    deletes the test files (any file ending with .nc) and output directories
    (any directory under output/)
    '''
    el_list = []
    dir_list = []
    #all dirs under output
    for path, subdirs, files in os.walk(OUTDIR):
      for name in subdirs:
        dir_list.append(osp.join(path,name))
    #all netcdf files
    for path, subdirs, files in os.walk(TEST_DATA_DIR):
      for name in files:
        if name.endswith(".nc"):
          el_list.append(osp.join(path,name))
    el_list = list(set(el_list))
    for f in el_list:
      os.remove(f)
    dir_list.sort(reverse=True)
    for d in dir_list:
      os.rmdir(d)
    dir_deleted = [not osp.isdir(el) for el in dir_list]
    el_deleted = [not osp.isdir(el) for el in el_list]
    assert all(el_deleted + dir_deleted)
