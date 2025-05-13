""" test regrid_xy functioning as an importable python module """
from pathlib import Path
import subprocess
import os
import shutil

import pytest

import fre.app.regrid_xy.regrid_xy as rgxy

# directories for tests
CWD = os.getcwd() # this should be the base repo directory (aka proj directory)
TEST_DIR = os.getcwd() + "/fre/app/regrid_xy/tests/test_inputs_outputs/"

TAR_IN_DIR = TEST_DIR + 'input_directory.tar.gz' #contains in-dir
IN_DIR = TEST_DIR + 'in-dir/'
WORK_DIR = TEST_DIR + 'work/'

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

def test_setup_clean_up():
    """ cleanup i/o directories is present for clean regrid_xy testing """
    if Path(IN_DIR).exists():
        shutil.rmtree(IN_DIR)
    if Path(TEST_NC_GRID_FILE).exists():
        Path(TEST_NC_GRID_FILE).unlink()
    if Path(WORK_DIR).exists():
        shutil.rmtree(WORK_DIR)
    if Path(TEST_OUT_DIR).exists():
        shutil.rmtree(TEST_OUT_DIR)
    if Path(ALL_TEST_OUT_DIR).exists():
        shutil.rmtree(ALL_TEST_OUT_DIR)
    if Path(REMAP_DIR).exists():
        shutil.rmtree(REMAP_DIR)
    if Path(REMAP_TEST_DIR).exists():
        shutil.rmtree(REMAP_TEST_DIR)
    assert os.getcwd() == CWD


def test_setup_global_work_dirs():
    """ create i/o directories for regrid_xy testing """
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
    assert os.getcwd() == CWD


def test_untar_inputs():
    """ untar input directory tarball to create test inputs """
    ex = ["tar", "-C", TEST_DIR, "-zxvf", TAR_IN_DIR]
    sp = subprocess.run( ex , check = True )
    assert all ( [ sp.returncode == 0,
                   Path(IN_DIR).exists() ] )
    assert os.getcwd() == CWD


#@pytest.mark.skip(reason='debug')
def test_make_ncgen3_nc_inputs():
    """
    set-up test: ncgen3 netcdf file inputs for later steps
    if the output exists, it will not bother remaking it
    """

    ncgen3_output = TEST_NC_GRID_FILE
    ncgen3_input = TEST_CDL_GRID_FILE
    if Path(ncgen3_output).exists():
        Path(ncgen3_output).unlink()
    
    assert Path(TEST_DIR).exists()
    assert Path(ncgen3_input).exists()
    ex = [ 'ncgen3', '-k', 'netCDF-4', '-o', ncgen3_output , ncgen3_input ]
    print (' '.join(ex))
    sp = subprocess.run( ex , check = True )
    
    assert all( [ sp.returncode == 0,
                  Path(ncgen3_output).exists() ] )
    assert os.getcwd() == CWD


#@pytest.mark.skip(reason='debug')
def test_make_ncgen_tile_nc_inputs():
    """
    set-up test: ncgen netcdf tile file inputs for later steps
    if the output exists, it will not bother remaking it
    """
    ncgen_tile_i_nc_output_exists = [ Path( WORK_YYYYMMDD_DIR + \
                                            f'{YYYYMMDD}.{SOURCE}.tile{i}.nc' ).exists() \
                                      for i in range(1, 6+1) ]
    if all( ncgen_tile_i_nc_output_exists ):
        assert True
    else:
        for i in range(1, 6+1):
            ncgen_tile_i_nc_output = WORK_YYYYMMDD_DIR + f'{YYYYMMDD}.{SOURCE}.tile{i}.nc'
            ncgen_tile_i_cdl_input = IN_DIR + f'{YYYYMMDD}.{SOURCE}.tile{i}.cdl'
            assert Path(ncgen_tile_i_cdl_input).exists()
            ex = [ 'ncgen', '-o', ncgen_tile_i_nc_output, ncgen_tile_i_cdl_input ]
            print (' '.join(ex))
            sp = subprocess.run( ex , check = True )

            assert all( [sp.returncode == 0,
                         Path(ncgen_tile_i_nc_output).exists()] )
    assert os.getcwd() == CWD


#@pytest.mark.skip(reason='debug')
def test_make_ncgen_grid_spec_nc_inputs():
    """
    set-up test: ncgen netcdf grid spec tile file inputs for later steps
    if the output exists, it will not bother remaking it
    """
    ncgen_grid_spec_i_nc_output_exists = [ Path( WORK_YYYYMMDD_DIR + \
                                                 f'{YYYYMMDD}.grid_spec.tile{i}.nc').exists() \
                                           for i in range(1, 6+1) ]
    if all( ncgen_grid_spec_i_nc_output_exists ):
        assert True
    else:
        for i in range(1, 6+1):
            ncgen_grid_spec_i_nc_output = WORK_YYYYMMDD_DIR + f'{YYYYMMDD}.grid_spec.tile{i}.nc'
            ncgen_grid_spec_i_cdl_input = IN_DIR + f'{YYYYMMDD}.grid_spec.tile{i}.cdl'
            ex = [ 'ncgen', '-o', ncgen_grid_spec_i_nc_output, ncgen_grid_spec_i_cdl_input ]
            print (' '.join(ex))
            sp = subprocess.run( ex , check = True )

            assert all( [sp.returncode == 0,
                         Path(ncgen_grid_spec_i_nc_output).exists()] )
    assert os.getcwd() == CWD


#@pytest.mark.skip(reason='debug')
def test_make_hgrid_gold_input():
    """
    set-up test: make C96 gold input via make_hgrid for later steps
    if the output exists in the desired location, it will not bother remaking it
    """
    grid_i_file_targ_loc_exists = [ Path( WORK_YYYYMMDD_DIR + f'C96_grid.tile{i}.nc').exists() \
                                    for i in range(1,6+1)                       ]
    if all( grid_i_file_targ_loc_exists ):
        assert True
    else:
        # remake gold grid file locally, then move
        ex = [ "make_hgrid",
               "--grid_type", "gnomonic_ed",
               "--nlon", "192",
               "--grid_name", "C96_grid" ]
        print (' '.join(ex))
        sp = subprocess.run( ex , check = True )

        assert sp.returncode == 0

        # now move the files...
        for i in range(1, 6+1):
            grid_i_file_curr_loc = f'C96_grid.tile{i}.nc'
            grid_i_file_targ_loc = WORK_YYYYMMDD_DIR + f'C96_grid.tile{i}.nc'
            ex = [ 'mv', '-f', grid_i_file_curr_loc, grid_i_file_targ_loc ]
            print (' '.join(ex))
            sp = subprocess.run( ex , check = True )

            assert all( [sp.returncode == 0,
                         Path(grid_i_file_targ_loc).exists()] )
    assert os.getcwd() == CWD


#@pytest.mark.skip(reason='debug')
def test_make_fregrid_comparison_input():
    """
    set-up test: use fregrid to regrid for later comparison to regrid_xy output
    if the output exists in the desired location, it will not bother remaking it
    """

    fregrid_input_mosaic_arg = TEST_NC_GRID_FILE
    fregrid_input_dir_arg = WORK_YYYYMMDD_DIR
    fregrid_input_file_arg = f'{YYYYMMDD}.{SOURCE}'
    fregrid_assoc_file_dir_arg = WORK_YYYYMMDD_DIR

    fregrid_remap_file = f'fregrid_remap_file_{NLON}_by_{NLAT}.nc'
    fregrid_remap_file_arg = REMAP_TEST_DIR + fregrid_remap_file

    fregrid_nlat_arg = str(NLAT)
    fregrid_nlon_arg = str(NLON)
    fregrid_vars_arg = 'grid_xt,grid_yt,orog'


    fregrid_output_file_arg = ALL_TEST_OUT_DIR + fregrid_input_file_arg + '.nc'

    ex = [ 'fregrid', '--standard_dimension',
           '--input_mosaic',          fregrid_input_mosaic_arg,
           '--input_dir',                fregrid_input_dir_arg,
           '--input_file',              fregrid_input_file_arg,
           '--associated_file_dir', fregrid_assoc_file_dir_arg,
           '--remap_file',              fregrid_remap_file_arg,
           '--nlon',                          fregrid_nlon_arg,
           '--nlat',                          fregrid_nlat_arg,
           '--scalar_field',                  fregrid_vars_arg,
           '--output_file',            fregrid_output_file_arg  ]
    print (' \n'.join(ex))
    sp = subprocess.run( ex , check = True )

    assert all( [ sp.returncode == 0,
                  Path(fregrid_remap_file_arg).exists(),
                  Path(fregrid_output_file_arg).exists() ] )
    assert os.getcwd() == CWD

#@pytest.mark.skip(reason='debug')
def test_import_regrid_xy():
    """
    check import of regrid_xy as a module
    """
    assert all( [ rgxy is not None,
                  rgxy.test_import() == 1 ] )
    assert os.getcwd() == CWD


@pytest.mark.skip(reason='sometimes i cover up mistakes of the next test. if mysterious failures, skip me to debug!')
def test_success_tar_grid_spec_regrid_xy():
    """
    checks for success of regrid_xy with rose app-app run
    """
    # this will only work at GFDL for now.
    if not Path(GOLD_GRID_SPEC).exists():
        pytest.xfail('I require /archive at GFDL to succeed because i required a GOLD_GRID_SPEC located there')
    else:
        # for the time being, still a little dependent on rose for configuration value passing
        if Path(os.getcwd()+'/rose-app-run.conf').exists():
            Path(os.getcwd()+'/rose-app-run.conf').unlink()

        with open(os.getcwd()+'/rose-app-run.conf','a',encoding='utf-8') as rose_app_run_config:
            rose_app_run_config.write(  '[command]\n'                    )
            rose_app_run_config.write(  'default=regrid-xy\n'            )
            rose_app_run_config.write(  '\n'                             )
            rose_app_run_config.write( f'[{COMPONENT}]\n'                )
            rose_app_run_config.write( f"sources=['{SOURCE}']\n"         )
            rose_app_run_config.write( f'inputGrid={INPUT_GRID}\n'       )
            rose_app_run_config.write( f'inputRealm={INPUT_REALM}\n'     )
            rose_app_run_config.write( f'interpMethod={INTERP_METHOD}\n' )
            rose_app_run_config.write( f'outputGridLon={NLON}\n'         )
            rose_app_run_config.write( f'outputGridLat={NLAT}\n'         )
            rose_app_run_config.write(  '\n'                             )
        assert Path('./rose-app-run.conf').exists()

        rgxy_returncode = rgxy.regrid_xy(
            input_dir = WORK_YYYYMMDD_DIR,
            output_dir = TEST_OUT_DIR,
            begin = f'{YYYYMMDD}T000000',
            tmp_dir = TEST_DIR,
            remap_dir = REMAP_DIR,
            source = SOURCE,
            grid_spec = GOLD_GRID_SPEC,
            rose_config = 'rose-app-run.conf'
        )

        # uhm....
        assert rgxy_returncode == 0
        assert Path( REMAP_DIR + \
                     f'{INPUT_GRID}/{INPUT_REALM}/96-by-96/{INTERP_METHOD}/' + \
                     f'fregrid_remap_file_{NLON}_by_{NLAT}.nc' ).exists()
        assert Path( TEST_OUT_DIR ).exists()
        assert Path( TEST_OUT_DIR + f'{YYYYMMDD}.{SOURCE}.nc'  ).exists()
        assert Path( WORK_DIR ).exists()
        assert Path( WORK_DIR + f'{YYYYMMDD}.{SOURCE}.nc' ).exists()
        assert Path( WORK_DIR + 'basin_codes.nc' ).exists()
        assert Path( WORK_DIR + 'C96_grid.tile1.nc' ).exists()
        assert Path( WORK_DIR + 'C96_grid.tile2.nc' ).exists()
        assert Path( WORK_DIR + 'C96_grid.tile3.nc' ).exists()
        assert Path( WORK_DIR + 'C96_grid.tile4.nc' ).exists()
        assert Path( WORK_DIR + 'C96_grid.tile5.nc' ).exists()
        assert Path( WORK_DIR + 'C96_grid.tile6.nc' ).exists()
        assert Path( WORK_DIR + 'C96_mosaic.nc' ).exists()
        assert Path( WORK_DIR + 'C96_mosaic_tile1XC96_mosaic_tile1.nc' ).exists()
        assert Path( WORK_DIR + 'C96_mosaic_tile1Xocean_mosaic_tile1.nc' ).exists()
        assert Path( WORK_DIR + 'C96_mosaic_tile2XC96_mosaic_tile2.nc' ).exists()
        assert Path( WORK_DIR + 'C96_mosaic_tile2Xocean_mosaic_tile1.nc' ).exists()
        assert Path( WORK_DIR + 'C96_mosaic_tile3XC96_mosaic_tile3.nc' ).exists()
        assert Path( WORK_DIR + 'C96_mosaic_tile3Xocean_mosaic_tile1.nc' ).exists()
        assert Path( WORK_DIR + 'C96_mosaic_tile4XC96_mosaic_tile4.nc' ).exists()
        assert Path( WORK_DIR + 'C96_mosaic_tile4Xocean_mosaic_tile1.nc' ).exists()
        assert Path( WORK_DIR + 'C96_mosaic_tile5XC96_mosaic_tile5.nc' ).exists()
        assert Path( WORK_DIR + 'C96_mosaic_tile5Xocean_mosaic_tile1.nc' ).exists()
        assert Path( WORK_DIR + 'C96_mosaic_tile6XC96_mosaic_tile6.nc' ).exists()
        assert Path( WORK_DIR + 'C96_mosaic_tile6Xocean_mosaic_tile1.nc' ).exists()
        assert Path( WORK_DIR + 'hash.md5' ).exists()
        assert Path( WORK_DIR + 'land_mask_tile1.nc' ).exists()
        assert Path( WORK_DIR + 'land_mask_tile2.nc' ).exists()
        assert Path( WORK_DIR + 'land_mask_tile3.nc' ).exists()
        assert Path( WORK_DIR + 'land_mask_tile4.nc' ).exists()
        assert Path( WORK_DIR + 'land_mask_tile5.nc' ).exists()
        assert Path( WORK_DIR + 'land_mask_tile6.nc' ).exists()
        assert Path( WORK_DIR + 'mosaic.nc' ).exists()
        assert Path( WORK_DIR + 'ocean_hgrid.nc' ).exists()
        assert Path( WORK_DIR + 'ocean_mask.nc' ).exists()
        assert Path( WORK_DIR + 'ocean_mosaic.nc' ).exists()
        assert Path( WORK_DIR + 'ocean_static.nc' ).exists()
        assert Path( WORK_DIR + 'ocean_topog.nc' ).exists()

    assert os.getcwd() == CWD



#@pytest.mark.skip(reason='debug')
def test_success_no_tar_grid_spec_regrid_xy():
    """
    checks for success of regrid_xy with rose app-app run
    """
    # for the time being, still a little dependent on rose for configuration value passing
    if Path(os.getcwd()+'/rose-app-run.conf').exists():
        Path(os.getcwd()+'/rose-app-run.conf').unlink()

    with open(os.getcwd()+'/rose-app-run.conf','a',encoding='utf-8') as rose_app_run_config:
        rose_app_run_config.write(  '[command]\n'                    )
        rose_app_run_config.write(  'default=regrid-xy\n'            )
        rose_app_run_config.write(  '\n'                             )
        rose_app_run_config.write( f'[{COMPONENT}]\n'                )
        rose_app_run_config.write( f"sources=['{SOURCE}']\n"             )
        rose_app_run_config.write( f'inputGrid={INPUT_GRID}\n'       )
        rose_app_run_config.write( f'inputRealm={INPUT_REALM}\n'     )
        rose_app_run_config.write( f'interpMethod={INTERP_METHOD}\n' )
        rose_app_run_config.write( f'outputGridLon={NLON}\n'         )
        rose_app_run_config.write( f'outputGridLat={NLAT}\n'         )
        rose_app_run_config.write(  '\n'                             )
    assert Path('./rose-app-run.conf').exists()

    rgxy_returncode = rgxy.regrid_xy(
        input_dir = WORK_YYYYMMDD_DIR,
        output_dir = TEST_OUT_DIR,
        begin = f'{YYYYMMDD}T000000',
        tmp_dir = TEST_DIR,
        remap_dir = REMAP_DIR,
        source = SOURCE,
        grid_spec = GOLD_GRID_SPEC_NO_TAR,
        rose_config = "rose-app-run.conf"
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

    assert Path( WORK_DIR + 'C96_grid.tile1.nc' ).exists()
    assert Path( WORK_DIR + 'C96_grid.tile2.nc' ).exists()
    assert Path( WORK_DIR + 'C96_grid.tile3.nc' ).exists()
    assert Path( WORK_DIR + 'C96_grid.tile4.nc' ).exists()
    assert Path( WORK_DIR + 'C96_grid.tile5.nc' ).exists()
    assert Path( WORK_DIR + 'C96_grid.tile6.nc' ).exists()
    assert Path( WORK_DIR + 'C96_mosaic.nc' ).exists()
    assert Path( WORK_DIR + 'mosaic.nc' ).exists()
    assert os.getcwd() == CWD



@pytest.mark.skip(reason='debug')
def test_failure_wrong_datetime_regrid_xy():
    """
     checks for failure of regrid_xy with rose app-run when fed an
    invalid date for begin
    """
    # for the time being, still a little dependent on rose for configuration value passing
    if Path(os.getcwd()+'/rose-app-run.conf').exists():
        Path(os.getcwd()+'/rose-app-run.conf').unlink()

    with open(os.getcwd()+'/rose-app-run.conf','a',encoding='utf-8') as rose_app_run_config:
        rose_app_run_config.write(  '[command]\n'                    )
        rose_app_run_config.write(  'default=regrid-xy\n'            )
        rose_app_run_config.write(  '\n'                             )
        rose_app_run_config.write( f'[{COMPONENT}]\n'                )
        rose_app_run_config.write( f"sources=['{SOURCE}']\n"             )
        rose_app_run_config.write( f'inputGrid={INPUT_GRID}\n'       )
        rose_app_run_config.write( f'inputRealm={INPUT_REALM}\n'     )
        rose_app_run_config.write( f'interpMethod={INTERP_METHOD}\n' )
        rose_app_run_config.write( f'outputGridLon={NLON}\n'         )
        rose_app_run_config.write( f'outputGridLat={NLAT}\n'         )
        rose_app_run_config.write(  '\n'                             )
    assert Path('./rose-app-run.conf').exists()

    try:
        rgxy_returncode = rgxy.regrid_xy(
            input_dir = WORK_YYYYMMDD_DIR,
            output_dir = TEST_OUT_DIR,
            begin = '99999999T999999',
            tmp_dir = TEST_DIR,
            remap_dir = REMAP_DIR,
            source = SOURCE,
            grid_spec = GOLD_GRID_SPEC,
            rose_config = 'rose-app-run.conf'
        )
    except:
        # yay good job
        assert True
    assert os.getcwd() == CWD



#@pytest.mark.skip(reason='debug')
def test_nccmp1_regrid_xy():
    """
    This test compares the output of make_hgrid and fregrid, which are expected to be identical
    """
    fregrid_remap_file=f'fregrid_remap_file_{NLON}_by_{NLAT}.nc'

    nccmp_arg1 = REMAP_DIR + INPUT_GRID + '/' + INPUT_REALM + '/' + \
                 SOURCES_XY + '/' + INTERP_METHOD  + '/' + fregrid_remap_file
    nccmp_arg2 = REMAP_TEST_DIR + fregrid_remap_file
    nccmp= [ 'nccmp', '-m', '--force', nccmp_arg1, nccmp_arg2 ]
    print (' '.join(nccmp))
    sp = subprocess.run( nccmp, check = True)
    assert sp.returncode == 0
    assert os.getcwd() == CWD

def test_nccmp2_regrid_xy():
    """
    This test compares the regridded source file output(s), which are expected to be identical
    """
    nccmp_arg1 = TEST_OUT_DIR  + f'{YYYYMMDD}.{SOURCE}.nc'
    nccmp_arg2 = ALL_TEST_OUT_DIR + f'{YYYYMMDD}.{SOURCE}.nc'
    nccmp= [ 'nccmp', '-m', '--force', nccmp_arg1, nccmp_arg2 ]
    print (' '.join(nccmp))
    sp = subprocess.run( nccmp, check = True)
    assert sp.returncode == 0
    assert os.getcwd() == CWD

@pytest.mark.skip(reason='TODO')
def test_regrid_one_for_two_comps():
    """
    this test will compare regridding settings for a single source file ref'd in two
    diff components and regrid that source file twice if the settings are different,
    and only once if the settings are the same.
    """
    assert False
    assert os.getcwd() == CWD
