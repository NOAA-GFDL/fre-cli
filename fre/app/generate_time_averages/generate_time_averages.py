''' tools for generating time averages from various packages '''

import os
import logging
import time
from typing import Optional, List, Union

from cdo import Cdo

from .cdoTimeAverager import cdoTimeAverager
from .frenctoolsTimeAverager import frenctoolsTimeAverager
from .frepytoolsTimeAverager import frepytoolsTimeAverager

fre_logger = logging.getLogger(__name__)

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
    :param pkg: which package to use to calculate climatology (cdo, fre-nctools, fre-python-tools)
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
    if pkg not in ['cdo', 'fre-nctools', 'fre-python-tools']:
        raise ValueError(f'argument pkg = {pkg} not known, must be one of: cdo, fre-nctools, fre-python-tools')
    exitstatus = 1
    myavger = None

    # multiple files case Use cdo to merge multiple files if present
    merged = False
    orig_infile_list = None
    if all ( [ type(infile).__name__ == 'list',
               len(infile) > 1 ] ) :
        fre_logger.info('list input argument detected')
        infile_str = [str(item) for item in infile]

        _cdo = Cdo()
        merged_file = "merged_output.nc"

        fre_logger.info('calling cdo mergetime')
        fre_logger.debug(' output: {merged_file}')
        fre_logger.debug( 'inputs: \n %s', ' '.join(infile_str) )
        _cdo.mergetime(input = ' '.join(infile_str), output = merged_file)

        # preserve the original file names for later
        orig_infile_list = infile
        infile = merged_file
        merged = True
        fre_logger.info('file merging success')

    if pkg == 'cdo':
        fre_logger.info('creating a cdoTimeAverager')
        myavger = cdoTimeAverager( pkg = pkg,
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

        fre_logger.info('creating a frepytoolsTimeAverager')
        myavger = frepytoolsTimeAverager( pkg = pkg,
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



