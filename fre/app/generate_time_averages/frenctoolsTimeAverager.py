''' class for utilizing timavg.csh (aka script to TAVG fortran exe) in frenc-tools '''
from .timeAverager import timeAverager
import os 
from netCDF4 import Dataset, num2date
import calendar
from cdo import Cdo
import logging
import subprocess
import shutil

cdo = Cdo()
fre_logger = logging.getLogger(__name__)

class frenctoolsTimeAverager(timeAverager):
    '''
    class inheriting from abstract base class timeAverager
    generates time-averages using fre-nctools
    '''

    def generate_timavg(self, infile=None, outfile=None):
        ''' use fre-nctool's CLI timavg.csh with subprocess call '''
        assert self.pkg=="fre-nctools"
        if __debug__:
            fre_logger.debug(locals()) #input argument details

        exitstatus=1
        if self.avg_type not in ['month','all']:
            raise fre_logger.error('avg_type= %s not supported by this class at this time.', self.avg_type)

        if self.unwgt:
            fre_logger.warning('unwgt=True unsupported by frenctoolsAverager. Ignoring!!!')

        if self.var is not None:
            fre_logger.warning('Variable specification (var= %s)' + \
                   ' not currently supported for frenctols time averaging. ignoring!', self.var)

        if infile is None:
            raise fre_logger.error('Need an input file, specify a value for the infile argument')

        if outfile is None:
            outfile='frenctoolsTimeAverage_'+infile
            fre_logger.warning('No output filename given, setting outfile= %s', outfile)
        
        #check for existence of timavg.csh. If not found, issue might be that user is not in env with frenctools.
        if shutil.which('timavg.csh') is None:
            raise fre_logger.error('did not find timavg.csh')
            
        from subprocess import Popen, PIPE

        
        #Recursive call if month is selcted for climatology. by Avery Kiihne
        if self.avg_type == 'month':
            monthly_nc_dir = f"monthly_nc_files"    #Folder that new monthly input files are put 
            output_dir = f"monthly_output_files"    #Folder for the results, split by month
            os.makedirs(monthly_nc_dir, exist_ok=True)   #create directory if it does not exist
            os.makedirs(output_dir, exist_ok=True)
            #Extract unique months from the infile 
            month_indices = list(range(1, 13))   #serves to track month index and as part of the outfile name
            month_names = [calendar.month_name[i] for i in month_indices]

            #Dictionary to store output filenames by month
            nc_month_file_paths = {month_index: os.path.join(monthly_nc_dir, f"all_years.{month_index}.nc") for month_index in month_indices}
            month_output_file_paths = {month_index: os.path.join(output_dir, f"{outfile}_.{month_index}.nc") for month_index in month_indices}

            #Loop through each month and select the corresponding data
            for month_index in month_indices:
                month_name = month_names[month_index - 1]
                nc_monthly_file = nc_month_file_paths[month_index]

                #Select data for the given month
                cdo.select(f"month={month_index}", input=infile, output=nc_monthly_file)

                #Run timavg command for newly created file
                month_output_file = month_output_file_paths[month_index]
                timavgcsh_command=['timavg.csh', '-mb','-o', month_output_file, nc_monthly_file]
                exitstatus=1
                with Popen(timavgcsh_command,
                        stdout=PIPE, stderr=PIPE, shell=False) as subp:
                    output=subp.communicate()[0]
                            

                    if subp.returncode < 0:
                        fre_logger.error('error: timavgcsh command not properly executed')
                    else:
                        fre_logger.info('%s climatology successfully ran',nc_monthly_file)
                        exitstatus=0
                        
                #Delete files after being used to generate output files
            shutil.rmtree('monthly_nc_files')    

        if self.avg_type == 'month':   #End here if month variable used
            raise exitstatus
        
        timavgcsh_command=['timavg.csh', '-mb','-o', outfile, infile]
        exitstatus=1
        with Popen(timavgcsh_command,
                   stdout=PIPE, stderr=PIPE, shell=False) as subp:
            output=subp.communicate()[0]
            fre_logger.info('output= %s',output)

            if subp.returncode < 0:
                fre_logger.error('error: timavgcsh command not properly executed')
            else:
                fre_logger.info('climatology successfully ran')
                exitstatus=0

        raise exitstatus
