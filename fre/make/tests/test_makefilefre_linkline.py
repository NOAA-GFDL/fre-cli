"""
Test fre.make.gfdlfremake.makefilefre link_line_build function
Tests coverage for lines 50 and 57 which contain the fixed regex patterns
"""
import os
import tempfile
from pathlib import Path
from unittest.mock import patch
from fre.make.gfdlfremake.makefilefre import link_line_build

class MockMakefileObject:
    """
    Mock makefile object for testing link_line_build
    """
    def __init__(self, file_path, experiment, clibs, bm_linkerflags, container_linkerflags):
        self.filepath = file_path
        self.e = experiment
        self.clibs = clibs
        self.bmlf = bm_linkerflags
        self.clf = container_linkerflags

def test_linklinebuild_container_path():
    """
    Test link_line_build when file_path contains 'tmp' (container path).
    This tests line 50 which contains the fh.write() call with the sed pattern.
    """
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        # Use the actual temp_dir which contains 'tmp' to trigger container path
        container_path = os.path.join(temp_dir, "container_test")

        # Setup mock object with tmp in path (container case)
        mock_obj = MockMakefileObject(
            file_path=container_path,
            experiment="test_exp",
            clibs=["lib1", "lib2"],
            bm_linkerflags=[],
            container_linkerflags=["-q=testing"]
        )

        # Create the directory structure
        os.makedirs(mock_obj.filepath, exist_ok=True)

        # Create initial linkline.sh file
        linkline_file = os.path.join(mock_obj.filepath, "linkline.sh")
        with open(linkline_file, "w") as f:
            f.write("# Initial content\n")

        # Call the function
        link_line_build(mock_obj)

        # Verify that the linkline.sh file was updated with the expected content
        with open(linkline_file, "r") as f:
            content = f.read()

        # Check that the specific line 50 regex pattern is in the file
        assert "sed -i 's|\\($(CLF)\\) \\($(LDFLAGS)\\)|\\1 $(CLIBS) \\2|' $MF_PATH" in content
        assert "MF_PATH='/apps/test_exp/exec/Makefile'" in content
        assert 'sed -i "/MK_TEMPLATE = /a CLIBS = $line" $MF_PATH' in content

def test_linklinebuild_baremetal_path():
    """
    Test link_line_build when file_path does not contain 'tmp' (bare metal path)
    This tests line 57: os.system(f"sed -i 's|\\($(LDFLAGS)\\)|$(LL) \\1|' {self.filepath}/Makefile")
    """
    # Use a path that doesn't contain 'tmp' to trigger bare metal path
    baremetal_path = "/home/user/baremetal/test"

    # Setup mock object without tmp in path (bare metal case)
    mock_obj = MockMakefileObject(
        file_path=baremetal_path,
        experiment="test_exp",
        clibs=[],
        bm_linkerflags=["-lnetcdf", "-lhdf5"],
        container_linkerflags=[]
    )

    # Mock os.system to capture the commands that would be executed
    with patch('fre.make.gfdlfremake.makefilefre.os.system') as mock_system:
        # Call the function
        link_line_build(mock_obj)

        # Verify that os.system was called with the expected commands
        assert mock_system.call_count == 2

        # Check the first call (adding LL variable)
        first_call = mock_system.call_args_list[0][0][0]
        assert f"sed -i '/MK_TEMPLATE = /a LL =  -lnetcdf -lhdf5' {baremetal_path}/Makefile" == first_call

        # Check the second call (line 57 - the regex pattern we fixed)
        second_call = mock_system.call_args_list[1][0][0]
        assert f"sed -i 's|\\($(LDFLAGS)\\)|$(LL) \\1|' {baremetal_path}/Makefile" == second_call


def test_linklinebuild_container_path_no_libs():
    """
    Test linkline.sh script is not created if no container libraries are defined
    Test Makefile in tmp directory includes sed line
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        # Use the actual temp_dir which contains 'tmp' to trigger container path
        container_path = os.path.join(temp_dir, "container_test")

        mock_obj = MockMakefileObject(
            file_path=container_path,
            experiment="test_exp",
            clibs=[],
            bm_linkerflags=[],
            container_linkerflags=["-q=testing"]
        )

        # Mock os.system to capture commands
        with patch('fre.make.gfdlfremake.makefilefre.os.system') as mock_system:
            link_line_build(mock_obj)

            # Should still call the sed commands even with empty libs
            assert mock_system.call_count == 2

            # Check the first call (adding CLF variable)
            first_call = mock_system.call_args_list[0][0][0]
            assert f"sed -i '/MK_TEMPLATE = /a CLF = -q=testing' {container_path}/Makefile" == first_call

            # Check the second call (line 57 - the regex pattern we fixed)
            second_call = mock_system.call_args_list[1][0][0]
            assert f"sed -i 's|\\($(LDFLAGS)\\)|$(CLF) \\1|' {container_path}/Makefile" == second_call

            linkline_file = Path(f"{mock_obj.filepath}/linkline.sh")
            assert not linkline_file.exists()

def test_linklinebuild_baremetal_path_no_libs():
    """
    Test link_line_build bare metal path with empty libs list
    """
    # Use a path that doesn't contain 'tmp' to trigger bare metal path
    baremetal_path = "/home/user/baremetal/test"

    mock_obj = MockMakefileObject(
        file_path=baremetal_path,
        experiment="test_exp",
        clibs=[],
        bm_linkerflags=[],
        container_linkerflags=[]
    )

    # Mock os.system to capture commands
    with patch('fre.make.gfdlfremake.makefilefre.os.system') as mock_system:
        link_line_build(mock_obj)

        # Should still call the sed commands even with empty libs
        assert mock_system.call_count == 2

        # Check the first call (adding LL variable with empty linkline)
        first_call = mock_system.call_args_list[0][0][0]
        assert f"sed -i '/MK_TEMPLATE = /a LL = ' {baremetal_path}/Makefile" == first_call

        # Check the second call (line 57 - the regex pattern we fixed)
        second_call = mock_system.call_args_list[1][0][0]
        assert f"sed -i 's|\\($(LDFLAGS)\\)|$(LL) \\1|' {baremetal_path}/Makefile" == second_call
