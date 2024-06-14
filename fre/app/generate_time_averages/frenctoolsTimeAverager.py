''' class for utilizing timavg.csh (aka script to TAVG fortran exe) in frenc-tools '''
from .timeAverager import timeAverager

class frenctoolsTimeAverager(timeAverager):
    '''
    class inheriting from abstract base class timeAverager
    generates time-averages using fre-nctools
    '''

    def generate_timavg(self, infile=None, outfile=None):
        ''' use fre-nctool's CLI timavg.csh with subprocess call '''
        assert (self.pkg=="fre-nctools")
        if __debug__:
            print(locals()) #input argument details

        exitstatus=1
        if self.avg_type!='all':
            print(f'ERROR: avg_type={self.avg_type} is not supported by this function at this time.')
            return exitstatus

        if self.unwgt:
            print('WARNING: unwgt=True unsupported by frenctoolsAverager. ignoring!!!')

        if self.stddev_type is not None:
            print('WARNING: stddev_type arg unsupported by frenctoolsTimeAverager. ignoring!!!')

        if self.var is not None:
            print(f'WARNING: variable specification (var={self.var}) not currently supported for frenctols time averaging. ignoring!')

        if infile is None:
            print('ERROR: I need an input file, specify a value for the infile argument')
            return exitstatus

        if outfile is None:
            outfile='frenctoolsTimeAverage_'+infile
            print(f'WARNING: no output filename given, setting outfile={outfile}')

        from subprocess import Popen, PIPE

        precision='-r8'
        timavgcsh_command=['timavg.csh', precision, '-mb','-o', outfile, infile]
        exitstatus=1
        with Popen(timavgcsh_command,
                   stdout=PIPE, stderr=PIPE, shell=False) as subp:
            output=subp.communicate()[0]
            print(f'output={output}')

            if subp.returncode < 0:
                print('error')
            else:
                print('success')
                exitstatus=0

        return exitstatus
