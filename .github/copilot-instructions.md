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

**Run core CLI tests**:
```bash
pytest fre/tests/test_fre_cli.py -v
```
- Takes approximately 1 second
- Should pass all 5 tests

**Run full test suite**:
```bash
pytest fre/tests/ -v --tb=short --disable-warnings
```
- Takes approximately 3 seconds
- NEVER CANCEL: Set timeout to 30+ minutes
- Expect 110+ tests to pass, 2-3 may be skipped, some CMOR tests may fail (this is normal)

**Run specific test file**:
```bash
pytest fre/tests/test_fre_[TOOL]_cli.py -v
```

**Run single test with output**:
```bash
pytest fre/tests/test_fre_cli.py::test_cli_fre_help -s
```

## Validation

**Always run these validation steps before committing:**

1. **Run pylint** (required for CI):
   ```bash
   pylint fre/fre.py --disable=all --enable=C0103,C0301,W0611
   ```
   - May show line length warnings (normal)

2. **Test CLI functionality**:
   ```bash
   fre --version  # Should show: fre, version 2025.04
   fre --help     # Should show all available commands
   ```

3. **ALWAYS test the main CLI entry point** after making changes:
   ```bash
   fre --help
   fre [your-tool] --help
   ```

## CLI Usage Patterns

**Main command structure**: `fre [tool] [sub-command] [options]`

**Available tools**:
- `analysis` - Analysis subcommands
- `app` - Application subcommands (regrid, remap, generate time averages)
- `catalog` - Catalog building and management
- `check` - Validation checks (not fully implemented)
- `cmor` - CMOR processing
- `list` - List experiments, platforms, components
- `make` - Build system integration
- `pp` - Post-processing tools
- `run` - Run management (not fully implemented) 
- `yamltools` - YAML manipulation and combination

**Example usage scenarios to test**:
```bash
# List available subcommands for a tool
fre list --help
fre yamltools --help

# Test YAML tools functionality
fre yamltools combine-yamls --help

# Test app functionality
fre app --help
fre app regrid --help
```

## Common Issues and Workarounds

**YAML validation failures**: 
- Many test YAML files may fail validation due to strict schema requirements
- This is expected behavior - the validation is working correctly
- Do NOT disable validation to "fix" test failures

**CMOR test failures**:
- Some CMOR tests may fail due to missing test data files
- This is known and acceptable - focus on CLI functionality tests

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
- `publish_conda.yml` - Publishes to noaa-gfdl channel on main
- Tests run automatically - ensure local tests pass first

**Conda build** (for advanced users):
```bash
conda install conda-build conda-verify
conda build .
```
- NEVER CANCEL: Can take 60+ minutes
- Set timeout to 90+ minutes

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
- **Conda build**: 60+ minutes (if needed)

**CRITICAL**: NEVER CANCEL long-running operations. The timing estimates include appropriate buffers.