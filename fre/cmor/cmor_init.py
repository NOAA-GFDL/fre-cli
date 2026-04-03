"""
CMOR Init Subtool
=================

This module powers the ``fre cmor init`` command, providing two key capabilities:

1. **Experiment config generation** – writes an empty (template) JSON experiment
   configuration file for either CMIP6 or CMIP7. The user fills in the
   placeholder values before running ``fre cmor run`` or ``fre cmor yaml``.

2. **MIP table retrieval** – fetches the official MIP tables from trusted
   GitHub repositories. By default tables are fetched via ``git clone``
   (shallow, depth 1); with ``--fast`` they are fetched as a tarball via
   ``curl`` and extracted in-place.

Trusted sources
---------------
- CMIP6: https://github.com/pcmdi/cmip6-cmor-tables
- CMIP7: https://github.com/WCRP-CMIP/cmip7-cmor-tables

Functions
---------
- ``cmor_init_subtool(...)``
"""

import json
import logging
import subprocess
import tarfile
import tempfile
from pathlib import Path

fre_logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Trusted sources for MIP tables
# ---------------------------------------------------------------------------
MIP_TABLE_REPOS = {
    'cmip6': 'https://github.com/pcmdi/cmip6-cmor-tables',
    'cmip7': 'https://github.com/WCRP-CMIP/cmip7-cmor-tables',
}


# ---------------------------------------------------------------------------
# Empty / template experiment configuration dictionaries
# ---------------------------------------------------------------------------

def _cmip6_exp_config_template():
    """Return an ordered dict-like structure for an empty CMIP6 experiment config."""
    return {
        "#note": " **** CMIP6 experiment configuration template – fill in values below ****",
        "source_type": "",
        "experiment_id": "",
        "activity_id": "",
        "sub_experiment_id": "none",
        "realization_index": "1",
        "initialization_index": "1",
        "physics_index": "1",
        "forcing_index": "1",
        "run_variant": "",
        "parent_experiment_id": "no parent",
        "parent_activity_id": "no parent",
        "parent_source_id": "no parent",
        "parent_variant_label": "no parent",
        "parent_time_units": "no parent",
        "branch_method": "no parent",
        "branch_time_in_child": 0.0,
        "branch_time_in_parent": 0.0,
        "institution_id": "",
        "source_id": "",
        "calendar": "",
        "grid": "",
        "grid_label": "",
        "nominal_resolution": "",
        "license": "",
        "outpath": "",
        "contact": "",
        "history": "",
        "comment": "",
        "references": "",
        "sub_experiment": "none",
        "institution": "",
        "source": "",
        "_controlled_vocabulary_file": "CMIP6_CV.json",
        "_AXIS_ENTRY_FILE": "CMIP6_coordinate.json",
        "_FORMULA_VAR_FILE": "CMIP6_formula_terms.json",
        "_cmip6_option": "CMIP6",
        "mip_era": "CMIP6",
        "parent_mip_era": "no parent",
        "tracking_prefix": "hdl:21.14100",
        "_history_template": (
            "%s ;rewrote data to be consistent with "
            "<activity_id> for variable <variable_id> found in table <table_id>."
        ),
        "output_path_template": (
            "<mip_era><activity_id><institution_id><source_id>"
            "<experiment_id><_member_id><table><variable_id><grid_label><version>"
        ),
        "output_file_template": (
            "<variable_id><table><source_id><experiment_id><_member_id><grid_label>"
        ),
    }


def _cmip7_exp_config_template():
    """Return an ordered dict-like structure for an empty CMIP7 experiment config."""
    return {
        "#note": " **** CMIP7 experiment configuration template – fill in values below ****",
        "contact": "",
        "comment": "",
        "license": "",
        "references": "",
        "drs_specs": "MIP-DRS7",
        "archive_id": "WCRP",
        "license_id": "CC-BY-4-0",
        "tracking_prefix": "hdl:21.14107",
        "_cmip7_option": 1,
        "mip_era": "CMIP7",
        "parent_mip_era": "CMIP7",
        "activity_id": "",
        "parent_activity_id": "",
        "institution": "",
        "institution_id": "",
        "source": "",
        "source_id": "",
        "source_type": "",
        "experiment_id": "",
        "sub_experiment": "none",
        "sub_experiment_id": "none",
        "parent_source_id": "",
        "parent_experiment_id": "",
        "realization_index": "r1",
        "initialization_index": "i1",
        "physics_index": "p1",
        "forcing_index": "f1",
        "run_variant": "",
        "parent_variant_label": "",
        "parent_time_units": "",
        "branch_method": "no parent",
        "branch_time_in_child": 0.0,
        "branch_time_in_parent": 0.0,
        "calendar": "",
        "grid": "",
        "grid_label": "",
        "frequency": "",
        "region": "",
        "nominal_resolution": "",
        "history": "",
        "_history_template": (
            "%s ;rewrote data to be consistent with "
            "<activity_id> for variable <variable_id> found in table <table_id>."
        ),
        "outpath": ".",
        "output_path_template": (
            "<activity_id><source_id><experiment_id><member_id>"
            "<variable_id><branding_suffix><grid_label><version>"
        ),
        "output_file_template": (
            "<variable_id><branding_suffix><frequency><region>"
            "<grid_label><source_id><experiment_id><variant_id>[<time_range>].nc"
        ),
        "_controlled_vocabulary_file": "../tables-cvs/cmor-cvs.json",
        "_AXIS_ENTRY_FILE": "CMIP7_coordinate.json",
        "_FORMULA_VAR_FILE": "CMIP7_formula_terms.json",
    }


# ---------------------------------------------------------------------------
# Table-fetching helpers
# ---------------------------------------------------------------------------

def _fetch_tables_git(repo_url, tables_dir, tag=None):
    """
    Clone MIP tables via ``git clone --depth 1``.

    Parameters
    ----------
    repo_url : str
        HTTPS URL of the MIP table repository.
    tables_dir : str
        Local directory to clone into.
    tag : str or None
        Optional git tag / branch to check out.
    """
    cmd = ['git', 'clone', '--depth', '1']
    if tag:
        cmd += ['--branch', tag]
    cmd += [repo_url, tables_dir]

    fre_logger.info('fetching MIP tables via git: %s', ' '.join(cmd))
    subprocess.run(cmd, check=True)
    fre_logger.info('MIP tables cloned to %s', tables_dir)


def _fetch_tables_curl(repo_url, tables_dir, tag=None):
    """
    Fetch MIP tables as a tarball via ``curl`` and extract.

    Parameters
    ----------
    repo_url : str
        HTTPS URL of the MIP table repository.
    tables_dir : str
        Local directory to extract into.
    tag : str or None
        Optional git tag / branch. Defaults to ``main`` if *None*.
    """
    ref = tag if tag else 'main'
    if tag:
        tarball_url = f'{repo_url}/archive/refs/tags/{ref}.tar.gz'
    else:
        tarball_url = f'{repo_url}/archive/refs/heads/{ref}.tar.gz'

    tables_path = Path(tables_dir)
    tables_path.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile(suffix='.tar.gz', delete=False) as tmp:
        tmp_path = tmp.name

    try:
        curl_cmd = ['curl', '-L', '-o', tmp_path, tarball_url]
        fre_logger.info('fetching MIP tables via curl: %s', ' '.join(curl_cmd))
        subprocess.run(curl_cmd, check=True)

        fre_logger.info('extracting tarball to %s', tables_dir)
        with tarfile.open(tmp_path, 'r:gz') as tar:
            tar.extractall(path=tables_dir)
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    fre_logger.info('MIP tables extracted to %s', tables_dir)


# ---------------------------------------------------------------------------
# Main subtool entry-point
# ---------------------------------------------------------------------------

def cmor_init_subtool(
        mip_era,
        exp_config=None,
        tables_dir=None,
        tag=None,
        fast=False
):
    """
    Initialise CMOR resources for the user.

    Depending on the arguments supplied this function will:

    * Write an empty experiment-configuration JSON file for the requested MIP
      era (``cmip6`` or ``cmip7``) when *exp_config* is given (or when neither
      *exp_config* nor *tables_dir* is provided — in which case a default
      filename is used).
    * Clone / download the official MIP tables into *tables_dir* when that
      argument is provided.

    Parameters
    ----------
    mip_era : str
        ``'cmip6'`` or ``'cmip7'``.
    exp_config : str or None
        Output path for the template experiment-config JSON file.
        When *None* and *tables_dir* is also *None*, a default path
        ``CMOR_<MIP_ERA>_template.json`` in the current directory is used.
    tables_dir : str or None
        Directory into which MIP tables will be fetched.
    tag : str or None
        Optional git tag / release for the MIP tables repository.
    fast : bool
        When *True*, use ``curl`` to download a tarball instead of ``git clone``.

    Returns
    -------
    dict
        A dictionary with keys ``'exp_config'`` (path written or *None*)
        and ``'tables_dir'`` (path written or *None*).
    """
    mip_era_lower = mip_era.lower()
    if mip_era_lower not in ('cmip6', 'cmip7'):
        raise ValueError(f"mip_era must be 'cmip6' or 'cmip7', got '{mip_era}'")

    result = {'exp_config': None, 'tables_dir': None}

    # -- experiment config --
    # Write config when explicitly requested OR when tables_dir is not given
    # (i.e. the user invoked `fre cmor init` without --tables_dir).
    if exp_config is not None or tables_dir is None:
        if exp_config is None:
            exp_config = f'CMOR_{mip_era_lower}_template.json'

        template_func = {
            'cmip6': _cmip6_exp_config_template,
            'cmip7': _cmip7_exp_config_template,
        }[mip_era_lower]

        config_data = template_func()

        out_path = Path(exp_config)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, 'w', encoding='utf-8') as fh:
            json.dump(config_data, fh, indent=4)
            fh.write('\n')

        fre_logger.info('wrote %s experiment config template to %s',
                        mip_era_lower.upper(), out_path)
        click_echo = f'Wrote {mip_era_lower.upper()} experiment config template to {out_path}'
        print(click_echo)
        result['exp_config'] = str(out_path)

    # -- MIP tables --
    if tables_dir is not None:
        repo_url = MIP_TABLE_REPOS[mip_era_lower]
        if fast:
            _fetch_tables_curl(repo_url, tables_dir, tag=tag)
        else:
            _fetch_tables_git(repo_url, tables_dir, tag=tag)
        result['tables_dir'] = tables_dir

    return result
