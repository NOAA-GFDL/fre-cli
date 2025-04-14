''' class for utilizing timavg.csh (aka script to TAVG fortran exe) in frenc-tools '''
from .timeAverager import timeAverager
import os 
from netCDF4 import Dataset, num2date
import calendar
from cdo import Cdo
cdo = Cdo()

class frenctoolsTimeAverager(timeAverager):
    '''
    class inheriting from abstract base class timeAverager
    generates time-averages using fre-nctools
    '''

    def generate_timavg(self, infile=None, outfile=None):
        ''' use fre-nctool's CLI timavg.csh with subprocess call '''
        assert self.pkg=="fre-nctools"
        if __debug__:
            print(locals()) #input argument details

        exitstatus=1
        if self.avg_type not in ['month','all']:
            print('correct location')
            print(f'ERROR: avg_type={self.avg_type} not supported by this class at this time.')
            return exitstatus

        if self.unwgt:
            print('WARNING: unwgt=True unsupported by frenctoolsAverager. ignoring!!!')

        if self.var is not None:
            print(f'WARNING: variable specification (var={self.var})' + \
                   ' not currently supported for frenctols time averaging. ignoring!')

        if infile is None:
            print('ERROR: I need an input file, specify a value for the infile argument')
            return exitstatus

        if outfile is None:
            outfile='frenctoolsTimeAverage_'+infile
            print(f'WARNING: no output filename given, setting outfile={outfile}')

        from subprocess import Popen, PIPE
########################################################################################
        #recursive call if month is selcted for climatology. by Avery Kiihne
        if self.avg_type == 'month':
            output_dir = f"monthly_outputs"
            os.makedirs(output_dir, exist_ok=True)
            # Extract unique months from the infile 
            month_indices = list(range(1, 13))
            month_names = [calendar.month_name[i] for i in month_indices]

            # Dictionary to store output filenames by month
            month_file_paths = {month: os.path.join(output_dir, f"{month}_all_years.nc") for month in month_names}

            # Loop through each month and select the corresponding data
        # Loop through each month and select the corresponding data
            for month_index in month_indices:
                month_name = month_names[month_index - 1]
                output_file = month_file_paths[month_name]

                # Select data for the given month
                cdo.select(f"month={month_index}", input=infile, output=output_file)

                #Delete files after being used to generate output files
            #for month_index in month_indices:  
             #   month_name = month_names[month_index - 1]
              #  output_file = month_file_paths[month_name]              
               # os.remove(output_file)
           # os.rmdir('monthly_outputs')    
########################################################################################

            
        timavgcsh_command=['timavg.csh', '-mb','-o', outfile, infile]
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
