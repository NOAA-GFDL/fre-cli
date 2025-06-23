import os
import subprocess
import shutil
from pathlib import Path
import pytest
import fre.app.remap_pp_components.remap_pp_components as rmp

CWD = os.getcwd()
TEST_DIR = Path(f"{CWD}/fre/app/remap_pp_components/tests")

## Path to test data
DATA_DIR = Path(f"{CWD}/fre/app/remap_pp_components/tests/test-data")
DATA_FILE_CDL = Path("atmos_scalar.198001-198412.co2mass.cdl") # CDL file to generate nc file from ncgen
DATA_FILE_NC = Path("atmos_scalar.198001-198412.co2mass.nc")   # Create NC file name to test remap functionality

# YAML configuration example file
YAML_EX = f"{DATA_DIR}/yaml_ex.yaml"

## keep around - will come in handy eventually when pp
## relies on dictionary instead of output yaml config
#YAML_EX = {"postprocess": {"component": [
#                                     {"type": "atmos_scalar", 
#                                      "sources": [{"history_file": "atmos_scalar", "variables": "['co2mass']"}],
#                                      "inputRealm": "atmos",
#                                      "static": [{"source": "atmos_static_scalar", "variables": "['bk']"},
#                                                 {"offline_source": "/home/Dana.Singh/fre/CMIP7-static/fre-workflows/app/remap-pp-components/test-data/empty.nc"}],
#                                      "postprocess_on": "True"}
#                                    ]
#                        }
#          }

# Define/create necessary output/input locatiions
TEST_OUTDIR = f"{TEST_DIR}/test-outDir"
REMAP_IN = f"{TEST_OUTDIR}/ncgen-output"
REMAP_OUT = f"{TEST_OUTDIR}/remap-output"

# Define variables
COMPOUT = "atmos_scalar"
NATIVE_GRID = "native"
REGRID_GRID = "regrid-xy"
FREQ = "P1M"
CHUNK = "P5Y"
PRODUCT = "ts"
COPY_TOOL = "cp"

# Define static variables 
STATIC_DATA_FILE_CDL = Path("atmos_static_scalar.bk.cdl")      # CDL file to generate static nc file from ncgen
STATIC_DATA_FILE_NC = Path("atmos_static_scalar.bk.nc")       # Create NC file name to test static functinality
STATIC_PRODUCT = "static"
STATIC_FREQ = "P0Y"
STATIC_CHUNK = "P0Y"
STATIC_SRC = "atmos_static_scalar"

# environment variables
#os.environ['inputDir'] = REMAP_IN
#os.environ['outputDir'] = REMAP_OUT
#os.environ['currentChunk'] = "P5Y"
#os.environ['components'] = COMPOUT
#os.environ['begin'] = "19800101T0000Z"
#os.environ['product'] = PRODUCT
#os.environ['dirTSWorkaround'] = "1"
#os.environ['COPY_TOOL'] = COPY_TOOL
#os.environ['yaml_config'] = str(YAML_EX)
#os.environ['src_vars_dict'] = "{'atmos_scalar': 'all', 'atmos_static_scalar': 'all'}"

# Set up input directory (location previously made in flow.cylc workflow)
ncgen_native_out = Path(REMAP_IN) / NATIVE_GRID / COMPOUT / FREQ / CHUNK
ncgen_static_out = Path(REMAP_IN) / NATIVE_GRID / STATIC_SRC / STATIC_FREQ / STATIC_CHUNK

#If output directory exists, remove and create again
if Path(TEST_OUTDIR).exists():
    shutil.rmtree(TEST_OUTDIR)
    Path(ncgen_native_out).mkdir(parents=True,exist_ok=True)
    Path(ncgen_static_out).mkdir(parents=True,exist_ok=True)
    Path(REMAP_OUT).mkdir(parents=True,exist_ok=True)
else:
    Path(ncgen_native_out).mkdir(parents=True,exist_ok=True)
    Path(ncgen_static_out).mkdir(parents=True,exist_ok=True)
    Path(REMAP_OUT).mkdir(parents=True,exist_ok=True)

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
    and a *.nc file from *.cdl text file using
    command ncgen. This file will be used as an input
    file for the rewrite remap tests.
    Test checks for success of ncgen command.
    """
    print(f"NCGEN OUTPUT DIRECTORY: {ncgen_native_out}")

    # NCGEN command: ncgen -o [outputfile] [inputfile]
    ex = [ "ncgen", "-k", "64-bit offset",
           "-o", Path(ncgen_native_out) / DATA_FILE_NC,
           DATA_DIR / DATA_FILE_CDL ]

    print (ex)

    # Run ncgen command
    sp = subprocess.run( ex, check = False )

    # Check for
    # 1. ncgen command success
    # 2. nc file creation
    assert all([sp.returncode == 0,
               Path(ncgen_native_out / DATA_FILE_NC).exists()])
    out, err = capfd.readouterr()

def test_create_static_ncfile_with_ncgen_cdl(capfd):
    """
    Check for the creation of required directories
    and a *.nc file from *.cdl text file using
    command ncgen. This file will be used as an input
    file for the rewrite remap tests.
    Test checks for success of ncgen command.
    """
    print(f"NCGEN OUTPUT DIRECTORY: {ncgen_static_out}")

    # NCGEN command: ncgen -o [outputfile] [inputfile]
    ex = [ "ncgen", "-k", "64-bit offset",
           "-o", Path(ncgen_static_out) / STATIC_DATA_FILE_NC,
           DATA_DIR / STATIC_DATA_FILE_CDL ]

    print (ex)

    # Run ncgen command
    sp = subprocess.run( ex, check = False )

    # Check for
    # 1. ncgen command success
    # 2. nc file creation
    assert all([sp.returncode == 0,
               Path(ncgen_static_out / STATIC_DATA_FILE_NC).exists()])
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
                                components=COMPOUT,
                                copy_tool=COPY_TOOL,
                                yaml_config=str(YAML_EX),
                                ts_workaround="1",
                                ens_mem="")
    except:
        assert False

    # Check for
    # 1. creation of output directory structre,
    # 2. link to nc file in output location
    assert all([Path(f"{REMAP_OUT}/{COMPOUT}/{PRODUCT}/monthly/5yr").exists(),
                Path(f"{REMAP_OUT}/{COMPOUT}/{PRODUCT}/monthly/5yr/{DATA_FILE_NC}").exists()])
    out, err = capfd.readouterr()

## Pytest utilizes mokeypatch fixture which can help set/delete attributes, environments, etc.
## monkeypatch.setenv() used to set/reset specific envrionment variables in each test, 
## without resetting them for all tests or the proceeding test (i.e. - wouldn't effect 
## other test's envrionment variables defined)
def test_remap_pp_components_with_ensmem(capfd, monkeypatch):
    """
    Checks for success of remapping a file with rose app config using
    the remap-pp-components script when ens_mem is defined.
    """
    # Redefine ens input and output directories
    remap_ens_in = f"{TEST_OUTDIR}/ncgen-ens-output"
    ncgen_ens_out = Path(remap_ens_in) / NATIVE_GRID / "ens_01" / COMPOUT / FREQ / CHUNK
    remap_ens_out = f"{TEST_OUTDIR}/remap-ens-output"

#    # Specify environment variables for just this test
#    monkeypatch.setenv('inputDir', remap_ens_in)
#    monkeypatch.setenv('outputDir', remap_ens_out)
#    monkeypatch.setenv('ens_mem', "ens_01") #ens_mem now defined

    # Create ensemble locations
    Path(ncgen_ens_out).mkdir(parents=True,exist_ok=True)
    Path(remap_ens_out).mkdir(parents=True,exist_ok=True)

    # Make sure input nc file is also in ens input location
    shutil.copyfile(Path(ncgen_native_out) / DATA_FILE_NC, Path(ncgen_ens_out) / DATA_FILE_NC)

    # run script
    try:
        rmp.remap_pp_components(input_dir=remap_ens_in,
                                output_dir=remap_ens_out,
                                begin_date="19800101T0000Z",
                                current_chunk="P5Y",
                                product=PRODUCT,
                                components=COMPOUT,
                                copy_tool=COPY_TOOL,
                                yaml_config=str(YAML_EX),
                                ts_workaround="1",
                                ens_mem="ens_01")
    except:
        assert False

    # Check for
    # 1. creation of output directory structre,
    # 2. link to nc file in output location
    assert all([Path(f"{remap_ens_out}/{COMPOUT}/{PRODUCT}/ens_01/monthly/5yr").exists(),
                Path(f"{remap_ens_out}/{COMPOUT}/{PRODUCT}/ens_01/monthly/5yr/{DATA_FILE_NC}").exists()])
    out, err = capfd.readouterr()

@pytest.mark.xfail
def test_remap_pp_components_product_failure(capfd, monkeypatch):
    """
    Checks for failure of remapping a file with rose app using
    the remap-pp-components script when the product is ill-defined.
    (not ts or av)
    """
#    # Specify environment variables for just this test
#    monkeypatch.setenv('product', "not-ts-or-av")

    # run script
    rmp.remap_pp_components(input_dir=REMAP_IN,
                            output_dir=REMAP_OUT,
                            begin_date="19800101T0000Z",
                            current_chunk="P5Y",
                            product="not-ts-or-av",
                            components=COMPOUT,
                            copy_tool=COPY_TOOL,
                            yaml_config=str(YAML_EX),
                            ts_workaround="1",
                            ens_mem="")

@pytest.mark.xfail
def test_remap_pp_components_begin_date_failure(capfd, monkeypatch):
    """
    Checks for failure of remapping a file with rose app using
    the remap-pp-components script when the begin variable is
    ill-defined.
    """
#    # Specify environment variables for just this test
#    monkeypatch.setenv('begin', "123456789T0000Z")

    # run script
    rmp.remap_pp_components(input_dir=REMAP_IN,
                            output_dir=REMAP_OUT,
                            begin_date="123456789T0000Z",
                            current_chunk="P5Y",
                            product=PRODUCT,
                            components=COMPOUT,
                            copy_tool=COPY_TOOL,
                            yaml_config=str(YAML_EX),
                            ts_workaround="1",
                            ens_mem="")

## STATIC SOURCE REMAPPING ##
def test_remap_pp_components_statics(capfd, monkeypatch):
    """
    Test static sources are remapped to output location correctly
    """
#    # Specify environment variables for just this test
#    monkeypatch.setenv('outputDir', f"{REMAP_OUT}/static")
#    monkeypatch.setenv('currentChunk', "P0Y")
#    monkeypatch.setenv('product', "static") 
#    monkeypatch.setenv('dirTSWorkaround', "")

    remap_static_out = f"{REMAP_OUT}/static"
    Path(remap_static_out).mkdir(parents=True,exist_ok=True)

    # run script
    try:
        rmp.remap_pp_components(input_dir=REMAP_IN,
                                output_dir=remap_static_out,
                                begin_date="19800101T0000Z",
                                current_chunk="P0Y",
                                product="static",
                                components=COMPOUT,
                                copy_tool=COPY_TOOL,
                                yaml_config=str(YAML_EX),
                                ts_workaround="",
                                ens_mem="")
    except:
        assert False

    # Check for
    # 1. creation of output directory structre,
    # 2. link to nc file in output location
    assert all([Path(f"{remap_static_out}/atmos_scalar/{STATIC_FREQ}/{STATIC_CHUNK}").exists(),
                Path(f"{remap_static_out}/atmos_scalar/{STATIC_FREQ}/{STATIC_CHUNK}/{STATIC_DATA_FILE_NC}").exists()])
    out, err = capfd.readouterr()

@pytest.mark.skip(reason="Offline file will not be in same place for everyone here - figure out how to test")
def test_remap_offline_diagnostics(capfd, monkeypatch):
    """
    Test offline diagnostic file remapped to output location correctly
    """
    # Specify environment variables for just this test
    monkeypatch.setenv('outputDir', f"{REMAP_OUT}/static")
    monkeypatch.setenv('currentChunk', "P0Y")
    monkeypatch.setenv('product', "static")
    monkeypatch.setenv('dirTSWorkaround', "")

    assert Path(f"{os.getenv('outputDir')}/atmos_scalar/{STATIC_FREQ}/{STATIC_CHUNK}/empty.nc").exists()

## COMPARE INPUT AND OUTPUT FILES ##
def test_nccmp_ncgen_remap(capfd):
    """
    This test compares the results of ncgen and rewrite_remap,
    making sure that the remapped files are identical.
    """
    nccmp = [ "nccmp", "-d",
              Path(f"{REMAP_IN}/{NATIVE_GRID}/{COMPOUT}/{FREQ}/{CHUNK}/{DATA_FILE_NC}"),
              Path(f"{REMAP_OUT}/{COMPOUT}/{PRODUCT}/monthly/5yr/{DATA_FILE_NC}") ]

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
              Path(f"{remap_ens_in}/{NATIVE_GRID}/ens_01/{COMPOUT}/{FREQ}/{CHUNK}/{DATA_FILE_NC}"),
              Path(f"{remap_ens_out}/{COMPOUT}/{PRODUCT}/ens_01/monthly/5yr/{DATA_FILE_NC}") ]

    sp = subprocess.run( nccmp, check = False)
    assert sp.returncode == 0
    out, err = capfd.readouterr()

def test_nccmp_ncgen_remap_statics(capfd):
    """
    This test compares the results of ncgen and remap,
    making sure that the remapped static files are identical.
    """
    nccmp = [ "nccmp", "-d",
              Path(f"{REMAP_IN}/{NATIVE_GRID}/{STATIC_SRC}/{STATIC_FREQ}/{STATIC_CHUNK}/{STATIC_DATA_FILE_NC}"),
              Path(f"{REMAP_OUT}/static/atmos_scalar/{STATIC_FREQ}/{STATIC_CHUNK}/{STATIC_DATA_FILE_NC}")]

    sp = subprocess.run( nccmp, check = False)
    assert sp.returncode == 0
    out, err = capfd.readouterr()

## VARIABLE FILTERING TESTS ##
def test_remap_variable_filtering(capfd, monkeypatch):
    """
    Test variable filtering capabilties
    - same file should be found as in first regular remap test,
      but component defined specifies variable co2mass
    """
    # Remove previous output and re-create
    if Path(REMAP_OUT).exists():
        shutil.rmtree(REMAP_OUT)
        Path(REMAP_OUT).mkdir(parents=True,exist_ok=True)

#    # Specify environment variables for just this test
#    monkeypatch.setenv('components', "atmos_scalar_test_vars")

    # run script
    try:
        rmp.remap_pp_components(input_dir=REMAP_IN,
                                output_dir=REMAP_OUT,
                                begin_date="19800101T0000Z",
                                current_chunk="P5Y",
                                product=PRODUCT,
                                components="atmos_scalar_test_vars",
                                copy_tool=COPY_TOOL,
                                yaml_config=str(YAML_EX),
                                ts_workaround="1",
                                ens_mem="")
    except:
        assert False

    # Check for
    # 1. creation of output directory structre,
    # 2. link to nc file in output location
    assert all([Path(f"{REMAP_OUT}/atmos_scalar_test_vars/{PRODUCT}/monthly/5yr").exists(),
                Path(f"{REMAP_OUT}/atmos_scalar_test_vars/{PRODUCT}/monthly/5yr/{DATA_FILE_NC}").exists()])
    out, err = capfd.readouterr()

def test_remap_static_variable_filtering(capfd, monkeypatch):
    """
    Test variable filtering capabilties
    - same file should be found as in static remap test,
      but component, defined specifies variable bk
    """
#    # Specify environment variables for just this test
#    monkeypatch.setenv('outputDir', f"{REMAP_OUT}/static")
#    monkeypatch.setenv('currentChunk', "P0Y")
#    monkeypatch.setenv('product', "static")
#    monkeypatch.setenv('dirTSWorkaround', "")
#    monkeypatch.setenv('components', "atmos_scalar_test_vars")

    remap_static_out = f"{REMAP_OUT}/static"
    Path(remap_static_out).mkdir(parents=True,exist_ok=True)

    # run script
    try:
        rmp.remap_pp_components(input_dir=REMAP_IN,
                                output_dir=remap_static_out,
                                begin_date="19800101T0000Z",
                                current_chunk="P0Y",
                                product="static",
                                components="atmos_scalar_test_vars",
                                copy_tool=COPY_TOOL,
                                yaml_config=str(YAML_EX),
                                ts_workaround="",
                                ens_mem="")
    except:
        assert False

    # Check for
    # 1. creation of output directory structre,
    # 2. link to nc file in output location
    assert all([Path(f"{remap_static_out}/atmos_scalar_test_vars/{STATIC_FREQ}/{STATIC_CHUNK}").exists(),
                Path(f"{remap_static_out}/atmos_scalar_test_vars/{STATIC_FREQ}/{STATIC_CHUNK}/{STATIC_DATA_FILE_NC}").exists()])
    out, err = capfd.readouterr()
 
@pytest.mark.xfail
def test_remap_variable_filtering_fail(capfd, monkeypatch):
    """
    Test failure of variable filtering capabilties when
    variable does not exist; variable = no_var
    """
#    # Specify environment variables for just this test
#    monkeypatch.setenv('components', "atmos_scalar_test_vars_fail")

    # run script
    rmp.remap_pp_components(input_dir=REMAP_IN,
                            output_dir=REMAP_OUT,
                            begin_date="19800101T0000Z",
                            current_chunk="P5Y",
                            product=PRODUCT,
                            components="atmos_scalar_test_vars_fail",
                            copy_tool=COPY_TOOL,
                            yaml_config=str(YAML_EX),
                            ts_workaround="1",
                            ens_mem="")

@pytest.mark.xfail
def test_remap_static_variable_filtering_fail(capfd, monkeypatch):
    """
    Test failure of variable filtering capabilties for statics
    when variable does not exist; variables = bk, no_var
    """
#    # Specify environment variables for just this test
#    monkeypatch.setenv('outputDir', f"{REMAP_OUT}/static")
#    monkeypatch.setenv('currentChunk', "P0Y")
#    monkeypatch.setenv('product', "static")
#    monkeypatch.setenv('dirTSWorkaround', "")
#    monkeypatch.setenv('components', "atmos_scalar_static_test_vars_fail")

    # run script
    rmp.remap_pp_components(input_dir=REMAP_IN,
                            output_dir=f"{REMAP_OUT}/static",
                            begin_date="19800101T0000Z",
                            current_chunk="P0Y",
                            product="static",
                            components="atmos_scalar_static_test_vars_fail",
                            copy_tool=COPY_TOOL,
                            yaml_config=str(YAML_EX),
                            ts_workaround="",
                            ens_mem="")

#to-do:
# - mulitple components
# - figure out test for offline diagnostics
# - test for when product = "av"
# - test grid = regrid-xy
