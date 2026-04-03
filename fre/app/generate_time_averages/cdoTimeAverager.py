''' stub that redirects pkg='cdo' requests to the xarray time averager '''

import logging
import warnings

from .xarrayTimeAverager import xarrayTimeAverager

fre_logger = logging.getLogger(__name__)


class cdoTimeAverager(xarrayTimeAverager):  # pylint: disable=invalid-name
    '''
    Legacy entry-point kept for backward compatibility.
    CDO/python-cdo has been removed.  All work is now done by xarrayTimeAverager.
    '''

    def generate_timavg(self, infile=None, outfile=None):
        """
        Emit a loud warning then delegate to the xarray implementation.

        :param infile: path to input NetCDF file
        :type infile: str
        :param outfile: path to output file
        :type outfile: str
        :return: 0 on success
        :rtype: int
        """
        msg = (
            "WARNING *** CDO/python-cdo has been REMOVED from fre-cli. "
            "pkg='cdo' now uses the xarray time-averager under the hood. "
            "Please switch to pkg='xarray' or pkg='fre-python-tools'. ***"
        )
        warnings.warn(msg, FutureWarning, stacklevel=2)
        fre_logger.warning(msg)
        return super().generate_timavg(infile=infile, outfile=outfile)
