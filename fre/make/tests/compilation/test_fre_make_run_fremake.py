''' test "fre make run-fremake" calls '''
''' these tests assume your os is the ci image (gcc 14 + mpich on rocky 8)'''

# def fremake_run(yamlfile,platform,target,parallel,jobs,no_parallel_checkout,verbose):

import os
from fre.make import runFremake
from pathlib import Path

# command options
YAMLFILE = "fre/make/tests/null_example/null_model.yaml"
PLATFORM = [ "ci.gnu" ]
CONTAINER_PLATFORM = ["hpcme.2023"]
TARGET = ["debug"]
EXPERIMENT = "null_model_full"
VERBOSE = False 

# get HOME dir to check output
HOME_DIR = os.environ["HOME"]

# compilation tests

def test_fre_make_run_fremake_serial_compile():
    ''' test run-fremake serial compile with gnu'''
    runFremake.fremake_run(YAMLFILE, PLATFORM, TARGET, False, 1, False, VERBOSE)
    assert Path(f"{HOME_DIR}/fremake_canopy/test/{EXPERIMENT}/{PLATFORM[0]}-{TARGET[0]}/exec/{EXPERIMENT}.x").exists()


def test_fre_make_run_fremake_multijob_compile():
    ''' test run-fremake parallel compile with gnu'''
    runFremake.fremake_run(YAMLFILE, PLATFORM, TARGET, True, 4, False, VERBOSE)
    assert Path(f"{HOME_DIR}/fremake_canopy/test/{EXPERIMENT}/{PLATFORM[0]}-{TARGET[0]}/exec/{EXPERIMENT}.x").exists()

def test_fre_make_run_fremake_container_build():
    ''' test run-fremake serial compile with gnu'''
    runFremake.fremake_run(YAMLFILE, PLATFORM, TARGET, False, 1, False, VERBOSE)
    assert Path(f"{HOME_DIR}/fremake_canopy/test/{EXPERIMENT}/{PLATFORM[0]}-{TARGET[0]}/exec/{EXPERIMENT}.x").exists()


# script/makefile creation tests

def test_fre_make_run_fremake_checkout_script():
    ''' check for checkout script creation '''
    runFremake.fremake_run(YAMLFILE, PLATFORM, TARGET, False, 1, False, VERBOSE)
    assert Path(f"{HOME_DIR}/fremake_canopy/test/{EXPERIMENT}/src/checkout.sh").exists()

def test_fre_make_run_fremake_checkout_script_npc():
    ''' check for checkout script creation with non-parallel checkout option'''
    runFremake.fremake_run(YAMLFILE, PLATFORM, TARGET, False, 1, True, VERBOSE)
    assert Path(f"{HOME_DIR}/fremake_canopy/test/{EXPERIMENT}/src/checkout.sh").exists()

def test_fre_make_run_fremake_compile_script():
    ''' check for compilation script creation '''
    runFremake.fremake_run(YAMLFILE, PLATFORM, TARGET, False, 1, False, VERBOSE)
    assert Path(f"{HOME_DIR}/fremake_canopy/test/{EXPERIMENT}/{PLATFORM[0]}-{TARGET[0]}/exec/compile.sh").exists()

def test_fre_make_run_fremake_makefile():
    ''' check for checkout script creation with non-parallel checkout option'''
    runFremake.fremake_run(YAMLFILE, PLATFORM, TARGET, False, 1, True, VERBOSE)
    assert Path(f"{HOME_DIR}/fremake_canopy/test/{EXPERIMENT}/{PLATFORM[0]}-{TARGET[0]}/exec/Makefile").exists()

