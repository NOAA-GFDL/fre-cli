# FRE-CLI Development Instructions

**ALWAYS** follow these instructions first and fallback to additional search and context gathering only if the 
information in these instructions is incomplete or found to be in error.

## Working Effectively

**Conda setup, Code Initialization, Env Creation, Activation, and Install**

1. **Configure conda channels** (required for all dependencies):
   ```bash
   conda config --append channels noaa-gfdl
   conda config --append channels conda-forge
   ```
   - requirements must be obtained through the `conda-forge` or `noaa-gfdl` channels

2. **Initialize git submodules** (essential - contains mkmf tools):
   ```bash
   git submodule update --init --recursive
   ```
   - Takes roughly 10 seconds or less
   - NEVER CANCEL: Wait for completion

3. **Create conda environment**:
   ```bash
   conda env create -f environment.yml
   ```
   - Takes approximately 2 - 3 minutes
   - NEVER CANCEL: Set timeout to 10+ minutes
   - Creates environment named `fre-cli`

4. **Activate environment and add mkmf to PATH**:
   ```bash
   source $(conda info --base)/etc/profile.d/conda.sh
   conda activate fre-cli
   export PATH=$PATH:${PWD}/fre/mkmf/bin
   ```

5. **Install fre-cli in development mode**:
   ```bash
   pip install -e .
   ```
   - Takes approximately 10 - 20 seconds
   - NEVER CANCEL: Set timeout to 10+ minutes
   - The `-e` flag enables immediate reflection of code changes
   - Never run code from within the `fre/` package directory structure

## Testing Effectively

**Testing Changes to the Code**

1. **Run `click` CLI tests**:
   ```bash
   pytest -v fre/tests
   ```
   - These tests cover integration with the `click` CLI functionality
   - Takes approximately 10 seconds
   - All tests should pass, be skipped, or xfail
   - set `log-level INFO` or `DEBUG` if needed

2. **Run functionality/implementation tests**:
   ```bash
   pytest -v --ignore fre/tests fre/
   ```
   - Each tool directory contains its own test suite
   - These routines test `fre` tools and apps in a pythonic manner
   - The tests are generally for functionality independent of the `click`-based CLI
   - Run tool-specific tests: `pytest -v fre/[tool]/tests/`
   - Run app-specific tests `pytest -v fre/app/[app]/tests`
   - set `log-level INFO` or `DEBUG` if needed
   - if no Fortran compilers or other build tools, add `--ignore=fre/make/tests/compilation` to `pytest` call

3. **Run a specific test file**:
   ```bash
   pytest -v fre/tests/test_fre_cli.py
   ```
   - this is just an example, other test files have different names
   - explore the test directories to discover which tests to run
   - quicker than running all tests to vet small changes
   - set `log-level INFO` or `DEBUG` if needed

4. **Run single test**:
   ```bash
   pytest -v fre/tests/test_fre_cli.py::test_cli_fre_help
   ```
   - this is just an example, other test files/functions have different names
   - explore the test directories and the test files to discover which tests to run
   - some tests require a previous `setup` style test to succeed
   - tests that require a `setup` will typically fail when run in isolation
   - set `log-level INFO` or `DEBUG` if needed

5. **Run pylint**:
   ```bash
   pylint --fail-under 0.1 --max-line-length 120 --max-args 6 -ry --ignored-modules netCDF4,cmor fre/
   ```
   - targets the entire `fre/` directory for comprehensive checking
   - focus on implementing and verifying functionality first
   - address pylint complaints after your code passes all relevant tests and is functionally complete.


## CLI Usage Patterns

**Main command structure**: `fre [tool] [sub-command] [options]`

**Available tools**:
- `analysis` - Analysis subcommands
- `app` - Application subcommands (`regrid`, `remap`, `generate_time_averages`)
- `catalog` - Catalog building and management
- `check` - Validation checks (not-yet-implemented)
- `cmor` - CMOR processing
- `list` - List experiments, platforms, components
- `make` - Build system integration
- `pp` - Post-processing tools
- `run` - Run management (not-yet-implemented) 
- `yamltools` - YAML manipulation and combination

**Example usage scenarios to test**:
- each test in `fre/tests` has a CLI-equivalent call
- some tests in other places can also be reduced to CLI-equivalent calls
  - e.g. `fre/cmor/tests/test_cmor_run_subtool.py::test_fre_cmor_run_subtool_case1`
- generally lean on the `pytest` testing suite 

## Common Issues and Workarounds

**YAML validation failures**:
- Do NOT disable validation to "fix" test failures
- Instead, check if the `gfdl_msd_schemas` submodule commit is appropriate

**Environment activation issues**:
- Always use the full conda activation commands shown above
- The `export PATH` command for mkmf is required for full functionality

**Submodule issues**:
- If mkmf tools are missing, ensure submodules are initialized
- Re-run `git submodule update --init --recursive` if needed

## File Structure Knowledge

**Key directories**:
- `fre/` - Main source code directory
- `fre/tests/` - Unit tests for CLI functionality (64+ test files)
- `fre/mkmf/` - Submodule containing build tools
- `fre/gfdl_msd_schemas/` - Submodule with validation schemas
- `.github/workflows/` - CI/CD configuration

**Important files**:
- `fre/fre.py` - Main CLI entry point with lazy loading
- `pyproject.toml` - Python package configuration
- `environment.yml` - Conda environment specification
- `meta.yaml` - Conda package build configuration

**Each tool has its own directory structure**:
```
fre/[tool]/
├── __init__.py
├── fre[tool].py        # Click CLI definitions
├── [script].py         # Implementation scripts
└── README.md           # Tool-specific documentation
```

## CI/CD Integration

**GitHub Actions workflows**:
- `build_conda.yml` - Builds conda package on PRs
- `create_test_conda_env.yml` - Creates test environment and runs tests
- `publish_conda.yml` - Publishes to noaa-gfdl channel on main

**Conda build** (for advanced users):
```bash
conda install conda-build conda-verify
conda build .
```
- NEVER CANCEL: Can take approximately 10 minutes
- Set timeout to 60+ minutes

## Development Workflow

1. **Always start with environment setup** (steps above)
2. **Make minimal code changes** following existing patterns
3. **Test immediately** with relevant CLI commands
4. **Run test suite** before committing
5. **Validate with pylint** if modifying Python files
6. **Test real user scenarios** with sample YAML files. 
   - You may encounter validation errors such as missing required fields, incorrect data types, or schema mismatches. 
   - Review each error: fix the YAML file if the error is due to incorrect formatting or missing data, or update the code to handle new valid scenarios. 
   - If unsure whether an error is acceptable, consult the schema documentation or ask a team member.

## Performance Expectations

- **Environment creation**: 2-3 minutes total
- **Test suite**: Under 5 minutes  
- **CLI commands**: Nearly instantaneous
- **Package installation**: 10-15 seconds
- **Conda build**: Approximately 10 minutes (if needed)

**CRITICAL**: NEVER CANCEL long-running operations. The timing estimates include appropriate buffers.
