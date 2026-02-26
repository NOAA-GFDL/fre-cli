"""
Test fre make checkout-script
"""
from pathlib import Path
import shutil
from fre.make import create_checkout_script

# Set example yaml paths, input directory
TEST_DIR = str(Path("fre/make/tests"))
YAMLFILE = str(Path(f"{TEST_DIR}/null_example/null_model.yaml"))

# Set platform and target
PLATFORM = ["ci.gnu"]
CONTAINER_PLATFORM = ["hpcme.2023"]
TARGET = ["debug"]

# Set output directory
OUT = f"{TEST_DIR}/checkout_out"

# Set expected line that should be in checkout script
EXPECTED_LINE = "git clone --recursive --jobs=2 https://github.com/NOAA-GFDL/FMS.git -b foo3 FMS"

def test_nullyaml_exists():
    """
    Make sure combined yaml file exists
    """
    assert Path(f"{YAMLFILE}").exists()

def test_nullyaml_filled():
    """
    Make sure null.yaml is not an empty file
    """
    with open(YAMLFILE,'r') as f:
        assert sum(1 for _ in f) >1

def test_checkout_script_exists(monkeypatch):
    """
    Test checkout-script was successful and that file exists.
    Also checks that the default behavior is a parallel checkout.
    """
    # Set output directory as home for fre make output
    monkeypatch.setenv("TEST_BUILD_DIR", OUT)

    shutil.rmtree(f"{OUT}/fremake_canopy/test", ignore_errors=True)
    create_checkout_script.checkout_create(YAMLFILE,
                                           PLATFORM,
                                           TARGET,
                                           no_parallel_checkout = False,
                                           njobs = 2,
                                           execute = False,
                                           force_checkout = False)
    #assert result.exit_code == 0
    assert Path(f"{OUT}/fremake_canopy/test/null_model_full/src/checkout.sh").exists()

    # A parallel checkout is done by default - check for subshells (parallelism in script)
    expected_line = f"({EXPECTED_LINE}) &"
    with open(f"{OUT}/fremake_canopy/test/null_model_full/src/checkout.sh", 'r') as f1:
        content = f1.read()
    assert expected_line in content

def test_checkout_execute(monkeypatch):
    """
    check if --execute option works
    """
    # Set output directory as home for fre make output
    monkeypatch.setenv("TEST_BUILD_DIR", OUT)

    shutil.rmtree(f"{OUT}/fremake_canopy/test", ignore_errors=True)
    create_checkout_script.checkout_create(YAMLFILE,
                                           PLATFORM,
                                           TARGET,
                                           no_parallel_checkout = False,
                                           njobs = 2,
                                           execute = True,
                                           force_checkout = False)

    # Check for checkout script and for some resulting folders from running the script
    assert all([Path(f"{OUT}/fremake_canopy/test/null_model_full/src/checkout.sh").exists(),
                Path(f"{OUT}/fremake_canopy/test/null_model_full/src/FMS").is_dir(),
                any(Path(f"{OUT}/fremake_canopy/test/null_model_full/src/FMS").iterdir()),
                Path(f"{OUT}/fremake_canopy/test/null_model_full/src/coupler").is_dir(),
                any(Path(f"{OUT}/fremake_canopy/test/null_model_full/src/coupler").iterdir())])

def test_checkout_no_parallel_checkout(monkeypatch):
    """
    check if --no_parallel_checkout option works
    """
    # Set output directory as home for fre make output
    monkeypatch.setenv("TEST_BUILD_DIR", OUT)

    shutil.rmtree(f"{OUT}/fremake_canopy/test", ignore_errors=True)
    create_checkout_script.checkout_create(YAMLFILE,
                                           PLATFORM,
                                           TARGET,
                                           no_parallel_checkout = True,
                                           njobs = 2,
                                           execute = False,
                                           force_checkout = False)
    assert Path(f"{OUT}/fremake_canopy/test/null_model_full/src/checkout.sh").exists()

    expected_line = EXPECTED_LINE
    with open(f"{OUT}/fremake_canopy/test/null_model_full/src/checkout.sh", 'r') as f:
        content = f.read()

    assert all([expected_line in content,
                "pids" not in content,
                "&" not in content])

def test_bm_checkout_force_checkout(caplog, monkeypatch):
    """
    Test re-creation of checkout script if --force-checkout is passed.
    """
    # Set output directory as home for fre make output
    monkeypatch.setenv("TEST_BUILD_DIR", OUT)

    # Remove if previously created
    shutil.rmtree(f"{OUT}/fremake_canopy/test", ignore_errors=True)

    ## Mock checkout script with some content we can check
    # Create come checkout script
    mock_checkout = Path(f"{OUT}/fremake_canopy/test/null_model_full/src")
    mock_checkout.mkdir(parents = True)

    # Write checkout
    with open(f"{mock_checkout}/checkout.sh", 'w') as f:
        f.write("mock bare-metal checkout content")

    # Check mock script was created correctly
    assert Path(f"{mock_checkout}/checkout.sh").exists()
    # Check mock content
    with open(f"{mock_checkout}/checkout.sh", 'r') as f:
        assert f.read() == "mock bare-metal checkout content"

    # Re-create checkout script
    create_checkout_script.checkout_create(YAMLFILE,
                                           PLATFORM,
                                           TARGET,
                                           no_parallel_checkout = False,
                                           njobs = 2,
                                           execute = False,
                                           force_checkout = True)

    # Check it exists, check output, check content
    assert all([Path(f"{OUT}/fremake_canopy/test/null_model_full/src/checkout.sh").exists(),
                "Checkout script PREVIOUSLY created" in caplog.text,
                "*** REMOVING CHECKOUT SCRIPT ***" in caplog.text,
                "Checkout script created" in caplog.text])

    # Check one expected line is now populating the re-created checkout script
    expected_line = f"({EXPECTED_LINE}) &"

    with open(f"{OUT}/fremake_canopy/test/null_model_full/src/checkout.sh", 'r') as f2:
        content = f2.read()

    assert all([expected_line in content,
                "pids" in content,
                "mock bare-metal checkout content" not in content])

def test_container_checkout_force_checkout(caplog):
    """
    Test for the re-creation of the checkout script if
    --force-checkout is passed.
    """
    # Remove if previously created from a different test
    shutil.rmtree(f"./tmp/{CONTAINER_PLATFORM[0]}", ignore_errors=True)

    ## Mock checkout script with some content we can check
    # Create come checkout script
    mock_checkout = Path(f"./tmp/{CONTAINER_PLATFORM[0]}")
    mock_checkout.mkdir(parents = True)

    # Write checkout
    with open(f"{mock_checkout}/checkout.sh", 'w') as f:
        f.write("mock container checkout content")

    # Check mock script was created correctly and check content
    assert Path(f"{mock_checkout}/checkout.sh").exists()
    with open(f"{mock_checkout}/checkout.sh", 'r') as f:
        assert f.read() == "mock container checkout content"

    # Re-create checkout script
    create_checkout_script.checkout_create(YAMLFILE,
                                           CONTAINER_PLATFORM,
                                           TARGET,
                                           no_parallel_checkout = True,
                                           njobs = 2,
                                           execute = False,
                                           force_checkout = True)

    # Check it mock checkout script exists
    # Check output for script removal
    # Check output for script creation
    # Check content of re-created script
    assert all([Path(f"{mock_checkout}/checkout.sh").exists(),
                "Checkout script PREVIOUSLY created" in caplog.text,
                "*** REMOVING CHECKOUT SCRIPT ***" in caplog.text,
                "Checkout script created in ./tmp" in caplog.text])

    # Check for an expected line that should be populating the re-created checkout script
    # Check no parenthesis (no parallel checkouts)
    # Check content did not just append (no previous content)

    expected_line = EXPECTED_LINE
    with open(f"./tmp/{CONTAINER_PLATFORM[0]}/checkout.sh", "r") as f2:
        content = f2.read()

    assert all([expected_line in content,
               "pids" not in content,
               "mock container checkout content" not in content])

##test checkout w/o force but if it already exists
