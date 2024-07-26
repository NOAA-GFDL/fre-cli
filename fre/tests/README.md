note- this directory is for unit tests assessing `fre` functionality, and NOT for code corresponding to the command `fre test`

to run the tests as intended, simply call `pytest` from the root directory of this repository.

From the root directory of this repository, if you want to...

Invoke all tests (intended use):
    `pytest fre/tests/`

Invoke all tests in a single file: 
    `pytest fre/tests/test_fre_cli.py`
    
Invoke a single test in a file: 
    `pytest fre/tests/test_fre_cli.py::test_cli_fre_option_dne`


Note that pytest will not print stdout from individual tests. If you want to...

Print stdout from an invoked test (debugging with print statements):
    `pytest fre/tests/test_fre_cli.py::test_cli_fre_option_dne -s`
