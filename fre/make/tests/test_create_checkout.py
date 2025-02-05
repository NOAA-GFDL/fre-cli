#tests for the create-checkout step of fre-make, for null_model.yaml
from pathlib import Path
import os
import subprocess
from fre.make import create_checkout_script

# Set example yaml paths, input directory
TEST_DIR = str(Path("fre/make/tests"))
YAMLFILE = str(Path(f"{TEST_DIR}/null_example/null_model.yaml"))

#set platform and target
PLATFORM = ["ci.gnu"]
TARGET = ["debug"]

#set output directory
# Set home for ~/cylc-src location in script
#run checkout command
OUT = f"{TEST_DIR}/test_run_fremake_multitarget"
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
    subprocess.run(["rm","-rf",f"{OUT}/fremake_canopy/test/null_model_full/src/checkout.sh"])
    create_checkout_script.checkout_create(YAMLFILE,
                                           PLATFORM,
                                           TARGET,
                                           no_parallel_checkout = False,
                                           jobs = False, execute = False,
                                           verbose = False)
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
                                           jobs = False, 
                                           execute = False,
                                           verbose = True)

def test_checkout_execute():
    """
    check if --execute option works
    """
    subprocess.run(["rm","-rf",f"{OUT}/fremake_canopy/test"])
    create_checkout_script.checkout_create(YAMLFILE,
                                           PLATFORM,
                                           TARGET,
                                           no_parallel_checkout = False,
                                           jobs = 2,
                                           execute = True,
                                           verbose = False)
    
def test_checkout_no_parallel_checkout():
    """
    check if --no_parallel_checkout option works
    """
    create_checkout_script.checkout_create(YAMLFILE,
                                           PLATFORM,
                                           TARGET,
                                           no_parallel_checkout = True,
                                           jobs = False,
                                           execute = False,
                                           verbose = False)

