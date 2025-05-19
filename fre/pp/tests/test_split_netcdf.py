'''
Tests split-netcdf, parse_yaml from split_netcdf_script.py
'''

import pytest
import re
from fre.pp import split_netcdf_script
from fre.pp.split_netcdf_script import split_file_xarray, parse_yaml_for_varlist
import subprocess
import os
from os import path as osp
import pathlib
from pathlib import Path
from fre import fre

import click
from click.testing import CliRunner
runner=CliRunner()

#rootdir = Path(__file__).parents[3] #get to root directory
test_dir = osp.realpath("fre/tests/test_files/ascii_files/split_netcdf")
test_dir1  = osp.join(test_dir, "atmos_daily.tile3")
test_cdlfile1 = "00010101.atmos_daily.tile3.cdl"
test_ncfile1 = "00010101.atmos_daily.tile3.nc"

all_varlist = "all"
some_varlist = ["tasmax", "tasmin", "ps", "tasmin", "tas", "temp", "zsurf", "pv350K"]
none_varlist = ["tasmin","tasmax"]


#Set up splitting files
def test_split_file_setup():
    ''' Sets up the files we need in order to test variable splitting. Mostly ncgen3 commands.'''
    #ncgen the test file for test_dir1
    ncgen_commands = []
    nc_files = []
    sp_stat = []
    subdirs = [f.path for f in os.scandir(test_dir1) if f.is_dir()]
    for sd in subdirs:
        #for each directory in the current dir, make a new dir with "new_" prepended
        newdir = osp.join(test_dir1, "new_" + os.path.basename(sd))
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
                               osp.join(test_dir1, test_ncfile1), 
                               osp.join(test_dir1, test_cdlfile1)])
        for ncg in ncgen_commands:
            sp = subprocess.run(ncg, check = True, capture_output=True)
            sp_stat.append(sp.returncode)
        sp_success = [el == 0 for el in sp_stat]
        nc_files_exist = [osp.isfile(el) for el in nc_files]
    assert all( [ sp_success + nc_files_exist ] )

#test splitting files
@pytest.mark.parametrize("infile,outfiledir,varlist", 
                             [pytest.param(osp.join(test_dir1, test_ncfile1), "new_all_varlist",  "all", 
                                id="all"), 
                              pytest.param(osp.join(test_dir1, test_ncfile1), "new_some_varlist",
                                ",".join(some_varlist),
                                id="some"), 
                              pytest.param(osp.join(test_dir1, test_ncfile1), "new_none_varlist", 
                                ",".join(none_varlist), id='none')])
def test_split_file_run(infile, outfiledir, varlist):
    ''' Checks that split-netcdf will run when called from the command line 
    
        infile: netcdf file to split into single-var files
        outfiledir: directory to which to write the split netcdf files
          (new_all_varlist, new_some_varlist, new_none_varlist)
        varlist: comma-separated string specifying which variables to write 
          ("all", some_varlist, none_varlist)
        
        Parameters for the 3 tests are based off of the list of variables to filter on:
            all: "all", the default, processes all variables in the input
            some: processes a list of variables, some of which are and some of 
                which are not in the input; includes one duplicate var
            none: processes a list of variables, none of which are in the input;
                should produce no files'''
    outfiledir = osp.join(test_dir1, outfiledir)
    split_netcdf_args = ["pp", "split-netcdf", 
                                          "--file", infile, 
                                          "--outputdir", outfiledir, 
                                          "--variables", varlist]
    result = runner.invoke(fre.fre, args=split_netcdf_args)
    assert result.exit_code == 0

@pytest.mark.parametrize("newdir,origdir", 
                         [pytest.param("new_all_varlist", "all_varlist", id='all'), 
                         pytest.param("new_some_varlist", "some_varlist", id='some')])    
def test_split_file_data(newdir, origdir):
    ''' Checks that the data in the new files match the data in the old files
        newdir: the directory containing the newly-written files
          (new_all_varlist, new_some_varlist)
        origdir: dir containing the old files to check against
          (all_varlist, some_varlist)
        Parameters for the 2 tests differ based off the variable list from test_split_file_run: 
            all: "all", the default, processes all variables in the input
            some: processes a list of variables, some of which are and some of 
                which are not in the input; includes one duplicate var
                '''
    newdir = osp.join(test_dir1, newdir)
    origdir = osp.join(test_dir1, origdir)
    orig_count = len([el for el in os.listdir(origdir) if el.endswith(".nc")])
    split_files = [el for el in os.listdir(newdir) if el.endswith(".nc")]
    new_count = len(split_files)
    same_count_files = (new_count == orig_count)
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

@pytest.mark.parametrize("newdir,origdir",
                         [pytest.param("new_all_varlist", "all_varlist", id='all'),
                         pytest.param("new_some_varlist", "some_varlist", id='some')])
def test_split_file_metadata(newdir, origdir):
    ''' Checks that the metadata in the new files match the metadata in the old files 
        newdir: the directory containing the newly-written files
          (new_all_varlist, new_some_varlist)
        origdir: dir containing the old files to check against
          (all_varlist, some_varlist)
        Parameters for the 2 tests differ based off the variable list from test_split_file_run: 
            all: "all", the default, processes all variables in the input
            some: processes a list of variables, some of which are and some of 
                which are not in the input; includes one duplicate var
                '''
    newdir = osp.join(test_dir1, newdir)
    origdir = osp.join(test_dir1, origdir)
    orig_count = len([el for el in os.listdir(origdir) if el.endswith(".nc")])
    split_files = [el for el in os.listdir(newdir) if el.endswith(".nc")]
    new_count = len(split_files)
    same_count_files = (new_count == orig_count)
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

#clean up splitting files
def test_split_file_cleanup():
    ''' Cleaning up files and dirs created for this set of tests. 
        Deletes all netcdf files (*.nc) and all dirs created for this test (new_*)'''
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

#test parsing yaml
@pytest.mark.parametrize("component,compdir,varlist,hist_source", 
                             [("atmos", "all_varlist","all", "none"), 
                             ("atmos", "some_varlist", some_varlist, "none"), 
                             pytest.param("mantle", "none_varlist", 
                                          "", "none", marks=pytest.mark.xfail), 
                             pytest.param("atmos", "all_varlist", "all", 
                                          "atmos_diurnal", marks=pytest.mark.xfail)])
def test_parse_yaml(component, compdir, varlist, hist_source):
    ''' Tests parsing yaml for the variable_list we need for splitting 
        component: string corresponding to a component in the yaml
        compdir: directory in which to look for the yaml (all use same filename)
        varlist: list of variables expected to match what we get from the yaml
        hist_source: optional, string corresponding to a hist_source that should be under the component in the yaml
        
        Parameters for the tests are based off of the following: 
            parses the yaml, does not find a varlist, gets the right default
            parses the yaml, finds a varlist and it matches the orig results
            parses the yaml, does not find the component and throws an error
            parses the yaml, finds the varlist, but does not find a history_file
              under sources that matches the hist_source
            '''
    yamlfile = osp.join(osp.join(test_dir1, compdir), "am5_components_varlist.yml")
    if hist_source == "none":
      new_varlist = parse_yaml_for_varlist(yamlfile, component)
    else:
      new_varlist = parse_yaml_for_varlist(yamlfile, component, hist_source)  
    assert varlist == new_varlist
