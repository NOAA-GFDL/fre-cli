import os
import subprocess
import shutil
from pathlib import Path
import pytest
import fre.app.remap_pp_components.remap_pp_components as rmp

# Test paths
CWD = os.getcwd()
TEST_DIR = Path(f"{CWD}/fre/app/remap_pp_components/tests")
DATA_DIR = Path(f"{CWD}/fre/app/remap_pp_components/tests/test-data")

# YAML configuration example file
YAML_EX = f"{DATA_DIR}/yaml_ex.yaml"

# Define/create necessary output/input locations
TEST_OUTDIR = f"{TEST_DIR}/test-outDir"
REMAP_IN = f"{TEST_OUTDIR}/ncgen-output"
REMAP_OUT = f"{TEST_OUTDIR}/remap-output"

# Define components, grids, other
COMPOUT_LIST = ["atmos_scalar", "atmos_scalar_test_vars", "atmos_scalar_test_vars_fail", "atmos_scalar_static_test_vars_fail"]
NATIVE_GRID = "native"
REGRID_GRID = "regrid-xy"
COPY_TOOL = "cp"

# Define non-static variables
DATA_FILE_CDL = Path("atmos_scalar.198001-198412.co2mass.cdl") # CDL file to generate nc file from ncgen
# netcdf files to make
DATA_NC_FILES = ["atmos_scalar.198001-198412.co2mass.nc",
                 "atmos_scalar_test_vars.198001-198412.co2mass.nc",
                 "atmos_scalar_test_vars_fail.198001-198412.co2mass.nc",
                 "atmos_scalar_test_vars_fail.198001-198412.co2mass.nc"]
PRODUCT = "ts"
FREQ = "P1M"
CHUNK = "P5Y"

# Define static variables
STATIC_DATA_FILE_CDL = Path("atmos_static_scalar.bk.cdl")      # CDL file to generate static nc file from ncgen
# static netcdf files to make
STATIC_DATA_NC_FILES = ["atmos_static_scalar.bk.nc",
                        "atmos_static_scalar_test_vars.bk.nc",
                        "atmos_static_scalar_test_vars_fail.bk.nc"]
STATIC_PRODUCT = "static"
STATIC_FREQ = "P0Y"
STATIC_CHUNK = "P0Y"
STATIC_SRC_LIST = ["atmos_static_scalar", "atmos_static_scalar_test_vars", "atmos_static_scalar_test_vars_fail"]

#If output directory exists, remove and create again
if Path(TEST_OUTDIR).exists():
    shutil.rmtree(TEST_OUTDIR)

ncgen_native_out_paths = []
ncgen_static_out_paths = []
# Set up input directories (location previously made in flow.cylc workflow)
for i in COMPOUT_LIST:
    ncgen_native_out = f"{REMAP_IN}/{NATIVE_GRID}/{i}/{FREQ}/{CHUNK}"
    Path(ncgen_native_out).mkdir(parents=True,exist_ok=True)
    ncgen_native_out_paths.append(ncgen_native_out)
for j in STATIC_SRC_LIST:
    ncgen_static_out = f"{REMAP_IN}/{NATIVE_GRID}/{j}/{STATIC_FREQ}/{STATIC_CHUNK}"
    Path(ncgen_static_out).mkdir(parents=True,exist_ok=True)
    ncgen_static_out_paths.append(ncgen_static_out)

# Create output directory
Path(REMAP_OUT).mkdir(parents=True,exist_ok=True)

#################################################
## FILE EXISTENCE TESTS ##
def test_cdl_file_exists(capfd):
    """
    Test for the existence of cdl test files
    """
    assert all([Path(f"{DATA_DIR}/{DATA_FILE_CDL}").exists(),
                Path(f"{DATA_DIR}/{STATIC_DATA_FILE_CDL}")])

def test_yaml_ex_exists(capfd):
    """
    Test for the existence of example yaml configuration
    """
    assert Path(YAML_EX).exists()

## CREATE TEST FILES ##
def test_create_ncfile_with_ncgen_cdl(capfd):
    """
    Check for the creation of required directories
    and a \*.nc file from \*.cdl text file using
    command ncgen. These files will be used as an input
    files for the rewrite remap tests.
    Test checks for success of ncgen command for each
    created file.
    """
    # Loop through native paths created, create associated netcdf file
    # if name is in path name
    for out_path in ncgen_native_out_paths:
        for nc_fn in DATA_NC_FILES:
            if nc_fn.split(".")[0] != out_path.split("/")[-3]:
#                print(f'\n{nc_fn.split(".")[0]} not in {out_path.split("/")[-3]}')
                continue

            # NCGEN command: ncgen -o [outputfile] [inputfile]
            ex = [ "ncgen", "-k", "64-bit offset",
                   "-o", Path(out_path) / nc_fn,
                   DATA_DIR / DATA_FILE_CDL ]

            # Run ncgen command
            sp = subprocess.run( ex, check = False )

            # Check for
            # 1. ncgen command success
            # 2. nc file creation
            assert all([sp.returncode == 0,
                       Path(f"{out_path}/{nc_fn}").exists()])
            out, err = capfd.readouterr()

def test_create_static_ncfile_with_ncgen_cdl(capfd):
    """
    Check for the creation of required directories
    and a \*.nc file from \*.cdl text file using
    command ncgen. This file will be used as an input
    file for the rewrite remap tests.
    Test checks for success of ncgen command.
    """
    #print(f"NCGEN OUTPUT DIRECTORY: {ncgen_static_out}")

    for out_path in ncgen_static_out_paths:
        for snc_fn in STATIC_DATA_NC_FILES:
            if snc_fn.split(".")[0] != out_path.split("/")[-3]:
                continue

            # NCGEN command: ncgen -o [outputfile] [inputfile]
            ex = [ "ncgen", "-k", "64-bit offset",
                   "-o", Path(out_path) / snc_fn,
                   DATA_DIR / STATIC_DATA_FILE_CDL ]

            # Run ncgen command
            sp = subprocess.run( ex, check = False )

            # Check for
            # 1. ncgen command success
            # 2. nc file creation
            assert all([sp.returncode == 0,
                       Path(f"{out_path}/{snc_fn}").exists()])
            out, err = capfd.readouterr()

## TEST REMAP FUNCTION ##
def test_remap_pp_components(capfd):
    """
    Checks for success of remapping a file with rose app using
    the remap-pp-components script as the valid definitions
    are being called by the environment.
    """
    # run script
    try:
        rmp.remap_pp_components(input_dir=REMAP_IN,
                                output_dir=REMAP_OUT,
                                begin_date="19800101T0000Z",
                                current_chunk="P5Y",
                                product=PRODUCT,
                                component="atmos_scalar",
                                copy_tool=COPY_TOOL,
                                yaml_config=str(YAML_EX),
                                ts_workaround=True,
                                ens_mem="")
    except:
        assert False

    # Check for
    # 1. creation of output directory structure,
    # 2. link to nc file in output location
    assert all([Path(f"{REMAP_OUT}/atmos_scalar/{PRODUCT}/monthly/5yr").exists(),
                Path(f"{REMAP_OUT}/atmos_scalar/{PRODUCT}/monthly/5yr/{DATA_NC_FILES[0]}").exists()])
    out, err = capfd.readouterr()

## Pytest can utilize monkeypatch fixture, if needed, which can help set/delete attributes, environments, etc.
## monkeypatch.setenv() used to set/reset specific environment variables in each test,
## without resetting them for all tests or the proceeding test (i.e. - wouldn't effect
## other test's environment variables defined)
def test_remap_pp_components_with_ensmem(capfd):
    """
    Checks for success of remapping a file with rose app config using
    the remap-pp-components script when ens_mem is defined.
    """
    # Redefine ens input and output directories
    remap_ens_in = f"{TEST_OUTDIR}/ncgen-ens-output"
    ncgen_ens_out = Path(remap_ens_in) / NATIVE_GRID / "ens_01" / "atmos_scalar" / FREQ / CHUNK
    remap_ens_out = f"{TEST_OUTDIR}/remap-ens-output"

    # Create ensemble locations
    Path(ncgen_ens_out).mkdir(parents=True,exist_ok=True)
    Path(remap_ens_out).mkdir(parents=True,exist_ok=True)

    # Make sure input nc file is also in ens input location
    shutil.copyfile(Path(ncgen_native_out_paths[0]) / DATA_NC_FILES[0], Path(ncgen_ens_out) / DATA_NC_FILES[0])

    # run script
    try:
        rmp.remap_pp_components(input_dir=remap_ens_in,
                                output_dir=remap_ens_out,
                                begin_date="19800101T0000Z",
                                current_chunk="P5Y",
                                product=PRODUCT,
                                component="atmos_scalar",
                                copy_tool=COPY_TOOL,
                                yaml_config=str(YAML_EX),
                                ts_workaround=True,
                                ens_mem="ens_01")
    except:
        assert False

    # Check for
    # 1. creation of output directory structure,
    # 2. link to nc file in output location
    assert all([Path(f"{remap_ens_out}/atmos_scalar/{PRODUCT}/ens_01/monthly/5yr").exists(),
                Path(f"{remap_ens_out}/atmos_scalar/{PRODUCT}/ens_01/monthly/5yr/{DATA_NC_FILES[0]}").exists()])
    out, err = capfd.readouterr()

@pytest.mark.xfail
def test_remap_pp_components_product_failure(capfd):
    """
    Checks for failure of remapping a file with rose app using
    the remap-pp-components script when the product is ill-defined.
    (not ts or av)
    """
    # run script
    rmp.remap_pp_components(input_dir=REMAP_IN,
                            output_dir=REMAP_OUT,
                            begin_date="19800101T0000Z",
                            current_chunk="P5Y",
                            product="not-ts-or-av",
                            component="atmos_scalar",
                            copy_tool=COPY_TOOL,
                            yaml_config=str(YAML_EX),
                            ts_workaround=True,
                            ens_mem="")

@pytest.mark.xfail
def test_remap_pp_components_begin_date_failure(capfd):
    """
    Checks for failure of remapping a file with rose app using
    the remap-pp-components script when the begin variable is
    ill-defined.
    """
    # run script
    rmp.remap_pp_components(input_dir=REMAP_IN,
                            output_dir=REMAP_OUT,
                            begin_date="123456789T0000Z",
                            current_chunk="P5Y",
                            product=PRODUCT,
                            component="atmos_scalar",
                            copy_tool=COPY_TOOL,
                            yaml_config=str(YAML_EX),
                            ts_workaround=True,
                            ens_mem="")

## STATIC SOURCE REMAPPING ##
def test_remap_pp_components_statics(capfd):
    """
    Test static sources are remapped to output location correctly
    """
    remap_static_out = f"{REMAP_OUT}/static"
    Path(remap_static_out).mkdir(parents=True,exist_ok=True)

    # run script
    try:
        rmp.remap_pp_components(input_dir=REMAP_IN,
                                output_dir=remap_static_out,
                                begin_date="19800101T0000Z",
                                current_chunk="P0Y",
                                product="static",
                                component="atmos_scalar",
                                copy_tool=COPY_TOOL,
                                yaml_config=str(YAML_EX),
                                ts_workaround=False,
                                ens_mem="")
    except:
        assert False

    # Check for
    # 1. creation of output directory structure,
    # 2. link to nc file in output location
    assert all([Path(f"{remap_static_out}/atmos_scalar/{STATIC_FREQ}/{STATIC_CHUNK}").exists(),
                Path(f"{remap_static_out}/atmos_scalar/{STATIC_FREQ}/{STATIC_CHUNK}/{STATIC_DATA_NC_FILES[0]}").exists()])
    out, err = capfd.readouterr()

@pytest.mark.skip(reason="Offline file will not be in same place for everyone here - figure out how to test")
def test_remap_offline_diagnostics(capfd, monkeypatch):
    """
    Test offline diagnostic file remapped to output location correctly
    """
    assert Path(f"{os.getenv('outputDir')}/atmos_scalar/{STATIC_FREQ}/{STATIC_CHUNK}/empty.nc").exists()

## COMPARE INPUT AND OUTPUT FILES ##
def test_nccmp_ncgen_remap(capfd):
    """
    This test compares the results of ncgen and rewrite_remap,
    making sure that the remapped files are identical.
    """
    nccmp = [ "nccmp", "-d",
              Path(f"{REMAP_IN}/{NATIVE_GRID}/atmos_scalar/{FREQ}/{CHUNK}/{DATA_NC_FILES[0]}"),
              Path(f"{REMAP_OUT}/atmos_scalar/{PRODUCT}/monthly/5yr/{DATA_NC_FILES[0]}") ]

    sp = subprocess.run( nccmp, check = False)
    assert sp.returncode == 0
    out, err = capfd.readouterr()

def test_nccmp_ncgen_remap_ens_mem(capfd):
    """
    This test compares the results of ncgen and rewrite_remap,
    making sure that the remapped files are identical.
    """
    # Redefine ens input and output directories
    remap_ens_in = f"{TEST_OUTDIR}/ncgen-ens-output"
    remap_ens_out = f"{TEST_OUTDIR}/remap-ens-output"

    nccmp = [ "nccmp", "-d",
              Path(f"{remap_ens_in}/{NATIVE_GRID}/ens_01/atmos_scalar/{FREQ}/{CHUNK}/{DATA_NC_FILES[0]}"),
              Path(f"{remap_ens_out}/atmos_scalar/{PRODUCT}/ens_01/monthly/5yr/{DATA_NC_FILES[0]}") ]

    sp = subprocess.run( nccmp, check = False)
    assert sp.returncode == 0
    out, err = capfd.readouterr()

def test_nccmp_ncgen_remap_statics(capfd):
    """
    This test compares the results of ncgen and remap,
    making sure that the remapped static files are identical.
    """
    nccmp = [ "nccmp", "-d",
              Path(f"{REMAP_IN}/{NATIVE_GRID}/atmos_static_scalar/{STATIC_FREQ}/{STATIC_CHUNK}/{STATIC_DATA_NC_FILES[0]}"),
              Path(f"{REMAP_OUT}/static/atmos_scalar/{STATIC_FREQ}/{STATIC_CHUNK}/{STATIC_DATA_NC_FILES[0]}")]

    sp = subprocess.run( nccmp, check = False)
    assert sp.returncode == 0
    out, err = capfd.readouterr()

## VARIABLE FILTERING TESTS ##
def test_remap_variable_filtering(capfd):
    """
    Test variable filtering capabilities

    - same file should be found as in first regular remap test,
      but component defined specifies variable co2mass
    """
    # Remove previous output and re-create
    if Path(REMAP_OUT).exists():
        shutil.rmtree(REMAP_OUT)
        Path(REMAP_OUT).mkdir(parents=True,exist_ok=True)

    # run script
    try:
        rmp.remap_pp_components(input_dir=REMAP_IN,
                                output_dir=REMAP_OUT,
                                begin_date="19800101T0000Z",
                                current_chunk="P5Y",
                                product=PRODUCT,
                                component="atmos_scalar_test_vars",
                                copy_tool=COPY_TOOL,
                                yaml_config=str(YAML_EX),
                                ts_workaround=True,
                                ens_mem="")
    except:
        assert False

    # Check for
    # 1. creation of output directory structure,
    # 2. link to nc file in output location
    assert all([Path(f"{REMAP_OUT}/atmos_scalar_test_vars/{PRODUCT}/monthly/5yr").exists(),
                Path(f"{REMAP_OUT}/atmos_scalar_test_vars/{PRODUCT}/monthly/5yr/{DATA_NC_FILES[1]}").exists()])
    out, err = capfd.readouterr()

def test_remap_static_variable_filtering(capfd):
    """
    Test variable filtering capabilities

    - same file should be found as in static remap test,
      but component, defined specifies variable bk
    """
    remap_static_out = f"{REMAP_OUT}/static"
    Path(remap_static_out).mkdir(parents=True,exist_ok=True)

    # run script
    try:
        rmp.remap_pp_components(input_dir=REMAP_IN,
                                output_dir=remap_static_out,
                                begin_date="19800101T0000Z",
                                current_chunk="P0Y",
                                product="static",
                                component="atmos_scalar_test_vars",
                                copy_tool=COPY_TOOL,
                                yaml_config=str(YAML_EX),
                                ts_workaround=False,
                                ens_mem="")
    except:
        assert False

    # Check for
    # 1. creation of output directory structure,
    # 2. link to nc file in output location
    assert all([Path(f"{remap_static_out}/atmos_scalar_test_vars/{STATIC_FREQ}/{STATIC_CHUNK}").exists(),
                Path(f"{remap_static_out}/atmos_scalar_test_vars/{STATIC_FREQ}/{STATIC_CHUNK}/{STATIC_DATA_NC_FILES[1]}").exists()])
    out, err = capfd.readouterr()

@pytest.mark.xfail
def test_remap_variable_filtering_fail(capfd):
    """
    Test failure of variable filtering capabilities when
    variable does not exist; variable = no_var
    """
    # run script
    rmp.remap_pp_components(input_dir=REMAP_IN,
                            output_dir=REMAP_OUT,
                            begin_date="19800101T0000Z",
                            current_chunk="P5Y",
                            product=PRODUCT,
                            component="atmos_scalar_test_vars_fail",
                            copy_tool=COPY_TOOL,
                            yaml_config=str(YAML_EX),
                            ts_workaround=True,
                            ens_mem="")

@pytest.mark.xfail
def test_remap_static_variable_filtering_fail(capfd):
    """
    Test failure of variable filtering capabilities for statics
    when variable does not exist; variables = bk, no_var
    """
    # run script
    rmp.remap_pp_components(input_dir=REMAP_IN,
                            output_dir=f"{REMAP_OUT}/static",
                            begin_date="19800101T0000Z",
                            current_chunk="P0Y",
                            product="static",
                            component="atmos_scalar_static_test_vars_fail",
                            copy_tool=COPY_TOOL,
                            yaml_config=str(YAML_EX),
                            ts_workaround=False,
                            ens_mem="")

def test_remap_chdir(capfd):
    """
    Test that original directory is the same as final directory.
    The remap tool changes into input_dir, source dir, etc., but
    we need to make sure the the final_dir is the fre-cli root
    for testing purposes (and that remap does not leave us
    somewhere we don't want to be)
    """
    # directory before running remap
    original_dir = Path.cwd()

    # run remap which should be changing into the input_dir, etc.
    rmp.remap_pp_components(input_dir=REMAP_IN,
                            output_dir=REMAP_OUT,
                            begin_date="19800101T0000Z",
                            current_chunk="P5Y",
                            product=PRODUCT,
                            component="atmos_scalar",
                            copy_tool=COPY_TOOL,
                            yaml_config=str(YAML_EX),
                            ts_workaround=True,
                            ens_mem="")

    # directory after remap has completed
    final_dir = Path.cwd()

    assert all([original_dir == final_dir])

#to-do:
# - figure out test for offline diagnostics
# - test for when product = "av"
# - test grid = regrid-xy
