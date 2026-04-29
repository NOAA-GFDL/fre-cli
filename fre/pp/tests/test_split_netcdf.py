'''
Tests split-netcdf, parse_yaml from split_netcdf_script.py
'''

import os
import pathlib
import re
import subprocess
from os import path as osp
from pathlib import Path

import click
import pytest
import xarray as xr
from click.testing import CliRunner

from fre import fre
from fre.pp import split_netcdf_script
from fre.pp.split_netcdf_script import split_file_xarray


runner=CliRunner()

#rootdir = Path(__file__).parents[3] #get to root directory
test_dir = osp.realpath("fre/tests/test_files/ascii_files/split_netcdf")

cases = {"ts": {"dir":"atmos_daily.tile3",
                 "nc": "00010101.atmos_daily.tile3.nc",
                 "cdl": "00010101.atmos_daily.tile3.cdl"},
         "static": {"dir": "ocean_static",
                     "nc": "00010101.ocean_static.nc",
                     "cdl": "00010101.ocean_static.cdl"}}

casedirs = [osp.join(test_dir, el) for el in [cases["ts"]["dir"], cases["static"]["dir"]]]

all_ts_varlist = "all"
some_ts_varlist = ["tasmax", "tasmin", "ps", "tasmin", "tas", "temp", "zsurf", "pv350K"]
none_ts_varlist = ["tasmin","tasmax"]

all_static_varlist = "all"
some_static_varlist = ["wet", "wet_c", "wet_v"] #should drop xh dim


#Set up splitting files
def test_split_file_setup():
    ''' Sets up the files we need in order to test variable splitting. Mostly ncgen3 commands.'''
    #ncgen the test file for test_dir1
    ncgen_commands = []
    nc_files = []
    sp_stat = []
    for testcase in cases.keys():
        cds = osp.join(test_dir,cases[testcase]["dir"])
        subdirs = [f.path for f in os.scandir(cds) if f.is_dir()]
        for sd in subdirs:
            #for each directory in the current dir, make a new dir with "new_" prepended
            newdir = osp.join(cds, "new_" + os.path.basename(sd))
            if not osp.exists(newdir):
                os.makedirs(newdir)
                print(newdir)
            cdl_files = [f.path for f in os.scandir(sd) if f.is_file]
            cdl_files = [el for el in cdl_files if re.search("cdl", el) is not None]
            for cdlf in cdl_files:
                cdl_out = re.sub(".cdl", ".nc", cdlf)
                cdlf_cmd = ["ncgen3", "-k", "netCDF-4", "-o", cdl_out, cdlf]
                nc_files.append(cdl_out)
                ncgen_commands.append(cdlf_cmd)
            ncgen_commands.append(["ncgen3", "-k", "netCDF-4", "-o",
                                   osp.join(cds, cases[testcase]["nc"]),
                                   osp.join(cds, cases[testcase]["cdl"])])
            for ncg in ncgen_commands:
                print(ncg)
                sp = subprocess.run(ncg, check = True, capture_output=True)
                sp_stat.append(sp.returncode)
            sp_success = [el == 0 for el in sp_stat]
            nc_files_exist = [osp.isfile(el) for el in nc_files]
    assert all( [ sp_success + nc_files_exist ] )

#test splitting files
@pytest.mark.parametrize("workdir,infile,outfiledir,varlist",
                             [pytest.param(casedirs[0], cases["ts"]["nc"],
                                "new_all_ts_varlist",  "all",
                                id="ts_all"),
                              pytest.param(casedirs[0], cases["ts"]["nc"],
                                "new_some_ts_varlist",
                                ",".join(some_ts_varlist),
                                id="ts_some"),
                              pytest.param(casedirs[0], cases["ts"]["nc"],
                                "new_none_ts_varlist",
                                ",".join(none_ts_varlist), id='none'),
                              pytest.param(casedirs[1], cases["static"]["nc"],
                                "new_all_static_varlist",  "all",
                                id="static_all"),
                              pytest.param(casedirs[1], cases["static"]["nc"],
                                "new_some_static_varlist",
                                ",".join(some_static_varlist),
                                id="static_some")])
def test_split_file_run(workdir,infile, outfiledir, varlist):
    ''' Checks that split-netcdf will run when called from the command line

    :param workdir: subdir all operations are relative to
    :type workdir: string
    :param infile: netcdf file to split into single-var files
    :type infile: string
    :param outfiledir: directory to which to write the split netcdf files
        (new_all_ts_varlist, new_some_ts_varlist, new_none_ts_varlist)
    :type outfiledir: string
    :param varlist: comma-separated string specifying which variables to write ("all", some_ts_varlist, none_ts_varlist)
    :type varlist: string
    :type origdir: string

    Parameters for the 5 tests are based off of the list of variables to
    filter on plus the type of file:

    - all: "all", the default, processes all variables in the input
    - some: processes a list of variables, some of which are and some of which
      are not in the input; includes one duplicate var
    - none: processes a list of variables, none of which are in the input;
      should produce no files
    - ts: timeseries files
    - static: static files
    '''
    infile = osp.join(workdir, infile)
    outfiledir = osp.join(workdir, outfiledir)
    split_netcdf_args = ["pp", "split-netcdf",
                                          "--file", infile,
                                          "--outputdir", outfiledir,
                                          "--variables", varlist]
    print(split_netcdf_args)
    result = runner.invoke(fre.fre, args=split_netcdf_args)
    print(result)
    assert result.exit_code == 0

@pytest.mark.parametrize("workdir,newdir,origdir",
                         [pytest.param(casedirs[0],"new_all_ts_varlist", "all_ts_varlist", id='ts_all'),
                         pytest.param(casedirs[0],"new_some_ts_varlist", "some_ts_varlist", id='ts_some'),
                         pytest.param(casedirs[1],"new_all_static_varlist", "all_static_varlist", id='static_all'),
                         pytest.param(casedirs[1],"new_some_static_varlist", "some_static_varlist", id='static_some')])
def test_split_file_data(workdir,newdir, origdir):
    ''' Checks that the data in the new files match the data in the old files
    :param workdir: dir that all operations are relative to
    :type workdir: string
    :param newdir: the directory containing the newly-written files (new_all_ts_varlist, new_some_ts_varlist)
    :type newdir: string
    :param origdir: dir containing the old files to check against (all_ts_varlist, some_ts_varlist)
    :type origdir: string

    Parameters for the tests differ based off the variable list from
    test_split_file_run and the type of file being split:

    - all: "all", the default, processes all variables in the input
    - some: processes a list of variables, some of which are and some of
      which are not in the input; includes one duplicate var
    - ts: timeseries files
    - static: static files
    '''
    newdir = osp.join(workdir, newdir)
    origdir = osp.join(workdir, origdir)
    orig_count = len([el for el in os.listdir(origdir) if el.endswith(".nc")])
    split_files = [el for el in os.listdir(newdir) if el.endswith(".nc")]
    new_count = len(split_files)
    same_count_files = new_count == orig_count
    print(f"orig dir: {origdir}  new dir: {newdir}")
    print(f"orig count: {orig_count}  new count: {new_count}")
    all_files_equal=True
    for sf in split_files:
        nccmp_cmd = [ 'nccmp', '-d', '--force',
                    osp.join(origdir, sf), osp.join(newdir, sf) ]
        sp = subprocess.run( nccmp_cmd)
        if sp.returncode != 0:
            all_files_equal=False
            print(" ".join(nccmp_cmd))
            print("comparison of " + nccmp_cmd[-1] + " and " + nccmp_cmd[-2] + " did not match")
            print(sp.stdout, sp.stderr)
    assert all_files_equal and same_count_files

#test_split_file_metadata is currently commented out because the set of commands:
#  ncdump file.nc > file.cdl
#  ncgen3 -k netcdf-4 -o new_file.nc file.cdl
#produces different metadata on the _FillValue in each context.
#everything else seems to be matching; discussing this at the code review.

@pytest.mark.parametrize("workdir,newdir,origdir",
                         [pytest.param(casedirs[0],"new_all_ts_varlist", "all_ts_varlist", id='all'),
                         pytest.param(casedirs[0],"new_some_ts_varlist", "some_ts_varlist", id='some'),
                         pytest.param(casedirs[1],"new_all_static_varlist", "all_static_varlist", id='static_all'),
                         pytest.param(casedirs[1],"new_some_static_varlist", "some_static_varlist", id='static_some')])
def test_split_file_metadata(workdir,newdir, origdir):
    ''' Checks that the metadata in the new files match the metadata in the old files
    :param workdir: dir that all operations are relative to
    :type workdir: string
    :param newdir: the directory containing the newly-written files (new_all_ts_varlist, new_some_ts_varlist)
    :type newdir: string
    :param origdir: dir containing the old files to check against (all_ts_varlist, some_ts_varlist)
    :type origdir: string

    Parameters for the tests differ based off the variable list from
    test_split_file_run and the type of file being split:

    - all: "all", the default, processes all variables in the input
    - some: processes a list of variables, some of which are and some of
      which are not in the input; includes one duplicate var
    - ts: timeseries files
    - static: static files
    '''
    newdir = osp.join(workdir, newdir)
    origdir = osp.join(workdir, origdir)
    orig_count = len([el for el in os.listdir(origdir) if el.endswith(".nc")])
    split_files = [el for el in os.listdir(newdir) if el.endswith(".nc")]
    new_count = len(split_files)
    same_count_files = new_count == orig_count
    all_files_equal=True
    for sf in split_files:
        nccmp_cmd = [ 'nccmp', '-mg', '--force',
                     osp.join(origdir, sf), osp.join(newdir, sf) ]
        sp = subprocess.run( nccmp_cmd)
        if sp.returncode != 0:
            print(" ".join(nccmp_cmd))
            all_files_equal=False
            print("comparison of " + nccmp_cmd[-1] + " and " + nccmp_cmd[-2] + " did not match")
            print(sp.stdout, sp.stderr)
    assert all_files_equal and same_count_files

def test_variable_filtering_bug_fix():
    ''' Test that variables with names containing short metadata var names are not excluded.
    
    This test verifies the fix for a bug where the matching logic was incorrectly applied
    to both known patterns and the list of short variable names (e.g., "a", "b"), causing
    variables like "drybc" to be excluded because they contain "b".
    
    The bug was that short vars were treated as patterns instead of exact matches.
    '''
    # Create a mock dataset with variables that would trigger the old bug
    import numpy as np
    import tempfile
    
    # Create dimensions
    time = xr.DataArray(np.arange(10), dims=['time'])
    lat = xr.DataArray(np.arange(5), dims=['lat'])
    lon = xr.DataArray(np.arange(5), dims=['lon'])
    
    # Create variables: some data vars with names that contain short var letters
    data_vars = {
        'drybc': (['time', 'lat', 'lon'], np.random.rand(10, 5, 5)),  # Should be included
        'wetbc': (['time', 'lat', 'lon'], np.random.rand(10, 5, 5)),  # Should be included
        'temp': (['time', 'lat', 'lon'], np.random.rand(10, 5, 5)),   # Should be included
        'a': (['time'], np.random.rand(10)),                          # Short var, should be excluded
        'b': (['lat'], np.random.rand(5)),                            # Short var, should be excluded
        'time_bnds': (['time', 'nv'], np.random.rand(10, 2)),         # Pattern match, should be excluded
        'average_T1': (['time'], np.random.rand(10)),                 # Pattern match, should be excluded
    }
    
    # Create coordinates
    coords = {
        'time': time,
        'lat': lat,
        'lon': lon,
        'nv': [0, 1],
    }
    
    ds = xr.Dataset(data_vars=data_vars, coords=coords)
    
    # Use a temporary directory for output
    with tempfile.TemporaryDirectory() as tmpdir:
        # Call split_file_xarray with "all" to get all data vars
        split_file_xarray.__wrapped__ = split_file_xarray  # Access the original function
        
        # We need to test the internal logic. Since split_file_xarray writes files,
        # let's test the filtering logic by inspecting the datavars.
        # Actually, let's modify the function to return the datavars for testing.
        
        # For now, let's call it and check the output files
        output_file = osp.join(tmpdir, 'test.nc')
        # But split_file_xarray expects an input file, so we need to save ds first
        input_file = osp.join(tmpdir, 'input.nc')
        ds.to_netcdf(input_file)
        
        split_file_xarray(input_file, tmpdir, "all")
        
        # Check which files were created
        output_files = [f for f in os.listdir(tmpdir) if f.endswith('.nc') and f != 'input.nc']
        
        # Expected data vars: drybc, wetbc, temp (3D+ vars)
        # Excluded: a, b (1D), time_bnds (pattern), average_T1 (pattern)
        expected_vars = {'drybc', 'wetbc', 'temp'}
        actual_vars = {f.replace('input.', '').replace('.nc', '') for f in output_files}
        
        assert actual_vars == expected_vars, f"Expected {expected_vars}, got {actual_vars}"

#clean up splitting files
def test_split_file_cleanup():
    ''' Cleaning up files and dirs created for this set of tests.
        Deletes all netcdf files (*.nc) and all dirs created for this test (new_*)
        '''
    el_list = []
    dir_list = []
    for path, subdirs, files in os.walk(test_dir):
        for name in files:
            el_list.append(osp.join(path, name))
        for name in subdirs:
            dir_list.append(osp.join(path,name))
    netcdf_files = [el for el in el_list if el.endswith(".nc")]
    for nc in netcdf_files:
        pathlib.Path.unlink(Path(nc))
    newdir = [el for el in dir_list if osp.basename(el).startswith("new_")]
    for nd in newdir:
        pathlib.Path.rmdir(Path(nd))
    dir_deleted = [not osp.isdir(el) for el in newdir]
    el_deleted = [not osp.isdir(el) for el in netcdf_files]
    assert all(el_deleted + dir_deleted)
