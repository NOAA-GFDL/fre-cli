"""
fre.cmor constants
==================

Centralized constants for the ``fre cmor`` subpackage.  Every hard-coded
value that was previously scattered across ``cmor_mixer``, ``cmor_helpers``,
``cmor_config``, ``cmor_finder``, and ``cmor_yamler`` now lives here so that
each module imports from a single, transparent location.

Sections
--------
- **Vertical-coordinate classification** – lists that partition the accepted
  vertical dimension names into physical categories.
- **CMOR module defaults** – arguments passed to ``cmor.setup()``.
- **CMIP7 brand disambiguation** – mapping from input netCDF vertical
  dimension names to MIP-table dimension names.
- **Archive / filesystem paths** – locations of gold-standard data sets.
- **MIP-table filtering** – suffixes used to exclude non-variable-entry
  tables when scanning a MIP-tables directory.
- **Output / display flags** – behavioural toggles for CLI and finder output.
"""

import cmor


# ---------------------------------------------------------------------------
# Vertical-coordinate classification (used by cmor_mixer)
# ---------------------------------------------------------------------------
ACCEPTED_VERT_DIMS = [
    "z_l", "landuse",
    "plev39", "plev30", "plev19", "plev8",
    "height2m",
    "level", "lev", "levhalf",
]

NON_HYBRID_SIGMA_COORDS = [
    "landuse",
    "plev39", "plev30", "plev19", "plev8",
    "height2m",
]

ALT_HYBRID_SIGMA_COORDS = ["level", "lev", "levhalf"]

DEPTH_COORDS = ["z_l"]


# ---------------------------------------------------------------------------
# CMOR module defaults (passed to cmor.setup in cmor_mixer)
# ---------------------------------------------------------------------------
CMOR_NC_FILE_ACTION = cmor.CMOR_REPLACE
CMOR_VERBOSITY      = cmor.CMOR_NORMAL
CMOR_EXIT_CTL       = cmor.CMOR_NORMAL
CMOR_MK_SUBDIRS     = 1
CMOR_LOG             = None


# ---------------------------------------------------------------------------
# CMIP7 brand disambiguation (used by cmor_helpers.filter_brands)
# ---------------------------------------------------------------------------
# Maps input netCDF vertical dimension names to their CMIP7 MIP-table
# equivalents.  Dimensions whose names already match (e.g. plev39, height2m)
# need no entry; the look-up falls back to using the input name directly.
INPUT_TO_MIP_VERT_DIM = {
    "z_l":      "olevel",
    "level":    "alevel",
    "lev":      "alevel",
    "levhalf":  "alevhalf",
}


# ---------------------------------------------------------------------------
# Archive / filesystem paths (used by cmor_helpers)
# ---------------------------------------------------------------------------
ARCHIVE_GOLD_DATA_DIR = '/archive/gold/datasets'
CMIP7_GOLD_OCEAN_FILE_STUB='OM5_025/ocean_mosaic_v20250916_unpacked/ocean_static.nc'
CMIP6_GOLD_OCEAN_FILE_STUB=None #TODO

# ---------------------------------------------------------------------------
# MIP-table filtering (used by cmor_config)
# ---------------------------------------------------------------------------
# Table-file suffixes to exclude when scanning a MIP-tables directory for
# variable-entry tables.
EXCLUDED_TABLE_SUFFIXES = [
    'long_name_overrides',
    'grids',
    'formula_terms',
    'coordinate',
    'cell_measures',
]


# ---------------------------------------------------------------------------
# Output / display flags
# ---------------------------------------------------------------------------
# cmor_finder: variable-entry keys to suppress when printing variable info.
DO_NOT_PRINT_LIST = [
    'comment',
    'ok_min_mean_abs', 'ok_max_mean_abs',
    'valid_min', 'valid_max',
]
