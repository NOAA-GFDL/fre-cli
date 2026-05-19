"""
use NOAA-GFDL/fremor
"""

import logging


fre_logger = logging.getLogger(__name__)


def cmor_config_subtool(
        pp_dir: str,
        mip_tables_dir: str,
        mip_era: str,
        exp_config: str,
        output_yaml: str,
        output_dir: str,
        varlist_dir: str,
        freq: str = 'monthly',
        chunk: str = '5yr',
        grid: str = 'g99',
        overwrite: bool = False,
        calendar_type: str = 'noleap'
):
    """
    PLACEHOLDER STUB
    """
    raise NotImplementedError('use NOAA-GFDL/fremor')
