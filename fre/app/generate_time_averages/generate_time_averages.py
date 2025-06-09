''' tools for generating time averages from various packages '''
import logging
fre_logger = logging.getLogger(__name__)

def generate_time_average(infile = None, outfile = None,
                          pkg = None, var = None, unwgt = False,
                          avg_type = None):
    ''' steering function to various averaging functions above'''
    if __debug__:
        fre_logger.info(locals()) #input argument details
    exitstatus=1

    myavger=None

    #Use cdo to merge multiple files if present
    merged = False
    if type(infile).__name__=='list' and len(infile)> 1:   #multiple files case. Generates one combined file
        from cdo import Cdo
        _cdo=Cdo()
        merged_file = "merged_output.nc"
        _cdo.mergetime(input=' '.join(infile), output=merged_file)
        multi_file = infile   #preserve the original file names for later
        infile = merged_file
        merged = True



    if   pkg == 'cdo'            :
        from .cdoTimeAverager import cdoTimeAverager
        myavger=cdoTimeAverager(pkg = pkg, var=var,
                                unwgt = unwgt,
                                avg_type = avg_type)

    elif pkg == 'fre-nctools'    :
        from .frenctoolsTimeAverager import frenctoolsTimeAverager
        myavger=frenctoolsTimeAverager(pkg = pkg, var=var,
                                       unwgt = unwgt ,
                                       avg_type = avg_type)

    elif pkg == 'fre-python-tools':   #fre-python-tools adresses var in a uniqe way, which is adressed here
      #TO-DO: generate an error message if multiple files exist in infiles, with different results for the var search
        if merged == True and var == None:
            var = multi_file[0].split('/').pop().split('.')[-2]
        from .frepytoolsTimeAverager import frepytoolsTimeAverager
        myavger=frepytoolsTimeAverager(pkg = pkg, var=var,
                                       unwgt = unwgt,
                                       avg_type = avg_type)

    else :
        fre_logger.info('requested package unknown. exit.')
        return exitstatus

    if __debug__:
        fre_logger.info(f'myavger.__repr__={myavger.__repr__}')
    if myavger is not None:
        exitstatus=myavger.generate_timavg(infile=infile, outfile=outfile)
    else:
        fre_logger.info('ERROR: averager is None, check generate_time_average in generate_time_averages.py!')
    #remove new file if merged created from multiple infiles
    if merged:   #if multiple files where used, the merged version is now removed
        import os
        os.remove(merged_file)
    return exitstatus

def generate(inf = None, outf = None,
             pkg = None, var = None, unwgt = False,
             avg_type = None):
    ''' click entrypoint to time averaging routine '''
    exitstatus=generate_time_average( inf, outf,
                                      pkg, var,
                                      unwgt,
                                      avg_type)
    if exitstatus!=0:
        fre_logger.info(f'WARNING: exitstatus={exitstatus} != 0. Something exited poorly!')
    else:
        fre_logger.info('time averaging finished successfully')

if __name__ == '__main__':
    import time
    start_time=time.perf_counter()
    generate(inf, outf, pkg, var, unwgt, avg_type)
    fre_logger.info(f'Finished in total time {round(time.perf_counter() - start_time , 2)} second(s)')
