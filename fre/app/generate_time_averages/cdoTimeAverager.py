''' class using (mostly) cdo functions for time-averages '''

import logging

from netCDF4 import Dataset
import numpy as np

import cdo
from cdo import Cdo

from .timeAverager import timeAverager

fre_logger = logging.getLogger(__name__)

class cdoTimeAverager(timeAverager):
    '''
    class inheriting from abstract base class timeAverager
    generates time-averages using cdo (mostly, see weighted approach)
    '''

    def generate_timavg(self, infile = None, outfile = None):
        """
        use cdo package routines via python bindings        

        :param self: This is an instance of the class cdoTimeAverager
        :param infile: path to history file, or list of paths, default is None
        :type infile: str, list
        :param outfile: path to where output file should be stored, default is None
        :type outfile: str
        :return: 1 if the instance variable self.avg_typ is unsupported, 0 if function has a clean exit
        :rtype: int
        """

        if self.avg_type not in ['all', 'seas', 'month']:
            fre_logger.error('ERROR, requested unknown avg_type %s.', self.avg_type)
            raise ValueError

        if self.var is not None:
            fre_logger.warning('WARNING: variable specification not twr supported for cdo time averaging. ignoring!')

        fre_logger.info('python-cdo version is %s', cdo.__version__)

        _cdo = Cdo()

        wgts_sum = 0
        if not self.unwgt: #weighted case, cdo ops alone don't support a weighted time-average.

            nc_fin = Dataset(infile, 'r')

            time_bnds = nc_fin['time_bnds'][:].copy()
            wgts = ( np.moveaxis(time_bnds, 0, -1)[1][:].copy() - \
                     np.moveaxis(time_bnds, 0, -1)[0][:].copy() )
            wgts_sum = sum(wgts)

            fre_logger.debug('wgts_sum = %s', wgts_sum)

        if self.avg_type == 'all':
            fre_logger.info('time average over all time requested.')
            if self.unwgt:
                _cdo.timmean(input = infile, output = outfile, returnCdf = True)
            else:
                _cdo.divc( str(wgts_sum), input = "-timsum -muldpm "+infile, output = outfile)
            fre_logger.info('done averaging over all time.')

        elif self.avg_type == 'seas':
            fre_logger.info('seasonal time-averages requested.')
            _cdo.yseasmean(input = infile, output = outfile, returnCdf = True)
            fre_logger.info('done averaging over seasons.')

        elif self.avg_type == 'month':
            fre_logger.info('monthly time-averages requested.')
            outfile_str = str(outfile)
            _cdo.ymonmean(input = infile, output = outfile_str, returnCdf = True)
            fre_logger.info('done averaging over months.')

            fre_logger.warning(" splitting by month")
            outfile_root = outfile_str.removesuffix(".nc") + '.'
            _cdo.splitmon(input = outfile_str, output = outfile_root)
            fre_logger.debug('Done with splitting by month, outfile_root = %s', outfile_root)
        else:
            fre_logger.error('problem: unknown avg_type = %s', self.avg_type)
            raise ValueError

        fre_logger.info('done averaging')
        fre_logger.info('output file created: %s', outfile)
        return 0
