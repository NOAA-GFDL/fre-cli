''' class for utilizing timavg.csh (aka script to TAVG fortran exe) in frenc-tools '''
import os
import calendar
import logging
import shutil
import subprocess
from subprocess import Popen, PIPE        
from pathlib import Path

from netCDF4 import Dataset, num2date
from cdo import Cdo
from .timeAverager import timeAverager

fre_logger = logging.getLogger(__name__)

class frenctoolsTimeAverager(timeAverager):
    '''
    class inheriting from abstract base class timeAverager
    generates time-averages using fre-nctools
    '''

    def generate_timavg(self, infile=None, outfile=None):
        """
        use fre-nctool's CLI timavg.csh with subprocess call

        :param self: This is an instance of the class frenctoolsTimeAverager
        :param infile: path to history file, or list of paths, default is None
        :type infile: str, list
        :param outfile: path to where output file should be stored, default is None
        :type outfile: str
        :return: 1 if timavg.csh command is not properly executed, and 0 if function has a clean exit
        :rtype: int
        :raises ValueError:
            - instance variable self.avg_type not supported
            - No infile specified
            - Cannot find timavg.csh (likely the user is not in an environment with frenctools installed)
            - timavgcsh command is not properly executed
        """
        exitstatus=1
        if self.avg_type not in ['month','all']:
            raise ValueError(f'avg_type= {self.avg_type} not supported by this class at this time.')

        if self.unwgt:
            fre_logger.warning('unwgt=True unsupported by frenctoolsAverager. Ignoring!!!')

        if self.var is not None:
            fre_logger.warning('Variable specification (var= %s)' + \
                   ' not currently supported for frenctols time averaging. ignoring!', self.var)

        if infile is None:
            raise ValueError('Need an input file, specify a value for the infile argument')

        if outfile is None:
            outfile='frenctoolsTimeAverage_'+infile
            fre_logger.warning('No output filename given, setting outfile= %s', outfile)

        #check for existence of timavg.csh. If not found, issue might be that user is not in env with frenctools.
        if shutil.which('timavg.csh') is None:
            raise ValueError('did not find timavg.csh')
        fre_logger.info(f'timeaverager using: {shutil.which("timavg.csh")}')



        #Recursive call if month is selected for climatology. by Avery Kiihne
        if self.avg_type == 'month':
            monthly_nc_dir = f"monthly_nc_files"    #Folder that new monthly input files are put 
            output_dir = Path(outfile).parent       #Save output in the user-specified location
            os.makedirs(monthly_nc_dir, exist_ok=True)   #create directory if it does not exist
            fre_logger.info('created monthly_nc_dir = %s', str(Path(monthly_nc_dir).resolve()))
            os.makedirs(output_dir, exist_ok=True)
            fre_logger.info('created output_dir = %s', str(Path(monthly_nc_dir).resolve()))

            #Extract unique months from the infile
            month_indices = list(range(1, 13))   #serves to track month index and as part of the outfile name
            month_names = [calendar.month_name[i] for i in month_indices]

            #Dictionary to store output filenames by month
            nc_month_file_paths = {month_index: os.path.join(monthly_nc_dir, f"all_years.{month_index}.nc") for month_index in month_indices}
            month_output_file_paths = {month_index: os.path.join(output_dir, f"{Path(outfile).stem}.{month_index:02d}.nc") for month_index in month_indices}

            cdo = Cdo()
            #Loop through each month and select the corresponding data
            for month_index in month_indices:


                month_name = month_names[month_index - 1]
                nc_monthly_file = nc_month_file_paths[month_index]

                #Select data for the given month
                cdo.select(f"month={month_index}", input=infile, output=nc_monthly_file)

                #Run timavg command for newly created file
                month_output_file = month_output_file_paths[month_index]
                timavgcsh_command=['timavg.csh', '-mb','-o', month_output_file, nc_monthly_file]
                fre_logger.debug( 'timavgcsh_command is %s', ' '.join(timavgcsh_command) )
                exitstatus=1
                with Popen(timavgcsh_command,
                        stdout=PIPE, stderr=PIPE, shell=False) as subp:
                    stdout, stderr = subp.communicate()
                    stdoutput=stdout.decode()
                    fre_logger.info('output= %s', stdoutput)
                    stderror=stderr.decode()
                    #fre_logger.info('error = %s', stderror )

                    if subp.returncode != 0:
                        fre_logger.error('stderror  = %s', stderror)
                        raise ValueError('error: timavgcsh command not properly executed, subp.returncode=%s',subp.returncode)
                    else:
                        fre_logger.info('%s climatology successfully ran',nc_monthly_file)
                        exitstatus=0

                #Delete files after being used to generate output files
            shutil.rmtree('monthly_nc_files')

        if self.avg_type == 'month':   #End here if month variable used
            return exitstatus

        timavgcsh_command=['timavg.csh', '-mb','-o', outfile, infile]
        fre_logger.debug( 'timavgcsh_command is %s', ' '.join(timavgcsh_command) )
        exitstatus=1
        with Popen(timavgcsh_command,
                   stdout=PIPE, stderr=PIPE, shell=False) as subp:
            stdout, stderr = subp.communicate()
            stdoutput=stdout.decode()
            fre_logger.info('output= %s', stdoutput)
            stderror=stderr.decode()
            #fre_logger.info('error = %s', stderror )

            if subp.returncode != 0:
                fre_logger.error('stderror  = %s', stderror)
                raise ValueError('error: timavgcsh command not properly executed, subp.returncode=%s',subp.returncode)
            else:
                fre_logger.info('climatology successfully ran')
                exitstatus=0

        return exitstatus
