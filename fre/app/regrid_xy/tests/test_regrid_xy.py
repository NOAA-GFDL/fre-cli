from pathlib import Path
import pytest
import subprocess
import os
import shutil

# directories for tests
TEST_DIR = os.getcwd() + "/fre/app/regrid_xy/tests/test_inputs_outputs/"

TAR_IN_DIR = TEST_DIR + 'input_directory.tar.gz' #contains in-dir
IN_DIR = TEST_DIR + 'in-dir/'
WORK_DIR = TEST_DIR + f'work/'

TEST_OUT_DIR = TEST_DIR + 'out-dir/'
REMAP_DIR = TEST_DIR + 'remap-dir/'

ALL_TEST_OUT_DIR  = TEST_DIR + "out-test-dir/"
REMAP_TEST_DIR = TEST_DIR + 'remap-test-dir/'

# official data/mosaic stuff
GOLD_GRID_SPEC = "/archive/gold/datasets/OM4_05/mosaic_c96.v20180227.tar"
GOLD_GRID_SPEC_NO_TAR = IN_DIR + "mosaic.nc"
TEST_CDL_GRID_FILE = IN_DIR + "C96_mosaic.cdl"


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
SOURCES_XY = '96-by-96'

WORK_YYYYMMDD_DIR = WORK_DIR + f'{YYYYMMDD}.nc/'
TEST_NC_GRID_FILE = WORK_YYYYMMDD_DIR + "C96_mosaic.nc" # output of first ncgen test

def test_setup_clean_up(capfd):
    try:
        Path(IN_DIR).unlink()
    except:
        pass
    try:
        Path(TEST_NC_GRID_FILE).unlink()
    except:
        pass
    try:
        shutil.rmtree(WORK_DIR)
    except:
        pass
    try:
        shutil.rmtree(TEST_OUT_DIR)
    except:
        pass
    try:
        shutil.rmtree(ALL_TEST_OUT_DIR)
    except:
        pass
    try:
        shutil.rmtree(REMAP_DIR)
    except:
        pass
    try:
        shutil.rmtree(REMAP_TEST_DIR)
    except:
        pass
    assert True
    out, err = capfd.readouterr()
    

def test_setup_global_work_dirs(capfd):
    Path(WORK_YYYYMMDD_DIR).mkdir(parents = True, exist_ok = True)
    assert Path(WORK_YYYYMMDD_DIR).exists()

    Path(REMAP_TEST_DIR).mkdir(exist_ok = True)
    assert Path(REMAP_TEST_DIR).exists()

    Path(ALL_TEST_OUT_DIR).mkdir(exist_ok = True)
    assert Path(ALL_TEST_OUT_DIR).exists()

    Path(TEST_OUT_DIR).mkdir(exist_ok = True)
    assert Path(TEST_OUT_DIR).exists()

    Path(REMAP_DIR).mkdir(exist_ok = True)
    assert Path(REMAP_DIR).exists()
    out, err = capfd.readouterr()


def test_untar_inputs(capfd):
    ex = ["tar", "-C", TEST_DIR, "-zxvf", TAR_IN_DIR]
    sp = subprocess.run( ex )
    assert all ( [ sp.returncode == 0,
                   Path(IN_DIR).exists() ] )
    out, err = capfd.readouterr()


#@pytest.mark.skip(reason='debug')
def test_make_ncgen3_nc_inputs(capfd):
    '''
    set-up test: ncgen3 netcdf file inputs for later steps
    if the output exists, it will not bother remaking it
    '''

    ncgen3_OUTPUT = TEST_NC_GRID_FILE
    ncgen3_INPUT = TEST_CDL_GRID_FILE
    if Path(ncgen3_OUTPUT).exists():
        assert True
    else:
        assert Path(TEST_DIR).exists()
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
    ncgen_tile_i_nc_OUTPUT_exists = [ Path( WORK_YYYYMMDD_DIR + f'{YYYYMMDD}.{SOURCE}.tile{i}.nc').exists() \
                                      for i in range(1, 6+1) ]
    if all( ncgen_tile_i_nc_OUTPUT_exists ):
        assert True
    else:
        for i in range(1, 6+1):
            ncgen_tile_i_nc_OUTPUT = WORK_YYYYMMDD_DIR + f'{YYYYMMDD}.{SOURCE}.tile{i}.nc'
            ncgen_tile_i_cdl_INPUT = IN_DIR + f'{YYYYMMDD}.{SOURCE}.tile{i}.cdl'
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
    ncgen_grid_spec_i_nc_OUTPUT_exists = [ Path( WORK_YYYYMMDD_DIR + f'{YYYYMMDD}.grid_spec.tile{i}.nc').exists() \
                                           for i in range(1, 6+1) ]
    if all( ncgen_grid_spec_i_nc_OUTPUT_exists ):
        assert True
    else:
        for i in range(1, 6+1):
            ncgen_grid_spec_i_nc_OUTPUT = WORK_YYYYMMDD_DIR + f'{YYYYMMDD}.grid_spec.tile{i}.nc'
            ncgen_grid_spec_i_cdl_INPUT = IN_DIR + f'{YYYYMMDD}.grid_spec.tile{i}.cdl'
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
    grid_i_file_targ_LOC_exists = [ Path( WORK_YYYYMMDD_DIR + f'C96_grid.tile{i}.nc').exists() \
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
            grid_i_file_targ_LOC = WORK_YYYYMMDD_DIR + f'C96_grid.tile{i}.nc'
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

    fregrid_input_mosaic_ARG = TEST_NC_GRID_FILE
    fregrid_input_dir_ARG = WORK_YYYYMMDD_DIR
    fregrid_input_file_ARG = f'{YYYYMMDD}.{SOURCE}'
    fregrid_assoc_file_dir_ARG = WORK_YYYYMMDD_DIR

    fregridRemapFile = f'fregrid_remap_file_{NLON}_by_{NLAT}.nc'
    fregrid_remap_file_ARG = REMAP_TEST_DIR + fregridRemapFile

    fregrid_nlat_ARG = str(NLAT)
    fregrid_nlon_ARG = str(NLON)
    fregrid_vars_ARG = 'grid_xt,grid_yt,orog'


    fregrid_output_file_ARG = ALL_TEST_OUT_DIR + fregrid_input_file_ARG + '.nc'

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
    print (' \n'.join(ex))
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
def test_success_tar_grid_spec_regrid_xy(capfd):
    """
    checks for success of regrid_xy with rose app-app run
    """
    # this will only work at GFDL for now.
    if not Path(GOLD_GRID_SPEC).exists():
        assert True
    else:
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
            input_dir = WORK_YYYYMMDD_DIR,
            output_dir = TEST_OUT_DIR,
            begin = f'{YYYYMMDD}T000000',
            tmp_dir = TEST_DIR,
            remap_dir = REMAP_DIR,
            source = SOURCE,
            grid_spec = GOLD_GRID_SPEC,
            def_xy_interp = f'"{NLON},{NLAT}"'
        )
        
        # uhm....
        assert rgxy_returncode == 0
        assert Path( REMAP_DIR + \
                     f'{INPUT_GRID}/{INPUT_REALM}/96-by-96/{INTERP_METHOD}/' + \
                     f'fregrid_remap_file_{NLON}_by_{NLAT}.nc' \
        ).exists()
        assert Path( TEST_OUT_DIR ).exists()
        assert Path( TEST_OUT_DIR + f'{YYYYMMDD}.{SOURCE}.nc' ).exists()
        assert Path( WORK_DIR ).exists()
        assert Path( WORK_DIR + f'{YYYYMMDD}.{SOURCE}.nc' ).exists()
        assert Path( WORK_YYYYMMDD_DIR ).exists()
        assert Path( WORK_YYYYMMDD_DIR + 'basin_codes.nc' ).exists()
        assert Path( WORK_YYYYMMDD_DIR + 'C96_grid.tile1.nc' ).exists()
        assert Path( WORK_YYYYMMDD_DIR + 'C96_grid.tile2.nc' ).exists()
        assert Path( WORK_YYYYMMDD_DIR + 'C96_grid.tile3.nc' ).exists()
        assert Path( WORK_YYYYMMDD_DIR + 'C96_grid.tile4.nc' ).exists()
        assert Path( WORK_YYYYMMDD_DIR + 'C96_grid.tile5.nc' ).exists()
        assert Path( WORK_YYYYMMDD_DIR + 'C96_grid.tile6.nc' ).exists()
        assert Path( WORK_YYYYMMDD_DIR + 'C96_mosaic.nc' ).exists()
        assert Path( WORK_YYYYMMDD_DIR + 'C96_mosaic_tile1XC96_mosaic_tile1.nc' ).exists()
        assert Path( WORK_YYYYMMDD_DIR + 'C96_mosaic_tile1Xocean_mosaic_tile1.nc' ).exists()
        assert Path( WORK_YYYYMMDD_DIR + 'C96_mosaic_tile2XC96_mosaic_tile2.nc' ).exists()
        assert Path( WORK_YYYYMMDD_DIR + 'C96_mosaic_tile2Xocean_mosaic_tile1.nc' ).exists()
        assert Path( WORK_YYYYMMDD_DIR + 'C96_mosaic_tile3XC96_mosaic_tile3.nc' ).exists()
        assert Path( WORK_YYYYMMDD_DIR + 'C96_mosaic_tile3Xocean_mosaic_tile1.nc' ).exists()
        assert Path( WORK_YYYYMMDD_DIR + 'C96_mosaic_tile4XC96_mosaic_tile4.nc' ).exists()
        assert Path( WORK_YYYYMMDD_DIR + 'C96_mosaic_tile4Xocean_mosaic_tile1.nc' ).exists()
        assert Path( WORK_YYYYMMDD_DIR + 'C96_mosaic_tile5XC96_mosaic_tile5.nc' ).exists()
        assert Path( WORK_YYYYMMDD_DIR + 'C96_mosaic_tile5Xocean_mosaic_tile1.nc' ).exists()
        assert Path( WORK_YYYYMMDD_DIR + 'C96_mosaic_tile6XC96_mosaic_tile6.nc' ).exists()
        assert Path( WORK_YYYYMMDD_DIR + 'C96_mosaic_tile6Xocean_mosaic_tile1.nc' ).exists()
        assert Path( WORK_YYYYMMDD_DIR + 'hash.md5' ).exists()
        assert Path( WORK_YYYYMMDD_DIR + 'land_mask_tile1.nc' ).exists()
        assert Path( WORK_YYYYMMDD_DIR + 'land_mask_tile2.nc' ).exists()
        assert Path( WORK_YYYYMMDD_DIR + 'land_mask_tile3.nc' ).exists()
        assert Path( WORK_YYYYMMDD_DIR + 'land_mask_tile4.nc' ).exists()
        assert Path( WORK_YYYYMMDD_DIR + 'land_mask_tile5.nc' ).exists()
        assert Path( WORK_YYYYMMDD_DIR + 'land_mask_tile6.nc' ).exists()
        assert Path( WORK_YYYYMMDD_DIR + 'mosaic.nc' ).exists()
        assert Path( WORK_YYYYMMDD_DIR + 'ocean_hgrid.nc' ).exists()
        assert Path( WORK_YYYYMMDD_DIR + 'ocean_mask.nc' ).exists()
        assert Path( WORK_YYYYMMDD_DIR + 'ocean_mosaic.nc' ).exists()
        assert Path( WORK_YYYYMMDD_DIR + 'ocean_static.nc' ).exists()
        assert Path( WORK_YYYYMMDD_DIR + 'ocean_topog.nc' ).exists() 
        out, err = capfd.readouterr()
    assert True




#@pytest.mark.skip(reason='debug')
def test_success_no_tar_grid_spec_regrid_xy(capfd):
    """
    checks for success of regrid_xy with rose app-app run
    """
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
        input_dir = WORK_YYYYMMDD_DIR,
        output_dir = TEST_OUT_DIR,
        begin = f'{YYYYMMDD}T000000',
        tmp_dir = TEST_DIR,
        remap_dir = REMAP_DIR,
        source = SOURCE,
        grid_spec = GOLD_GRID_SPEC_NO_TAR,
        def_xy_interp = f'"{NLON},{NLAT}"'
    )
    
    # uhm....
    assert rgxy_returncode == 0
    assert Path( REMAP_DIR + \
                 f'{INPUT_GRID}/{INPUT_REALM}/96-by-96/{INTERP_METHOD}/' + \
                 f'fregrid_remap_file_{NLON}_by_{NLAT}.nc' \
    ).exists()
    assert Path( TEST_OUT_DIR ).exists()
    assert Path( TEST_OUT_DIR + f'{YYYYMMDD}.{SOURCE}.nc' ).exists()
    assert Path( WORK_DIR ).exists()
    assert Path( WORK_DIR + f'{YYYYMMDD}.{SOURCE}.nc' ).exists()
    assert Path( WORK_YYYYMMDD_DIR ).exists()

    assert Path( WORK_YYYYMMDD_DIR + 'C96_grid.tile1.nc' ).exists()
    assert Path( WORK_YYYYMMDD_DIR + 'C96_grid.tile2.nc' ).exists()
    assert Path( WORK_YYYYMMDD_DIR + 'C96_grid.tile3.nc' ).exists()
    assert Path( WORK_YYYYMMDD_DIR + 'C96_grid.tile4.nc' ).exists()
    assert Path( WORK_YYYYMMDD_DIR + 'C96_grid.tile5.nc' ).exists()
    assert Path( WORK_YYYYMMDD_DIR + 'C96_grid.tile6.nc' ).exists()
    assert Path( WORK_YYYYMMDD_DIR + 'C96_mosaic.nc' ).exists()
    assert Path( WORK_YYYYMMDD_DIR + 'mosaic.nc' ).exists()
    out, err = capfd.readouterr()



    
@pytest.mark.skip(reason='debug')
def test_failure_wrong_DT_regrid_xy(capfd):
    """
     checks for failure of regrid_xy with rose app-run when fed an
    invalid date for begin
    """


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
            input_dir = WORK_YYYYMMDD_DIR,
            output_dir = TEST_OUT_DIR,
            begin = f'99999999T999999',
            tmp_dir = TEST_DIR,
            remap_dir = REMAP_DIR,
            source = SOURCE,
            grid_spec = GOLD_GRID_SPEC,
            def_xy_interp = f'"{NLON},{NLAT}"'
        )
    except:
        # yay good job
        assert True

    out, err = capfd.readouterr()



#@pytest.mark.skip(reason='debug')


def test_nccmp1_regrid_xy(capfd):
    """
    This test compares the output of make_hgrid and fregrid, which are expected to be identical
    """
    fregridRemapFile=f'fregrid_remap_file_{NLON}_by_{NLAT}.nc'

    nccmp_ARG1 = REMAP_DIR + INPUT_GRID + '/' + INPUT_REALM + '/' + \
                 SOURCES_XY + '/' + INTERP_METHOD  + '/' + fregridRemapFile
    nccmp_ARG2 = REMAP_TEST_DIR + fregridRemapFile
    nccmp= [ 'nccmp', '-m', '--force', nccmp_ARG1, nccmp_ARG2 ]
    print (' '.join(nccmp))
    sp = subprocess.run(nccmp)
    assert sp.returncode == 0
    out, err = capfd.readouterr()


def test_nccmp2_regrid_xy(capfd):
    """
    This test compares the regridded source file output(s), which are expected to be identical
    """
    nccmp_ARG1 = TEST_OUT_DIR  + f'{YYYYMMDD}.{SOURCE}.nc'
    nccmp_ARG2 = ALL_TEST_OUT_DIR + f'{YYYYMMDD}.{SOURCE}.nc'
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
