# FRE-CLI Development Instructions

**ALWAYS** follow these instructions first and fallback to additional search and context gathering only if the information in these instructions is incomplete or found to be in error.

## Working Effectively

**Bootstrap, build, and test the repository:**

1. **Configure conda channels** (required for all dependencies):
   ```bash
   conda config --append channels noaa-gfdl
   conda config --append channels conda-forge
   ```

2. **Initialize git submodules** (essential - contains mkmf tools):
   ```bash
   git submodule update --init --recursive
   ```
   - Takes approximately 6 seconds
   - NEVER CANCEL: Wait for completion

3. **Create conda environment**:
   ```bash
   conda env create -f environment.yml
   ```
   - Takes approximately 2 minutes 20 seconds
   - NEVER CANCEL: Set timeout to 10+ minutes
   - Creates environment named `fre-cli` with Python 3.11

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
   - Takes approximately 13 seconds
   - NEVER CANCEL: Set timeout to 10+ minutes
   - The `-e` flag enables immediate reflection of code changes

## Testing

**Run `click` CLI tests**:
```bash
pytest -v fre/tests
```
- These tests cover integration with the `click` CLI functionality
- Takes approximately 10 seconds
- All tests should pass, be skipped, or xfail

**Run functionality/implementation tests**:
```bash
pytest -v --ignore fre/tests fre/
```
- Each tool directory contains its own test suite
- These tests avoid `click` CLI functionality and test `fre/` in a pythonic manner
- Tests for tools are in `fre/*/tests/` and `fre/app/*/tests/`
- The tests are generally for functionality of certain function calls
- Run tool-specific tests: `pytest -v fre/[tool]/tests/` or `pytest -v fre/app/[tool]/tests`

**Run specific test file**:
```bash
pytest -v fre/tests/test_fre_[TOOL]_cli.py -v
```
Note: Not all test files follow this exact pattern - explore the test directories for actual file names.

**Run single test with output**:
```bash
pytest fre/tests/test_fre_cli.py::test_cli_fre_help -s
```
Note: Like above, not all test files and test names file this exact pattern - this is only an example.

## Validation

**Always run these validation steps before committing:**

1. **Run pylint** (required for CI):
   ```bash
   pylint fre/ --disable=all --enable=C0103,C0301,W0611
   ```
   - May show line length warnings (normal)
   - Targets the entire fre/ directory for comprehensive checking

2. **Test CLI functionality**:
   ```bash
   pytest -v fre/tests
   ```

3. **Test CLI by hand** after making changes:
   ```bash
   fre --help
   fre [tool] --help
   fre app [tool] --help
   ```

## CLI Usage Patterns

**Main command structure**: `fre [tool] [sub-command] [options]`

**Available tools**:
- `analysis` - Analysis subcommands
- `app` - Application subcommands (`regrid`, `remap`, `generate_time_averages`)
- `catalog` - Catalog building and management
- `check` - Validation checks (not fully implemented)
- `cmor` - CMOR processing
- `list` - List experiments, platforms, components
- `make` - Build system integration
- `pp` - Post-processing tools
- `run` - Run management (not fully implemented) 
- `yamltools` - YAML manipulation and combination

**Example usage scenarios to test**:
- each test in `fre/tests` has a CLI-equivalent call
- some tests in other places can also be reduced to CLI-equivalent calls
  - e.g. `fre/cmor/tests/test_cmor_run_subtool.py::test_fre_cmor_run_subtool_case1`
- generally lean on the `pytest` testing suite 

## Common Issues and Workarounds

**YAML validation failures**: 
- Many test YAML files may fail validation due to strict schema requirements
- This is expected behavior - the validation is working correctly
- Do NOT disable validation to "fix" test failures

**CMOR test expectations**:
- CMOR tests that do not succeed in the pipeline are marked as being skipped
- This is expected behavior - the validation is working correctly
- This is changing soon

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
- Tests run automatically - ensure local tests pass first

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
6. **Test real user scenarios** with sample YAML files (expect some validation errors)

## Performance Expectations

- **Environment creation**: 2-3 minutes total
- **Test suite**: Under 5 minutes  
- **CLI commands**: Nearly instantaneous
- **Package installation**: 10-15 seconds
- **Conda build**: Approximately 10 minutes (if needed)

**CRITICAL**: NEVER CANCEL long-running operations. The timing estimates include appropriate buffers.
