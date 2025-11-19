"""
Test fre make checkout-script
"""
from pathlib import Path
import os
import subprocess
from fre.make import create_checkout_script
import shutil

# Set example yaml paths, input directory
TEST_DIR = str(Path("fre/make/tests"))
YAMLFILE = str(Path(f"{TEST_DIR}/null_example/null_model.yaml"))

#set platform and target
PLATFORM = ["ci.gnu"]
TARGET = ["debug"]

#set output directory
# Set home for ~/cylc-src location in script
#run checkout command
OUT = f"{TEST_DIR}/checkout_out"
os.environ["TEST_BUILD_DIR"] = OUT

def test_nullyaml_exists():
    """
    Make sure combined yaml file exists
    """
    assert Path(f"{YAMLFILE}").exists()

def test_nullyaml_filled():
    """
    Make sure null.yaml is not an empty file
    """
    sum(1 for _ in open(f'{YAMLFILE}')) > 1

def test_checkout_script_exists():
    """
    Make sure checkout file exists
    """
    os.environ["TEST_BUILD_DIR"] = OUT # env vars seem to be carrying over from other tests, need to set it again
    shutil.rmtree(f"{OUT}/fremake_canopy/test", ignore_errors=True)
    create_checkout_script.checkout_create(YAMLFILE,
                                           PLATFORM,
                                           TARGET,
                                           no_parallel_checkout = False,
                                           njobs = False,
                                           execute = False,
                                           verbose = False,
                                           force_checkout = False)
    #assert result.exit_code == 0
    assert Path(f"{OUT}/fremake_canopy/test/null_model_full/src/checkout.sh").exists()

def test_checkout_verbose():
    """
    check if --verbose option works
    """
    create_checkout_script.checkout_create(YAMLFILE,
                                           PLATFORM,
                                           TARGET,
                                           no_parallel_checkout = False,
                                           njobs = False,
                                           execute = False,
                                           verbose = True,
                                           force_checkout = False)

def test_checkout_execute():
    """
    check if --execute option works
    """
    shutil.rmtree(f"{OUT}/fremake_canopy/test", ignore_errors=True)
    create_checkout_script.checkout_create(YAMLFILE,
                                           PLATFORM,
                                           TARGET,
                                           no_parallel_checkout = False,
                                           njobs = 2,
                                           execute = True,
                                           verbose = False,
                                           force_checkout = False)

def test_checkout_no_parallel_checkout():
    """
    check if --no_parallel_checkout option works
    """
    create_checkout_script.checkout_create(YAMLFILE,
                                           PLATFORM,
                                           TARGET,
                                           no_parallel_checkout = True,
                                           njobs = False,
                                           execute = False,
                                           verbose = False,
                                           force_checkout = False)

def test_checkout_force_checkout(caplog):
    """
    Test re-creation of checkout script if --force-checkout is passed.
    """
    shutil.rmtree(f"{OUT}/fremake_canopy/test", ignore_errors=True)
    ## Mock checkout script with some content we can check
    # create come checkout script
    mcs = Path(f"{OUT}/fremake_canopy/test/null_model_full/src")
    mcs.mkdir(parents = True)
    with open(f"{mcs}/checkout.sh", 'w') as f:
        f.write("mock checkout content")

    # Check mock script was created correctly
    assert Path(f"{OUT}/fremake_canopy/test/null_model_full/src/checkout.sh").exists()
    # Check mock content
    with open(f"{mcs}/checkout.sh", 'r') as f:
        assert f.read() == "mock checkout content"

    # Re-create checkout script
    create_checkout_script.checkout_create(YAMLFILE,
                                           PLATFORM,
                                           TARGET,
                                           no_parallel_checkout = True,
                                           njobs = False,
                                           execute = False,
                                           verbose = False,
                                           force_checkout = True)

    # Check it exists, check output, check content
    assert ([Path(f"{OUT}/fremake_canopy/test/null_model_full/src/checkout.sh").exists(),
             "Checkout script PREVIOUSLY created" in caplog.text,
             "*** REMOVING CHECKOUT SCRIPT ***" in caplog.text,
             "Checkout script created" in caplog.text])

    expected_line = "git clone --recursive --jobs=False https://github.com/NOAA-GFDL/FMS.git -b main FMS"
    # Check one expected line is now populating the re-created checkout script
    with open(f"{OUT}/fremake_canopy/test/null_model_full/src/checkout.sh", 'r') as f2:
        assert expected_line in f2.read()

###either mock checkout script or change yaml slightly to have 2 different checkout script results
##check content of previous checkout script
##change yaml slightly/rerun
##checkout content of new checkout script
