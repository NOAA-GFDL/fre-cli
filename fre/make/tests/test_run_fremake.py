''' test "fre make run-fremake" calls without actual compilation '''

import os
from shutil  import rmtree
from pathlib import Path
from click.testing import CliRunner
import pytest
from fre import fre
from fre.make import run_fremake_script

runner=CliRunner()

# command options
YAMLDIR = "fre/make/tests/null_example"
YAMLFILE = "null_model.yaml"
YAMLPATH = f"{YAMLDIR}/{YAMLFILE}"
PLATFORM = ["ci.gnu"]
CONTAINER_PLATFORM = ["hpcme.2023"]
CONTAINER_PLAT2 = ["con.twostep"]
TARGET = ["debug"]
BADOPT = ["foo"]
EXPERIMENT = "null_model_full"
VERBOSE = False

# possible targets
targets = ["debug", "prod", "repro", "debug-openmp", "prod-openmp", "repro-openmp"]

# set up some paths for the tests
SERIAL_TEST_PATH="fre/make/tests/test_run_fremake_serial"
MULTIJOB_TEST_PATH="fre/make/tests/test_run_fremake_multijob"
MULTITARGET_TEST_PATH="fre/make/tests/test_run_fremake_multitarget"
Path(SERIAL_TEST_PATH).mkdir(parents=True,exist_ok=True)
Path(MULTIJOB_TEST_PATH).mkdir(parents=True,exist_ok=True)
Path(MULTITARGET_TEST_PATH).mkdir(parents=True,exist_ok=True)

##def fremake_run(yamlfile,platform,target,parallel,jobs,no_parallel_checkout,execute,verbose):

# yaml file checks
def test_modelyaml_exists():
    assert Path(f"{YAMLDIR}/{YAMLFILE}").exists()

def test_compileyaml_exists():
    assert Path(f"{YAMLDIR}/compile.yaml").exists()

def test_platformyaml_exists():
    assert Path(f"{YAMLDIR}/platforms.yaml").exists()

# expected failures for incorrect options
@pytest.mark.xfail()
def test_bad_platform_option():
    ''' test run-fremake with a invalid platform option'''
    run_fremake_script.fremake_run(YAMLPATH, BADOPT, TARGET, False, 1, False, False, VERBOSE, False, False, False)

@pytest.mark.xfail()
def test_bad_target_option():
    ''' test run-fremake with a invalid target option'''
    run_fremake_script.fremake_run(YAMLPATH, PLATFORM, BADOPT, False, 1, False, False, VERBOSE, False, False, False)

@pytest.mark.xfail()
def test_bad_yamlpath_option():
    ''' test run-fremake with a invalid target option'''
    run_fremake_script.fremake_run(BADOPT[0], PLATFORM, TARGET, False, 1, False, False, VERBOSE, False, False, False)

# tests script/makefile creation without executing (serial compile)
# first test runs the run-fremake command, subsequent tests check for creation of scripts
def test_run_fremake_serial():
    ''' run fre make with run-fremake subcommand and build the null model experiment with gnu'''
    os.environ["TEST_BUILD_DIR"] = SERIAL_TEST_PATH
    run_fremake_script.fremake_run(YAMLPATH, PLATFORM, TARGET, False, 1, False, False, VERBOSE, False, False, False)

def test_run_fremake_compile_script_creation_serial():
    ''' check for compile script creation from previous test '''
    assert Path(f"{SERIAL_TEST_PATH}/fremake_canopy/test/{EXPERIMENT}/{PLATFORM[0]}-{TARGET[0]}/exec/compile.sh").exists()

def test_run_fremake_checkout_script_creation_serial():
    ''' check for checkout script creation from previous test '''
    assert Path(f"{SERIAL_TEST_PATH}/fremake_canopy/test/{EXPERIMENT}/src/checkout.sh").exists()

def test_run_fremake_makefile_creation_serial():
    ''' check for makefile creation from previous test '''
    assert Path(f"{SERIAL_TEST_PATH}/fremake_canopy/test/{EXPERIMENT}/{PLATFORM[0]}-{TARGET[0]}/exec/Makefile").exists()

def test_run_fremake_serial_force_checkout(capfd):
    '''run run-fremake with options for serial build with force-checkout'''
    run_fremake_script.fremake_run(YAMLPATH, PLATFORM, TARGET, False, 1, False, False, VERBOSE, True, False, False)

    #Capture output
    out,err=capfd.readouterr()
    if "Re-creating the checkout script" in out and "Re-creating the compile script" in out:
        assert Path(f"{SERIAL_TEST_PATH}/fremake_canopy/test/{EXPERIMENT}/src/checkout.sh").exists()
        assert Path(f"{SERIAL_TEST_PATH}/fremake_canopy/test/{EXPERIMENT}/{PLATFORM[0]}-{TARGET[0]}/exec/Makefile").exists()
        assert Path(f"{SERIAL_TEST_PATH}/fremake_canopy/test/{EXPERIMENT}/{PLATFORM[0]}-{TARGET[0]}/exec/compile.sh").exists()
    else:
       assert False

def test_run_fremake_serial_force_compile(capfd):
    '''run run-fremake with options for serial build with force-compile'''
    run_fremake_script.fremake_run(YAMLPATH, PLATFORM, TARGET, False, 1, False, False, VERBOSE, False, True, False)

    #Capture output
    out,err=capfd.readouterr()
    if "Re-creating the compile script" in out:
        assert Path(f"{SERIAL_TEST_PATH}/fremake_canopy/test/{EXPERIMENT}/{PLATFORM[0]}-{TARGET[0]}/exec/compile.sh").exists()
    else:
        assert False

# same tests with multijob compile and non-parallel-checkout options enabled
def test_run_fremake_multijob():
    ''' run fre make with run-fremake subcommand and build the null model experiment with gnu'''
    os.environ["TEST_BUILD_DIR"] = MULTIJOB_TEST_PATH
    run_fremake_script.fremake_run(YAMLPATH, PLATFORM, TARGET, True, 4, True, False, VERBOSE, False, False, False)

def test_run_fremake_compile_script_creation_multijob():
    ''' check for compile script creation from previous test '''
    assert Path(f"{MULTIJOB_TEST_PATH}/fremake_canopy/test/{EXPERIMENT}/{PLATFORM[0]}-{TARGET[0]}/exec/compile.sh").exists()

def test_run_fremake_checkout_script_creation_multijob():
    ''' check for checkout script creation from previous test '''
    assert Path(f"{MULTIJOB_TEST_PATH}/fremake_canopy/test/{EXPERIMENT}/src/checkout.sh").exists()

def test_run_fremake_makefile_creation_multijob():
    ''' check for makefile creation from previous test '''
    assert Path(f"{MULTIJOB_TEST_PATH}/fremake_canopy/test/{EXPERIMENT}/{PLATFORM[0]}-{TARGET[0]}/exec/Makefile").exists()

# tests container build script/makefile/dockerfile creation
def test_run_fremake_container():
    '''run run-fremake with options for containerized build'''
    if Path("Dockerfile").exists() or Path("createContainer.sh").exists():
        Path(f"{os.getcwd()}/Dockerfile").unlink()
        Path(f"{os.getcwd()}/createContainer.sh").unlink()

    run_fremake_script.fremake_run(YAMLPATH, CONTAINER_PLATFORM, TARGET, False, 1, True, False, VERBOSE, False, False, False)

def test_run_fremake_build_script_creation_container():
    ''' checks container build script creation from previous test '''
    assert Path("createContainer.sh").exists()

def test_run_fremake_dockerfile_creation_container():
    ''' checks dockerfile creation from previous test '''
    assert Path("Dockerfile").exists()

def test_run_fremake_checkout_script_creation_container():
    ''' checks checkout script creation from previous test '''
    assert Path(f"tmp/{CONTAINER_PLATFORM[0]}/checkout.sh").exists()

def test_run_fremake_makefile_creation_container():
    ''' checks makefile creation from previous test '''
    assert Path(f"tmp/{CONTAINER_PLATFORM[0]}/Makefile").exists()

def test_run_fremake_run_script_creation_container():
    ''' checks (internal) container run script creation from previous test '''
    assert Path(f"tmp/{CONTAINER_PLATFORM[0]}/execrunscript.sh").exists()

# tests container 2 stage build script/makefile/dockerfile creation
def test_run_fremake_2stage_container():
    '''run run-fremake with options for containerized build'''
    # Without force-dockerfile or force-checkout option, clean files first
    # or else it'll read that they exist already and not make the execrunscript.sh
    if Path("Dockerfile").exists() or Path("createContainer.sh").exists():
        Path("Dockerfile").unlink()
        Path("createContainer.sh").unlink()

    run_fremake_script.fremake_run(YAMLPATH, CONTAINER_PLAT2, TARGET, False, 1, True, False, VERBOSE, False, False, False)

def test_run_fremake_2stage_build_script_creation_container():
    ''' checks container build script creation from previous test '''
    assert Path("createContainer.sh").exists()

def test_run_fremake_2stage_dockerfile_creation_container():
    ''' checks dockerfile creation from previous test '''
    assert Path("Dockerfile").exists()

def test_run_fremake_2stage_checkout_script_creation_container():
    ''' checks checkout script creation from previous test '''
    assert Path(f"tmp/{CONTAINER_PLAT2[0]}/checkout.sh").exists()

def test_run_fremake_2stage_makefile_creation_container():
    ''' checks makefile creation from previous test '''
    assert Path(f"tmp/{CONTAINER_PLAT2[0]}/Makefile").exists()

def test_run_fremake_2stage_run_script_creation_container():
    ''' checks (internal) container run script creation from previous test '''
    assert Path(f"tmp/{CONTAINER_PLAT2[0]}/execrunscript.sh").exists()

# tests for builds with multiple targets

def test_run_fremake_container_force_checkout(capfd):
    '''run run-fremake with options for containerized build with force-checkout option'''
    run_fremake_script.fremake_run(YAMLPATH, CONTAINER_PLATFORM, TARGET, False, 1, True, False, VERBOSE, True, False, False)

    #Capture output
    out,err=capfd.readouterr()
    print(out)

    if "Re-creating the checkout script" in out:
        assert Path(f"tmp/{CONTAINER_PLATFORM[0]}/checkout.sh").exists()
        assert Path(f"tmp/{CONTAINER_PLATFORM[0]}/Makefile").exists()
        assert Path("Dockerfile").exists()
        assert Path("createContainer.sh").exists()
        assert Path(f"tmp/{CONTAINER_PLATFORM[0]}/execrunscript.sh").exists()
    else:
       assert False

def test_run_fremake_container_force_dockerfile(capfd):
    '''run run-fremake with options for containerized build with force-dockerfile option'''
    run_fremake_script.fremake_run(YAMLPATH, CONTAINER_PLATFORM, TARGET, False, 1, True, False, VERBOSE, False, False, True)

    #Capture output
    out,err=capfd.readouterr()
    if "Re-creating Dockerfile" in out:
        assert Path("Dockerfile").exists()
        assert Path("createContainer.sh").exists()
        assert Path(f"tmp/{CONTAINER_PLATFORM[0]}/execrunscript.sh").exists()
    else:
       assert False

# tests for builds with multiple targets
def test_run_fremake_bad_target():
    ''' checks invalid target returns an error '''
    os.environ["TEST_BUILD_DIR"] = MULTITARGET_TEST_PATH
    result = runner.invoke(fre.fre, args=["make", "run-fremake", "-y", YAMLPATH, "-p", PLATFORM, "-t", "prod-repro"])
    assert result.exit_code == 1

def test_run_fremake_multiple_targets():
    ''' passes all valid targets for a build '''
    result = runner.invoke(fre.fre, args=["make", "run-fremake", "-y", YAMLPATH, "-p", PLATFORM[0], "-t",  \
                                          "debug", "-t", "prod", "-t", "repro", "-t", "debug-openmp", "-t",\
                                          "prod-openmp", "-t", "repro-openmp"])
    assert result.exit_code == 0

def test_run_fremake_compile_script_creation_multitarget():
    ''' check compile scripts for all targets exist from previous test'''
    os.environ["TEST_BUILD_DIR"] = MULTITARGET_TEST_PATH
    for t in targets:
        assert Path(f"{MULTITARGET_TEST_PATH}/fremake_canopy/test/{EXPERIMENT}/{PLATFORM[0]}-{t}/exec/compile.sh").exists()

def test_run_fremake_checkout_script_creation_multitarget():
    ''' check for checkout script creation for mulit-target build'''
    ''' check checkout script exists from previous test'''
    os.environ["TEST_BUILD_DIR"] = MULTITARGET_TEST_PATH
    assert Path(f"{MULTITARGET_TEST_PATH}/fremake_canopy/test/{EXPERIMENT}/src/checkout.sh").exists()

def test_run_fremake_makefile_creation_multitarget():
    ''' check for makefile creation from previous test '''
    os.environ["TEST_BUILD_DIR"] = MULTITARGET_TEST_PATH
    for t in targets:
        assert Path(f"{MULTITARGET_TEST_PATH}/fremake_canopy/test/{EXPERIMENT}/{PLATFORM[0]}-{t}/exec/Makefile").exists()
