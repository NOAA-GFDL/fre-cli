''' tools for generating time averages from various packages '''

import os
import logging
import time
import warnings
from typing import Optional, List, Union

import xarray as xr

from .frenctoolsTimeAverager import frenctoolsTimeAverager
from .frepytoolsTimeAverager import NumpyTimeAverager
from .xarrayTimeAverager import xarrayTimeAverager

fre_logger = logging.getLogger(__name__)

VALID_PKGS = ['cdo', 'fre-nctools', 'fre-python-tools', 'xarray']

def generate_time_average(infile: Union[str, List[str]] = None,
                          outfile: str = None,
                          pkg: str = None,
                          var: Optional[str] = None,
                          unwgt: Optional[bool] = False,
                          avg_type: Optional[str] = None   ):
    """
    steering function to various averaging functions above
    
    :param infile: path to history file, or list of paths
    :type infile: str, list
    :param outfile: path to where output file should be stored
    :type outfile: str
    :param pkg: which package to use to calculate climatology
                ('xarray', 'fre-python-tools', 'fre-nctools', or 'cdo')
                'cdo' is kept for backward compat but silently uses xarray.
    :type pkg: str
    :param var: optional, not currently supported and defaults to None
    :type var: str
    :param unwgt: optional, whether or not to weight the data, default False
    :type unwgt: bool
    :param avg_type: optional, time scale for averaging, accepts ('all','seas','month'). defaults to 'all'
    :type avg_type: str
    :return: error message if requested package unknown, otherwise returns climatology
    :rtype: int
    """
    start_time = time.perf_counter()
    fre_logger.debug('called generate_time_average')
    if None in [infile, outfile, pkg]:
        raise ValueError('infile, outfile, and pkg are required inputs')
    if pkg not in VALID_PKGS:
        raise ValueError(f'argument pkg = {pkg} not known, must be one of: {", ".join(VALID_PKGS)}')
    exitstatus = 1
    myavger = None

    # multiple files case - merge multiple files if present
    merged = False
    orig_infile_list = None
    if all ( [ type(infile).__name__ == 'list',
               len(infile) > 1 ] ) :
        fre_logger.info('list input argument detected')
        infile_str = [str(item) for item in infile]

        merged_file = "merged_output.nc"

        fre_logger.info('merging input files with xarray')
        fre_logger.debug('output: %s', merged_file)
        fre_logger.debug('inputs: \n %s', ' '.join(infile_str) )
        with xr.open_mfdataset(infile_str, combine='by_coords') as ds:
            ds.to_netcdf(merged_file)

        # preserve the original file names for later
        orig_infile_list = infile
        infile = merged_file
        merged = True
        fre_logger.info('file merging success')

    if pkg == 'cdo':
        # CDO has been removed — warn loudly, use xarray instead
        msg = (
            "WARNING *** CDO/python-cdo has been REMOVED from fre-cli. "
            "pkg='cdo' now uses the xarray time-averager under the hood. "
            "Please switch to pkg='xarray' or pkg='fre-python-tools'. ***"
        )
        warnings.warn(msg, FutureWarning, stacklevel=2)
        fre_logger.warning(msg)
        fre_logger.info('creating an xarrayTimeAverager (via pkg=cdo redirect)')
        myavger = xarrayTimeAverager( pkg = pkg,
                                      var = var,
                                      unwgt = unwgt,
                                      avg_type = avg_type )

    elif pkg == 'xarray':
        fre_logger.info('creating an xarrayTimeAverager')
        myavger = xarrayTimeAverager( pkg = pkg,
                                      var = var,
                                      unwgt = unwgt,
                                      avg_type = avg_type )

    elif pkg == 'fre-nctools':
        fre_logger.info('creating a frenctoolsTimeAverager')
        myavger = frenctoolsTimeAverager( pkg = pkg,
                                          var = var,
                                          unwgt = unwgt,
                                          avg_type = avg_type )
    elif pkg == 'fre-python-tools':
        #fre-python-tools addresses var in a unique way, which is addressed here
        if merged and var is None:
            fre_logger.warning('special variable id logic underway...')
            var = orig_infile_list[0].split('/').pop().split('.')[-2]
            fre_logger.warning('extracted var = %s from orig_infile_list[0] = %s', var, orig_infile_list[0] )

        fre_logger.info('creating a NumpyTimeAverager')
        myavger = NumpyTimeAverager( pkg = pkg,
                                     var = var,
                                     unwgt = unwgt,
                                     avg_type = avg_type )

    # workload
    if myavger is not None:
        exitstatus = myavger.generate_timavg( infile = infile,
                                              outfile = outfile)
    else:
        fre_logger.error('averager is None, check generate_time_average in generate_time_averages.py!')
        raise ValueError

    # remove the new merged file if we created it.
    if merged:
        fre_logger.warning('removing merged_file = %s', merged_file)
        os.remove(merged_file)

    fre_logger.debug('generate_time_average call finished')
    fre_logger.info('Finished in total time %s second(s)', round(time.perf_counter() - start_time , 2))
    return exitstatus

def generate(inf = None,
             outf = None,
             pkg = None,
             var = None,
             unwgt= False,
             avg_type = None  ):
    ''' click entrypoint to time averaging routine '''
    exitstatus = generate_time_average( inf, outf,
                                        pkg, var,
                                        unwgt,
                                        avg_type)
    if exitstatus!=0:
        fre_logger.warning('time averaging exited non-zero, exitstatus == %s', exitstatus)
    else:
        fre_logger.info('time averaging finished successfully')
