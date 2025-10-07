''' tools for generating time averages from various packages '''

import os
import logging

from cdo import Cdo

from .cdoTimeAverager import cdoTimeAverager
from .frenctoolsTimeAverager import frenctoolsTimeAverager
from .frepytoolsTimeAverager import frepytoolsTimeAverager        

fre_logger = logging.getLogger(__name__)


def generate_time_average(infile   = None,
                          outfile  = None,
                          pkg      = None,
                          var      = None,
                          unwgt    = False,
                          avg_type = None   ):
    """
    steering function to various averaging functions above
    
    :param infile: path to history file, or list of paths
    :type infile: str, list
    :param outfile: path to where output file should be stored
    :type outfile: str
    :param pkg: which package to use to calculate climatology (cdo, fre-nctools, fre-python-tools)
    :type pkg: str
    :param var: not currently supported, defaults to none
    :type var: str
    :param unwgt: wether or not to weight the data, default false
    :type unwgt: bool
    :param avg_type: time scale for climatology. Accepted values based on pkg ('all','seas','month'), defaults to 'all'
    :type avg_type: str
    :return: error message if requested package unknown, otherwise returns climatology
    :rtype: int
    """
    fre_logger.debug('called generate_time_average')
    exitstatus=1
    myavger=None

    #Use cdo to merge multiple files if present
    merged = False
    if type(infile).__name__=='list' and len(infile)> 1:   #multiple files case. Generates one combined file
        fre_logger.info('list input argument detected')
        infile_str = [str(item) for item in infile]
        
        _cdo=Cdo()
        merged_file = "merged_output.nc"
        
        fre_logger.info('calling cdo mergetime')
        fre_logger.debug(' output: {merged_file}')
        fre_logger.debug( 'inputs:\n '+ ' '.join(infile_str))
        _cdo.mergetime(input=' '.join(infile_str), output=merged_file)
        multi_file = infile   #preserve the original file names for later
        infile = merged_file
        merged = True
        fre_logger.info('file merging success')



    if   pkg == 'cdo'            :
        fre_logger.info('creating a cdoTimeAverager')        
        myavger=cdoTimeAverager( pkg      = pkg,
                                 var      = var,
                                 unwgt    = unwgt,
                                 avg_type = avg_type )

    elif pkg == 'fre-nctools'    :
        fre_logger.info('creating a frenctoolsTimeAverager')
        myavger=frenctoolsTimeAverager( pkg      = pkg,
                                        var      = var,
                                        unwgt    = unwgt,
                                        avg_type = avg_type )

    elif pkg == 'fre-python-tools':   #fre-python-tools addresses var in a unique way, which is addressed here
        #TODO: generate an error message if multiple files exist in infiles, with different results for the var search
        # this seems oddly specific
        if merged == True and var == None:
            fre_logger.warning('WARNING! special variable id logic underway...')
            var = multi_file[0].split('/').pop().split('.')[-2]
            fre_logger.warning(f'extracted var={var} from multi_file[0]={multi_file[0]}')

        fre_logger.info('creating a frepytoolsTimeAverager')
        myavger=frepytoolsTimeAverager(pkg      = pkg,
                                       var      = var,
                                       unwgt    = unwgt,
                                       avg_type = avg_type)

    else :
        fre_logger.error('requested package unknown. exit.')
        raise ValueError

    if myavger is not None:
        exitstatus=myavger.generate_timavg(infile=infile, outfile=outfile)
    else:
        fre_logger.info('ERROR: averager is None, check generate_time_average in generate_time_averages.py!')
        raise ValueError

    #remove new file if merged created from multiple infiles
    if merged:   #if multiple files where used, the merged version is now removed
        fre_logger.warning(f'WARNING! removing merged_file={merged_file}')
        os.remove(merged_file)
    fre_logger.debug('generate_time_average call finished')
    return exitstatus

def generate(inf      = None,
             outf     = None,
             pkg      = None,
             var      = None,
             unwgt    = False,
             avg_type = None  ):
    ''' click entrypoint to time averaging routine '''
    fre_logger.debug('generate called')
    exitstatus=generate_time_average( inf, outf,
                                      pkg, var,
                                      unwgt,
                                      avg_type)
    if exitstatus!=0:
        fre_logger.warning(f'WARNING: exitstatus={exitstatus} != 0. Something exited poorly!')
    else:
        fre_logger.info('time averaging finished successfully')
    fre_logger.debug('generate call finished')
