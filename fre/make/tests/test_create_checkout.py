"""
Test fre make checkout-script
"""
import shutil
from pathlib import Path

from fre.make import create_checkout_script

# Set example yaml paths, input directory — use __file__ so tests work from any cwd
TEST_DIR = str(Path(__file__).resolve().parent)
YAMLFILE = str(Path(f"{TEST_DIR}/null_example/null_model.yaml"))

# Set platform and target
PLATFORM = ["ci.gnu"]
CONTAINER_PLATFORM = ["hpcme.2023"]
TARGET = ["debug"]

# Set output directory
OUT = f"{TEST_DIR}/checkout_out"

# Set expected line that should be in checkout script
EXPECTED_LINE = "git clone --recursive --jobs=2 https://github.com/NOAA-GFDL/FMS.git -b 2025.04 FMS"

# Common path for checkout script and cloned source
SRC_DIR = f"{OUT}/fremake_canopy/test/null_model_full/src"

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
        assert sum(1 for _ in f) > 1

def test_checkout_script_exists(checkout_out):
    """
    Test checkout-script was successful and that file exists.
    Also checks that the default behavior is a parallel checkout.
    """
    create_checkout_script.checkout_create(YAMLFILE,
                                           PLATFORM,
                                           TARGET,
                                           no_parallel_checkout = False,
                                           njobs = 2,
                                           execute = False,
                                           force_checkout = False)
    assert Path(f"{SRC_DIR}/checkout.sh").exists()

    # A parallel checkout is done by default - check for subshells (parallelism in script)
    expected_line = f"({EXPECTED_LINE}) &"
    with open(f"{SRC_DIR}/checkout.sh", 'r') as f1:
        content = f1.read()
    assert expected_line in content

def test_checkout_execute(checkout_out):
    """
    Check if --execute option works.

    Uses no_parallel_checkout to avoid shell-backgrounding race conditions
    that can cause flaky failures. The parallel checkout syntax is already
    covered by test_checkout_script_exists.
    """
    create_checkout_script.checkout_create(YAMLFILE,
                                           PLATFORM,
                                           TARGET,
                                           no_parallel_checkout = True,
                                           njobs = 2,
                                           execute = True,
                                           force_checkout = False)

    # Check for checkout script and for some resulting folders from running the script.
    # Individual assertions give better diagnostics on failure than assert all([...]).
    assert Path(f"{SRC_DIR}/checkout.sh").exists(), \
        "checkout.sh was not created"
    assert Path(f"{SRC_DIR}/FMS").is_dir(), \
        "FMS directory was not created by checkout execution"
    assert any(Path(f"{SRC_DIR}/FMS").iterdir()), \
        "FMS directory is empty after checkout execution"
    assert Path(f"{SRC_DIR}/coupler").is_dir(), \
        "coupler directory was not created by checkout execution"
    assert any(Path(f"{SRC_DIR}/coupler").iterdir()), \
        "coupler directory is empty after checkout execution"

def test_checkout_no_parallel_checkout(checkout_out):
    """
    Check if --no_parallel_checkout option works
    """
    create_checkout_script.checkout_create(YAMLFILE,
                                           PLATFORM,
                                           TARGET,
                                           no_parallel_checkout = True,
                                           njobs = 2,
                                           execute = False,
                                           force_checkout = False)
    assert Path(f"{SRC_DIR}/checkout.sh").exists()

    expected_line = EXPECTED_LINE
    with open(f"{SRC_DIR}/checkout.sh", 'r') as f:
        content = f.read()

    assert expected_line in content
    assert "pids" not in content
    assert "&" not in content

def test_bm_checkout_force_checkout(caplog, checkout_out):
    """
    Test re-creation of checkout script if --force-checkout is passed.
    """
    ## Mock checkout script with some content we can check
    mock_checkout = Path(f"{SRC_DIR}")
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
    assert Path(f"{SRC_DIR}/checkout.sh").exists()
    assert "Checkout script PREVIOUSLY created" in caplog.text
    assert "*** REMOVING CHECKOUT SCRIPT ***" in caplog.text
    assert "Checkout script created" in caplog.text

    # Check one expected line is now populating the re-created checkout script
    expected_line = f"({EXPECTED_LINE}) &"

    with open(f"{SRC_DIR}/checkout.sh", 'r') as f2:
        content = f2.read()

    assert expected_line in content
    assert "pids" in content
    assert "mock bare-metal checkout content" not in content

def test_container_checkout_force_checkout(caplog):
    """
    Test for the re-creation of the checkout script if
    --force-checkout is passed.
    """
    # Remove if previously created from a different test
    shutil.rmtree(f"./tmp/{CONTAINER_PLATFORM[0]}", ignore_errors=True)

    ## Mock checkout script with some content we can check
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

    # Check mock checkout script exists and output messages
    assert Path(f"{mock_checkout}/checkout.sh").exists()
    assert "Checkout script PREVIOUSLY created" in caplog.text
    assert "*** REMOVING CHECKOUT SCRIPT ***" in caplog.text
    assert "Checkout script created in ./tmp" in caplog.text

    # Check for an expected line that should be populating the re-created checkout script
    # Check no parenthesis (no parallel checkouts)
    # Check content did not just append (no previous content)

    expected_line = EXPECTED_LINE
    with open(f"./tmp/{CONTAINER_PLATFORM[0]}/checkout.sh", "r") as f2:
        content = f2.read()

    assert expected_line in content
    assert "pids" not in content
    assert "mock container checkout content" not in content

##test checkout w/o force but if it already exists
