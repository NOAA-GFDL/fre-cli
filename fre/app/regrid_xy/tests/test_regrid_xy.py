from pathlib import Path
import pytest
import subprocess
import os
import shutil

# directories for tests
LOCAL_TEST_DIR = os.getcwd() + "/fre/app/regrid_xy/tests/test_inputs_outputs/"
LOCAL_ALL_TEST_OUT_DIR  = "out-test-dir/"
LOCAL_REMAP_DIR = LOCAL_TEST_DIR + 'remap-dir/'
LOCAL_REMAP_TEST_DIR = LOCAL_TEST_DIR + 'remap-test-dir/'
LOCAL_TEST_OUT_DIR = LOCAL_TEST_DIR + 'out-dir/'

# official data/mosaic stuff
GOLD_GRID_SPEC = "/archive/gold/datasets/OM4_05/mosaic_c96.v20180227.tar"
GOLD_GRID_SPEC_NO_TAR = LOCAL_TEST_DIR + "mosaic.nc"
TEST_DATA_IN_DIR  = "/archive/oar.gfdl.fre_test/canopy_test_data/app/regrid-xy/"
TEST_CDL_GRID_FILE = "C96_mosaic.cdl"
TEST_NC_GRID_FILE = "C96_mosaic.nc"

## for rose configuration
COMPONENT='atmos'
NLON=288
NLAT=180
INPUT_GRID='cubedsphere'
INPUT_REALM='atmos'
INTERP_METHOD='conserve_order1'
YYYYMMDD='20030101'
SOURCE='atmos_static_cmip' # generally a list, but for tests, only one
                           # note that components will not always contain a
                           # a source file of the same name

# clobber current output or no?
CLEAN_ALL_OUTPUT = False
if CLEAN_ALL_OUTPUT:
    shutil.rmtree(LOCAL_TEST_DIR+'20030101.nc/'    )
    shutil.rmtree(LOCAL_TEST_DIR+'out-dir/'        )
    shutil.rmtree(LOCAL_TEST_DIR+'out-test-dir/'   )
    shutil.rmtree(LOCAL_TEST_DIR+'remap-dir/'      )
    shutil.rmtree(LOCAL_TEST_DIR+'remap-test-dir/' )
    shutil.rmtree(LOCAL_TEST_DIR+'work/'           )


# TODO this needs to be edited
"""
create test input files for regridding via ngen, ncgen3
create regridded files via make_hgrid and fregrid to
compare to regridded files made via regrid_xy

# Usage on runnung this app test for regrid_xy is as follows:
0) cd /path/to/postprocessing/
1) module conda fre-nctools nccmp
2) conda activate cylc-8.2.1

# if pytest and netCDF4 aren't present, pip install them
# may need a --user flag.
3) pip install netCDF4 pytest [pylint, if desired]
4) export PATH=/home/$USER/.local/bin:$PATH

# for rose to find the python script, AND have this be
# an importable module, create symbolic links
5) cd app && ln -s regrid-xy regrid_xy
6) cd regrid_xy && ln -s shared bin/shared

# to run tests, call pytest as module and give it the full
# path to the test script.
7) python -m pytest $PWD/fre/app/regrid_xy/test/test_regrid_xy.py
"""


#@pytest.mark.skip(reason='debug')
def test_make_ncgen3_nc_inputs(capfd):
    '''
    set-up test: ncgen3 netcdf file inputs for later steps
    if the output exists, it will not bother remaking it
    '''
    global d
    d = LOCAL_TEST_DIR + f'{YYYYMMDD}.nc/'
    Path(d).mkdir(exist_ok = True)
    assert Path(d).exists()

    ncgen3_OUTPUT = d + TEST_NC_GRID_FILE
    #ncgen3_INPUT = TEST_DATA_IN_DIR + TEST_CDL_GRID_FILE
    ncgen3_INPUT = LOCAL_TEST_DIR + TEST_CDL_GRID_FILE
    if Path(ncgen3_OUTPUT).exists():
        assert True
    else:
        assert Path(LOCAL_TEST_DIR).exists()
        assert Path(ncgen3_INPUT).exists()
        ex = [ 'ncgen3', '-k', 'netCDF-4', '-o', ncgen3_OUTPUT , ncgen3_INPUT ]
        print (' '.join(ex))
        sp = subprocess.run( ex )

        assert all( [ sp.returncode == 0,
                      Path(ncgen3_OUTPUT).exists() ] )
        out, err = capfd.readouterr()


#@pytest.mark.skip(reason='debug')
def test_make_ncgen_tile_nc_inputs(capfd):
    '''
    set-up test: ncgen netcdf tile file inputs for later steps
    if the output exists, it will not bother remaking it
    '''
    ncgen_tile_i_nc_OUTPUT_exists = [ Path(d + f'{YYYYMMDD}.{SOURCE}.tile{i}.nc').exists() \
                                      for i in range(1, 6+1) ]
    if all( ncgen_tile_i_nc_OUTPUT_exists ):
        assert True
    else:
        for i in range(1, 6+1):
            ncgen_tile_i_nc_OUTPUT = d + f'{YYYYMMDD}.{SOURCE}.tile{i}.nc'
            #ncgen_tile_i_cdl_INPUT = TEST_DATA_IN_DIR + f'{YYYYMMDD}.{SOURCE}.tile{i}.cdl'
            ncgen_tile_i_cdl_INPUT = LOCAL_TEST_DIR + f'{YYYYMMDD}.{SOURCE}.tile{i}.cdl'
            assert Path(ncgen_tile_i_cdl_INPUT).exists()
            ex = [ 'ncgen', '-o', ncgen_tile_i_nc_OUTPUT, ncgen_tile_i_cdl_INPUT ]
            print (' '.join(ex))
            sp = subprocess.run( ex )

            assert all( [sp.returncode == 0,
                         Path(ncgen_tile_i_nc_OUTPUT).exists()] )
            out, err = capfd.readouterr()


#@pytest.mark.skip(reason='debug')
def test_make_ncgen_grid_spec_nc_inputs(capfd):
    '''
    set-up test: ncgen netcdf grid spec tile file inputs for later steps
    if the output exists, it will not bother remaking it
    '''
    ncgen_grid_spec_i_nc_OUTPUT_exists = [ Path(d + f'{YYYYMMDD}.grid_spec.tile{i}.nc').exists() \
                                           for i in range(1, 6+1) ]
    if all( ncgen_grid_spec_i_nc_OUTPUT_exists ):
        assert True
    else:
        for i in range(1, 6+1):
            ncgen_grid_spec_i_nc_OUTPUT = d + f'{YYYYMMDD}.grid_spec.tile{i}.nc'
            #ncgen_grid_spec_i_cdl_INPUT = TEST_DATA_IN_DIR + f'{YYYYMMDD}.grid_spec.tile{i}.cdl'
            ncgen_grid_spec_i_cdl_INPUT = LOCAL_TEST_DIR + f'{YYYYMMDD}.grid_spec.tile{i}.cdl'
            ex = [ 'ncgen', '-o', ncgen_grid_spec_i_nc_OUTPUT, ncgen_grid_spec_i_cdl_INPUT ]
            print (' '.join(ex))
            sp = subprocess.run( ex )

            assert all( [sp.returncode == 0,
                         Path(ncgen_grid_spec_i_nc_OUTPUT).exists()] )
            out, err = capfd.readouterr()


#@pytest.mark.skip(reason='debug')
def test_make_hgrid_gold_input(capfd):
    '''
    set-up test: make C96 gold input via make_hgrid for later steps
    if the output exists in the desired location, it will not bother remaking it
    '''
    grid_i_file_targ_LOC_exists = [ Path(d + f'C96_grid.tile{i}.nc').exists() \
                                    for i in range(1,6+1)                       ]
    if all( grid_i_file_targ_LOC_exists ):
        assert True
    else:
        # remake gold grid file locally, then move
        ex = [ "make_hgrid",
               "--grid_type", "gnomonic_ed",
               "--nlon", "192",
               "--grid_name", "C96_grid" ]
        print (' '.join(ex))
        sp = subprocess.run( ex )

        assert sp.returncode == 0
        out, err = capfd.readouterr()

        # now move the files...
        for i in range(1, 6+1):
            grid_i_file_curr_LOC = f'C96_grid.tile{i}.nc'
            grid_i_file_targ_LOC = d + f'C96_grid.tile{i}.nc'
            ex = [ 'mv', '-f', grid_i_file_curr_LOC, grid_i_file_targ_LOC ]
            print (' '.join(ex))
            sp = subprocess.run( ex )

            assert all( [sp.returncode == 0,
                         Path(grid_i_file_targ_LOC).exists()] )
            out, err = capfd.readouterr()


#@pytest.mark.skip(reason='debug')
def test_make_fregrid_comparison_input(capfd):
    '''
    set-up test: use fregrid to regrid for later comparison to regrid_xy output
    if the output exists in the desired location, it will not bother remaking it
    '''

    fregrid_input_mosaic_ARG = d + TEST_NC_GRID_FILE
    fregrid_input_dir_ARG = d
    fregrid_input_file_ARG = f'{YYYYMMDD}.{SOURCE}'
    fregrid_assoc_file_dir_ARG = d

    fregrid_remap_dir = LOCAL_REMAP_TEST_DIR
    Path(fregrid_remap_dir).mkdir(exist_ok = True)
    assert Path(fregrid_remap_dir).exists()

    fregridRemapFile = f'fregrid_remap_file_{NLON}_by_{NLAT}.nc'
    fregrid_remap_file_ARG = fregrid_remap_dir + fregridRemapFile

    fregrid_nlat_ARG = str(NLAT)
    fregrid_nlon_ARG = str(NLON)
    fregrid_vars_ARG = 'grid_xt,grid_yt,orog'

    fregrid_output_dir = LOCAL_TEST_DIR + LOCAL_ALL_TEST_OUT_DIR
    Path(fregrid_output_dir).mkdir(exist_ok = True)
    assert Path(fregrid_output_dir).exists()

    fregrid_output_file_ARG = fregrid_output_dir + fregrid_input_file_ARG + '.nc'

    ex = [ 'fregrid', '--standard_dimension',
           '--input_mosaic',          fregrid_input_mosaic_ARG,
           '--input_dir',                fregrid_input_dir_ARG,
           '--input_file',              fregrid_input_file_ARG,
           '--associated_file_dir', fregrid_assoc_file_dir_ARG,
           '--remap_file',              fregrid_remap_file_ARG,
           '--nlon',                          fregrid_nlon_ARG,
           '--nlat',                          fregrid_nlat_ARG,
           '--scalar_field',                  fregrid_vars_ARG,
           '--output_file',            fregrid_output_file_ARG  ]
    print (' '.join(ex))
    sp = subprocess.run( ex )

    assert all( [ sp.returncode == 0,
                  Path(fregrid_remap_file_ARG).exists(),
                  Path(fregrid_output_file_ARG).exists() ] )
    out, err = capfd.readouterr()


#@pytest.mark.skip(reason='debug')
def test_import_regrid_xy(capfd):
    '''
    check import of regrid_xy as a module
    '''

    import sys
    for path in sys.path: print(path);


    import fre.app.regrid_xy.regrid_xy as rgxy
    assert all( [ rgxy is not None,
                  rgxy.test_import() == 1 ] )
    out, err = capfd.readouterr()


#@pytest.mark.skip(reason='debug')
def test_success_regrid_xy(capfd):
    """
    checks for success of regrid_xy with rose app-app run
    """

    dr_file_output = LOCAL_TEST_OUT_DIR
    Path(dr_file_output).mkdir(exist_ok = True)
    assert Path(dr_file_output).exists()

    dr_remap_out = LOCAL_REMAP_DIR
    Path(dr_remap_out).mkdir(exist_ok = True)
    assert Path(dr_remap_out).exists()

    #created by regrid-xy
    work_dir = LOCAL_TEST_DIR + 'work/'

    # for the time being, still a little dependent on rose for configuration value passing
    if Path(os.getcwd()+'/rose-app-run.conf').exists():
        Path(os.getcwd()+'/rose-app-run.conf').unlink()
    rose_app_run_config=open(os.getcwd()+'/rose-app-run.conf','a')    
    rose_app_run_config.write(  '[command]\n'                    )
    rose_app_run_config.write(  'default=regrid-xy\n'            )
    rose_app_run_config.write(  '\n'                             )
    rose_app_run_config.write( f'[{COMPONENT}]\n'                )
    rose_app_run_config.write( f'sources={SOURCE}\n'             )
    rose_app_run_config.write( f'inputGrid={INPUT_GRID}\n'       )
    rose_app_run_config.write( f'inputRealm={INPUT_REALM}\n'     )
    rose_app_run_config.write( f'interpMethod={INTERP_METHOD}\n' )
    rose_app_run_config.write( f'outputGridLon={NLON}\n'         )
    rose_app_run_config.write( f'outputGridLat={NLAT}\n'         )
    rose_app_run_config.write(  '\n'                             )
    rose_app_run_config.close()

    import fre.app.regrid_xy.regrid_xy as rgxy
    rgxy_returncode = rgxy.regrid_xy(
        input_dir = d,
        output_dir = dr_file_output,
        begin = f'{YYYYMMDD}T000000',
        tmp_dir = LOCAL_TEST_DIR,
        remap_dir = dr_remap_out,
        source = SOURCE,
#        grid_spec = GOLD_GRID_SPEC,
        grid_spec = GOLD_GRID_SPEC_NO_TAR,
        def_xy_interp = f'"{NLON},{NLAT}"'
    )

    # uhm....
    #assert False
    assert all( [rgxy_returncode == 0,
                 Path( dr_remap_out + \
                 f'{INPUT_GRID}/{INPUT_REALM}/96-by-96/{INTERP_METHOD}/' + \
                       f'fregrid_remap_file_{NLON}_by_{NLAT}.nc' \
                      ).exists(),
                 Path( work_dir ).exists(),
                 Path( work_dir + f'{YYYYMMDD}.{SOURCE}.nc' ).exists(),
                 Path( work_dir + 'basin_codes.nc' ).exists(),
                 Path( work_dir + 'C96_grid.tile1.nc' ).exists(),
                 Path( work_dir + 'C96_grid.tile2.nc' ).exists(),
                 Path( work_dir + 'C96_grid.tile3.nc' ).exists(),
                 Path( work_dir + 'C96_grid.tile4.nc' ).exists(),
                 Path( work_dir + 'C96_grid.tile5.nc' ).exists(),
                 Path( work_dir + 'C96_grid.tile6.nc' ).exists(),
                 Path( work_dir + 'C96_mosaic.nc' ).exists(),
                 Path( work_dir + 'C96_mosaic_tile1XC96_mosaic_tile1.nc' ).exists(),
                 Path( work_dir + 'C96_mosaic_tile1Xocean_mosaic_tile1.nc' ).exists(),
                 Path( work_dir + 'C96_mosaic_tile2XC96_mosaic_tile2.nc' ).exists(),
                 Path( work_dir + 'C96_mosaic_tile2Xocean_mosaic_tile1.nc' ).exists(),
                 Path( work_dir + 'C96_mosaic_tile3XC96_mosaic_tile3.nc' ).exists(),
                 Path( work_dir + 'C96_mosaic_tile3Xocean_mosaic_tile1.nc' ).exists(),
                 Path( work_dir + 'C96_mosaic_tile4XC96_mosaic_tile4.nc' ).exists(),
                 Path( work_dir + 'C96_mosaic_tile4Xocean_mosaic_tile1.nc' ).exists(),
                 Path( work_dir + 'C96_mosaic_tile5XC96_mosaic_tile5.nc' ).exists(),
                 Path( work_dir + 'C96_mosaic_tile5Xocean_mosaic_tile1.nc' ).exists(),
                 Path( work_dir + 'C96_mosaic_tile6XC96_mosaic_tile6.nc' ).exists(),
                 Path( work_dir + 'C96_mosaic_tile6Xocean_mosaic_tile1.nc' ).exists(),
                 Path( work_dir + f'fregrid_remap_file_{NLON}_by_{NLAT}.nc' ).exists(),
                 Path( work_dir + 'hash.md5' ).exists(),
                 Path( work_dir + 'land_mask_tile1.nc' ).exists(),
                 Path( work_dir + 'land_mask_tile2.nc' ).exists(),
                 Path( work_dir + 'land_mask_tile3.nc' ).exists(),
                 Path( work_dir + 'land_mask_tile4.nc' ).exists(),
                 Path( work_dir + 'land_mask_tile5.nc' ).exists(),
                 Path( work_dir + 'land_mask_tile6.nc' ).exists(),
                 Path( work_dir + 'mosaic.nc' ).exists(),
                 Path( work_dir + 'ocean_hgrid.nc' ).exists(),
                 Path( work_dir + 'ocean_mask.nc' ).exists(),
                 Path( work_dir + 'ocean_mosaic.nc' ).exists(),
                 Path( work_dir + 'ocean_static.nc' ).exists(),
                 Path( work_dir + 'ocean_topog.nc' ).exists() ] )
    out, err = capfd.readouterr()

#@pytest.mark.skip(reason='need to remove rose but failure test not inital priority. currently, this trivially passes')
def test_failure_wrong_DT_regrid_xy(capfd):
    """
     checks for failure of regrid_xy with rose app-run when fed an
    invalid date for begin
    """

    dr_file_output = LOCAL_TEST_OUT_DIR
    Path(dr_file_output).mkdir(exist_ok = True)
    assert Path(dr_file_output).exists()

    dr_remap_out = LOCAL_REMAP_DIR
    Path(dr_remap_out).mkdir(exist_ok = True)
    assert Path(dr_remap_out).exists()


        # for the time being, still a little dependent on rose for configuration value passing
    if Path(os.getcwd()+'/rose-app-run.conf').exists():
        Path(os.getcwd()+'/rose-app-run.conf').unlink()
    rose_app_run_config=open(os.getcwd()+'/rose-app-run.conf','a')    
    rose_app_run_config.write(  '[command]\n'                    )
    rose_app_run_config.write(  'default=regrid-xy\n'            )
    rose_app_run_config.write(  '\n'                             )
    rose_app_run_config.write( f'[{COMPONENT}]\n'                )
    rose_app_run_config.write( f'sources={SOURCE}\n'             )
    rose_app_run_config.write( f'inputGrid={INPUT_GRID}\n'       )
    rose_app_run_config.write( f'inputRealm={INPUT_REALM}\n'     )
    rose_app_run_config.write( f'interpMethod={INTERP_METHOD}\n' )
    rose_app_run_config.write( f'outputGridLon={NLON}\n'         )
    rose_app_run_config.write( f'outputGridLat={NLAT}\n'         )
    rose_app_run_config.write(  '\n'                             )
    rose_app_run_config.close()

    import fre.app.regrid_xy.regrid_xy as rgxy
    try:
        rgxy_returncode = rgxy.regrid_xy(
            input_dir = d,
            output_dir = dr_file_output,
            begin = f'99999999T999999',
            tmp_dir = LOCAL_TEST_DIR,
            remap_dir = dr_remap_out,
            source = SOURCE,
            grid_spec = GOLD_GRID_SPEC,
            def_xy_interp = f'"{NLON},{NLAT}"'
        )
    except:
        # yay good job
        assert True

#    assert rgxy_returncode != 0
#    assert all( [ rgxy_returncode != 0,
#                  True or sp.returncode == 1 ] )
    out, err = capfd.readouterr()



#@pytest.mark.skip(reason='debug')
def test_nccmp1_regrid_xy(capfd):
    """
    This test compares the output of make_hgrid and fregrid, which are expected to be identical
    """
    remap_dir_out = LOCAL_REMAP_TEST_DIR
    dr_remap_out = LOCAL_REMAP_DIR
    sources_xy = '96-by-96'
    fregridRemapFile=f'fregrid_remap_file_{NLON}_by_{NLAT}.nc'

    nccmp_ARG1 = dr_remap_out + INPUT_GRID + '/' + INPUT_REALM + '/' + \
                 sources_xy + '/' + INTERP_METHOD  + '/' + fregridRemapFile
    nccmp_ARG2 = remap_dir_out + fregridRemapFile
    nccmp= [ 'nccmp', '-m', '--force', nccmp_ARG1, nccmp_ARG2 ]
    print (' '.join(nccmp))
    sp = subprocess.run(nccmp)
    assert sp.returncode == 0
    out, err = capfd.readouterr()


#@pytest.mark.skip(reason='debug')
def test_nccmp2_regrid_xy(capfd):
    """
    This test compares the regridded source file output(s), which are expected to be identical
    """
    dr_file_output = LOCAL_TEST_OUT_DIR
    file_output_dir = LOCAL_TEST_DIR + LOCAL_ALL_TEST_OUT_DIR
    outputFile = f'{YYYYMMDD}.{SOURCE}.nc'

    nccmp_ARG1 = dr_file_output  + outputFile
    nccmp_ARG2 = file_output_dir + outputFile
    nccmp= [ 'nccmp', '-m', '--force', nccmp_ARG1, nccmp_ARG2 ]
    print (' '.join(nccmp))
    sp = subprocess.run(nccmp)
    assert sp.returncode == 0
    out, err = capfd.readouterr()


@pytest.mark.skip(reason='TODO')
def test_regrid_one_for_two_comps(capfd):
    """
    this test will compare regridding settings for a single source file ref'd in two
    diff components and regrid that source file twice if the settings are different,
    and only once if the settings are the same.
    """
    assert False
