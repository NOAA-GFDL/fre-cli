"""
use NOAA-GFDL/fremor
"""

import logging

fre_logger = logging.getLogger(__name__)

def cmor_run_subtool(indir: str = None,
                     json_var_list: str = None,
                     json_table_config: str = None,
                     json_exp_config: str = None,
                     outdir: str = None,
                     run_one_mode: Optional[bool] = False,
                     opt_var_name: Optional[str] = None,
                     grid: Optional[str] = None,
                     grid_label: Optional[str] = None,
                     nom_res: Optional[str] = None,
                     start: Optional[str] = None,
                     stop: Optional[str] = None,
                     calendar_type: Optional[str] = None) -> int:
    """
    PLACEHOLDER STUB
    """
    raise NotImplementedError('use NOAA-GFDL/fremor')
