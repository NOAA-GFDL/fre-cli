"""
Test fre.make.gfdlfremake.makefilefre linklineBuild function
Tests coverage for lines 50 and 57 which contain the fixed regex patterns
"""
import os
import tempfile
import shutil
from unittest.mock import patch, mock_open, MagicMock
from fre.make.gfdlfremake.makefilefre import linklineBuild


class MockMakefileObject:
    """
    Mock makefile object for testing linklineBuild
    """
    def __init__(self, filePath, experiment, libs):
        self.filePath = filePath
        self.e = experiment
        self.l = libs


def test_linklineBuild_container_path():
    """
    Test linklineBuild when filePath contains 'tmp' (container path).
    
    This tests line 50 which contains the fh.write() call with the sed pattern.
    """
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        # Use the actual temp_dir which contains 'tmp' to trigger container path
        container_path = os.path.join(temp_dir, "container_test")

        # Setup mock object with tmp in path (container case)
        mock_obj = MockMakefileObject(
            filePath=container_path,
            experiment="test_exp",
            libs=["lib1", "lib2"]
        )

        # Create the directory structure
        os.makedirs(mock_obj.filePath, exist_ok=True)

        # Create initial linkline.sh file
        linkline_file = os.path.join(mock_obj.filePath, "linkline.sh")
        with open(linkline_file, "w") as f:
            f.write("# Initial content\n")

        # Call the function
        linklineBuild(mock_obj)

        # Verify that the linkline.sh file was updated with the expected content
        with open(linkline_file, "r") as f:
            content = f.read()

        # Check that the specific line 50 regex pattern is in the file
        assert "sed -i 's|\\($^\\) \\($(LDFLAGS)\\)|\\1 $(LL) \\2|' $MF_PATH" in content
        assert "MF_PATH='/apps/test_exp/exec/Makefile'" in content
        assert 'sed -i "/MK_TEMPLATE = /a LL = $line" $MF_PATH' in content


def test_linklineBuild_baremetal_path():
    """
    Test linklineBuild when filePath does not contain 'tmp' (bare metal path)
    This tests line 57: os.system(f"sed -i 's|\\($(LDFLAGS)\\)|$(LL) \\1|' {self.filePath}/Makefile")
    """
    # Use a path that doesn't contain 'tmp' to trigger bare metal path
    baremetal_path = "/home/user/baremetal/test"

    # Setup mock object without tmp in path (bare metal case)
    mock_obj = MockMakefileObject(
        filePath=baremetal_path,
        experiment="test_exp",
        libs=["-lnetcdf", "-lhdf5"]
    )

    # Mock os.system to capture the commands that would be executed
    with patch('fre.make.gfdlfremake.makefilefre.os.system') as mock_system:
        # Call the function
        linklineBuild(mock_obj)

        # Verify that os.system was called with the expected commands
        assert mock_system.call_count == 2

        # Check the first call (adding LL variable)
        first_call = mock_system.call_args_list[0][0][0]
        assert f"sed -i '/MK_TEMPLATE = /a LL =  -lnetcdf -lhdf5' {baremetal_path}/Makefile" == first_call

        # Check the second call (line 57 - the regex pattern we fixed)
        second_call = mock_system.call_args_list[1][0][0]
        assert f"sed -i 's|\\($(LDFLAGS)\\)|$(LL) \\1|' {baremetal_path}/Makefile" == second_call


def test_linklineBuild_container_path_no_libs():
    """
    Test linklineBuild container path with empty libs list
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        # Use the actual temp_dir which contains 'tmp' to trigger container path
        container_path = os.path.join(temp_dir, "container_test")

        mock_obj = MockMakefileObject(
            filePath=container_path,
            experiment="test_exp",
            libs=[]
        )

        os.makedirs(mock_obj.filePath, exist_ok=True)
        linkline_file = os.path.join(mock_obj.filePath, "linkline.sh")
        with open(linkline_file, "w") as f:
            f.write("# Initial content\n")

        # Call the function
        linklineBuild(mock_obj)

        # Verify that the file was still created with the regex patterns
        with open(linkline_file, "r") as f:
            content = f.read()

        assert "sed -i 's|\\($^\\) \\($(LDFLAGS)\\)|\\1 $(LL) \\2|' $MF_PATH" in content


def test_linklineBuild_baremetal_path_no_libs():
    """
    Test linklineBuild bare metal path with empty libs list
    """
    # Use a path that doesn't contain 'tmp' to trigger bare metal path
    baremetal_path = "/home/user/baremetal/test"

    mock_obj = MockMakefileObject(
        filePath=baremetal_path,
        experiment="test_exp",
        libs=[]
    )

    # Mock os.system to capture commands
    with patch('fre.make.gfdlfremake.makefilefre.os.system') as mock_system:
        linklineBuild(mock_obj)

        # Should still call the sed commands even with empty libs
        assert mock_system.call_count == 2

        # Check the first call (adding LL variable with empty linkline)
        first_call = mock_system.call_args_list[0][0][0]
        assert f"sed -i '/MK_TEMPLATE = /a LL = ' {baremetal_path}/Makefile" == first_call

        # Check the second call (line 57 - the regex pattern we fixed)
        second_call = mock_system.call_args_list[1][0][0]
        assert f"sed -i 's|\\($(LDFLAGS)\\)|$(LL) \\1|' {baremetal_path}/Makefile" == second_call
