# FRE-CLI Development Instructions

**ALWAYS** follow these instructions first and fallback to additional search and context gathering only if the 
information in these instructions is incomplete or found to be in error.

## Essential Setup

**Quick Development Environment Setup**

1. **Configure conda channels**:
   ```bash
   conda config --append channels noaa-gfdl
   conda config --append channels conda-forge
   ```

2. **Initialize git submodules** (essential - contains mkmf tools):
   ```bash
   git submodule update --init --recursive
   ```
   - NEVER CANCEL: Wait for completion

3. **Create conda environment**:
   ```bash
   conda env create -f environment.yml
   ```
   - NEVER CANCEL: Set timeout to 10+ minutes

4. **Activate environment and install**:
   ```bash
   source $(conda info --base)/etc/profile.d/conda.sh
   conda activate fre-cli
   export PATH=$PATH:${PWD}/fre/mkmf/bin
   pip install -e .
   ```

## Testing

**Core test commands**:
```bash
# CLI tests
pytest -v fre/tests

# Tool/app tests  
pytest -v --ignore fre/tests fre/

# Specific tests
pytest -v fre/[tool]/tests/
pytest -v fre/app/[app]/tests/

# Code quality
pylint --fail-under 0.1 --max-line-length 120 --max-args 6 -ry --ignored-modules netCDF4,cmor fre/
```

**Critical notes**:
- All tests should pass, be skipped, or marked xfail
- No Fortran compilers: add `--ignore=fre/make/tests/compilation`
- NEVER CANCEL: Set timeout to 10+ minutes for test suites


## CLI Structure

**Command pattern**: `fre [tool] [sub-command] [options]`

**Available tools**: `analysis`, `app`, `catalog`, `check`, `cmor`, `list`, `make`, `pp`, `run`, `yamltools`

## Critical Notes

**YAML validation failures**:
- Do NOT disable validation to "fix" test failures
- Check if `gfdl_msd_schemas` submodule commit is appropriate

**Submodule dependency**: 
- If mkmf tools missing: `git submodule update --init --recursive`

**NEVER CANCEL operations**: Environment creation, test suites, conda builds
