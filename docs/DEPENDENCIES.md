# fre-cli Dependencies Reference

This document describes the dependencies required for `fre-cli` and provides guidance on version requirements and optional dependencies.

## Core Dependencies

### Python
- **Requirement:** >= 3.11
- **Tested versions:** 3.11, 3.12
- **Notes:** As of the 2025.04 release cycle, Python 3.11 and 3.12 are officially supported

### CMOR (Climate Model Output Rewriter)
- **Requirement:** >= 3.14
- **Channel:** conda-forge
- **Notes:** Upgraded from 3.11 to access latest features from PCMDI/cmor. See <a href="https://github.com/PCMDI/cmor/releases">PCMDI/cmor releases</a> for details

### Core Python Packages
- **click** >= 8.2
- **numpy** == 1.26.4 (pinned for stability)
- **netcdf4** >= 1.7.*
- **xarray** >= 2024.*
- **pyyaml**
- **cftime**
- **jinja2** >= 3

### Build Dependencies
- **python** >= 3.11
- **pip**
- **setuptools**
- **wheel**

## Optional External Dependencies

### fre-nctools (fregrid)
**Required for:** `fre app regrid_xy`

`fregrid` is **no longer bundled** as a package dependency. It must be loaded separately.

**Installation options:**

1. **On GFDL/Gaea systems** (recommended):
   ```bash
   module load fre-nctools
   ```

2. **Via conda:**
   ```bash
   conda install -c noaa-gfdl fre-nctools
   ```

**Testing behavior:**
- Tests requiring fregrid will be automatically skipped if not available
- Skip message: `"fregrid not in env. it was removed from package reqs. you must load it externally"`

**Verification:**
```bash
which fregrid
```

## Workflow-Specific Dependencies

### Cylc/Rose Workflows
- **cylc-flow** >= 8.2
- **cylc-rose**
- **metomi-rose**

### Post-Processing
- **CDO** (Climate Data Operators) >= 2
- **nccmp** (for netCDF comparison)
- **python-cdo**

### Analysis
- **analysis_scripts** == 0.0.1 (noaa-gfdl channel)

### Cataloging
- **catalogbuilder** == 2025.01.01 (noaa-gfdl channel)

## Development Dependencies

### Testing
- **pytest**
- **pytest-cov**

### Code Quality
- **pylint**

## Migration Notes

### Upgrading from Previous Versions

**If upgrading from versions with Python 3.11.*** 
- Python >= 3.11 is now supported (not pinned to 3.11.*)
- You can use Python 3.12 or later 3.11.x versions

**If upgrading from versions with CMOR 3.11:**
- CMOR >= 3.14 is now required
- Update your environment: `conda update cmor`

**If you use `fre app regrid_xy`:**
- `fregrid` is no longer automatically available
- Load fre-nctools separately before using regrid_xy
- Add `module load fre-nctools` to your workflow scripts

## Troubleshooting

### "fregrid: command not found"
**Cause:** fregrid is not in your PATH  
**Solution:** Load fre-nctools module or install it separately (see above)

### CMOR version errors
**Cause:** CMOR version < 3.14  
**Solution:** Update CMOR: `conda update -c conda-forge cmor`

### Python version incompatibility
**Cause:** Python version < 3.11  
**Solution:** Create new environment with Python >= 3.11:
```bash
conda create -n fre-cli-env python=3.12
conda activate fre-cli-env
conda install -c noaa-gfdl fre-cli
```

## References
- <a href="https://github.com/PCMDI/cmor">PCMDI/cmor</a>
- <a href="https://anaconda.org/NOAA-GFDL">NOAA-GFDL conda channel</a>
- <a href="https://noaa-gfdl.readthedocs.io/projects/fre-cli/en/latest/">fre-cli documentation</a>
