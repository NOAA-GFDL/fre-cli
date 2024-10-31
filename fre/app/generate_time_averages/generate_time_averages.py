''' tools for generating time averages from various packages '''
import click

def generate_time_average(infile=None, outfile=None,
                          pkg=None, var=None,
                          unwgt=False, avg_type=None, stddev_type=None):
    ''' steering function to various averaging functions above'''
    if __debug__:
        print(locals()) #input argument details
    exitstatus=1

    #needs a case statement. better yet, smarter way to do this? (TODO)
    myavger=None
    if   pkg == 'cdo'            :
        from .cdoTimeAverager import cdoTimeAverager
        myavger=cdoTimeAverager(pkg = pkg, var=var,
                                unwgt = unwgt,
                                avg_type = avg_type, stddev_type = stddev_type)

    elif pkg == 'fre-nctools'    :
        from .frenctoolsTimeAverager import frenctoolsTimeAverager
        myavger=frenctoolsTimeAverager(pkg = pkg, var=var,
                                       unwgt = unwgt ,
                                       avg_type = avg_type, stddev_type = stddev_type)

    elif pkg == 'fre-python-tools':
        from .frepytoolsTimeAverager import frepytoolsTimeAverager
        myavger=frepytoolsTimeAverager(pkg = pkg, var=var,
                                       unwgt = unwgt,
                                       avg_type = avg_type, stddev_type = stddev_type)

    else :
        print('requested package unknown. exit.')
        return exitstatus

    if __debug__:
        print(f'myavger.__repr__={myavger.__repr__}')
    if myavger is not None:
        exitstatus=myavger.generate_timavg(infile=infile, outfile=outfile)
    else:
        print('ERROR: averager is None, check generate_time_average in generate_time_averages.py!')

    return exitstatus

@click.command()
def generate(inf, outf, pkg, var, unwgt, avg_type, stddev_type):
    ''' click entrypoint to time averaging routine '''
    exitstatus=generate_time_average( inf, outf,
                                      pkg, var,
                                      unwgt,
                                      avg_type, stddev_type)
    if exitstatus!=0:
        print(f'WARNING: exitstatus={exitstatus} != 0. Something exited poorly!')
    else:
        print('time averaging finished successfully')

if __name__ == '__main__':
    import time
    start_time=time.perf_counter()
    generate(inf, outf, pkg, var, unwgt, avg_type, stddev_type)
    print(f'Finished in total time {round(time.perf_counter() - start_time , 2)} second(s)')
