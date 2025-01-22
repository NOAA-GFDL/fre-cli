#tests for the create-checkout step of fre-make, for null_model.yaml
from pathlib import Path
import os
import subprocess
from fre.make import create_checkout_script

# Set example yaml paths, input directory
TEST_DIR = str(Path("fre/make/tests"))
YAMLFILE = str(Path(f"{TEST_DIR}/null_example/null_model.yaml"))

#set platform and target
PLATFORM = ["ncrc5.intel23"]
TARGET = ["debug"]

#set output directory
# Set home for ~/cylc-src location in script
#run checkout command
OUT = f"{TEST_DIR}/configure_yaml_out"
os.environ["TEST_BUILD_DIR"] = OUT

def test_checkout_script_exists():
    """
    Make sure checkout file exists
    """
    subprocess.run(["rm","-rf",f"{OUT}/fremake_canopy/test/null_model_full/src/checkout.sh"])
    create_checkout_script.checkout_create(YAMLFILE,PLATFORM,TARGET,False,False, False, False)
    #assert result.exit_code == 0
    assert Path(f"{OUT}/fremake_canopy/test/null_model_full/src/checkout.sh").exists()

def test_checkout_verbose():
    """
    check if --verbose option works
    """
    create_checkout_script.checkout_create(YAMLFILE,PLATFORM,TARGET,False,False, False,True)

def test_checkout_execute():
    """
    check if --execute option works
    """
    subprocess.run(["rm","-rf",f"{OUT}/fremake_canopy/test"])
    create_checkout_script.checkout_create(YAMLFILE,PLATFORM,TARGET,False,False, True,False)
