''' class using (mostly) cdo functions for time-averages '''
from .timeAverager import timeAverager

class cdoTimeAverager(timeAverager):
    '''
    class inheriting from abstract base class timeAverager
    generates time-averages using cdo (mostly, see weighted approach)
    '''

    def generate_timavg(self, infile=None, outfile=None):
        ''' use cdo package routines via python bindings '''
        assert self.pkg=="cdo"
        if __debug__:
            print(locals()) #input argument details

        if all([self.avg_type!='all',self.avg_type!='seas',self.avg_type!='month',
                self.avg_type is not None]):
            print('ERROR, avg_type requested unknown.')
            return 1

        if self.var is not None:
            print(f'WARNING: variable specification (var={self.var})' + \
                   ' not currently supported for cdo time averaging. ignoring!')

        import cdo
        print(f'python-cdo version is {cdo.__version__}')
        from cdo import Cdo

        _cdo=Cdo()

        wgts_sum=0
        if not self.unwgt: #weighted case, cdo ops alone don't support a weighted time-average.
            from netCDF4 import Dataset
            import numpy

            nc_fin = Dataset(infile, 'r')

            time_bnds=nc_fin['time_bnds'][:].copy()
            wgts = ( numpy.moveaxis(time_bnds,0,-1)[1][:].copy() - \
                     numpy.moveaxis(time_bnds,0,-1)[0][:].copy() )
            wgts_sum=sum(wgts)
            if __debug__:
                print(f'wgts_sum={wgts_sum}')

        if self.avg_type == 'all':
            if self.stddev_type is None:
                print('time average over all time requested.')
                if self.unwgt:
                    _cdo.timmean(input=infile, output=outfile, returnCdf=True)
                else:
                    _cdo.divc( str(wgts_sum), input="-timsum -muldpm "+infile, output=outfile)

                print('done averaging over all time.')
            else:
                print('time standard-deviation (N-1) over all time requested.')
                _cdo.timstd1(input=infile, output=outfile, returnCdf=True)
                print('done computing standard-deviation over all time.')

        elif self.avg_type == 'seas':
            if self.stddev_type is None:
                print('seasonal time-averages requested.')
                _cdo.yseasmean(input=infile, output=outfile, returnCdf=True)
                print('done averaging over seasons.')
            else:
                print('seasonal time standard-deviation (N-1) requested.')
                _cdo.yseasstd1(input=infile, output=outfile, returnCdf=True)
                print('done averaging over seasons.')

        elif self.avg_type == 'month':

            if self.stddev_type is None:
                print('monthly time-averages requested.')
                _cdo.ymonmean(input=infile, output=outfile, returnCdf=True)
                print('done averaging over months.')
            else:
                print('monthly time standard-deviation (N-1) requested.')
                _cdo.ymonstd1(input=infile, output=outfile, returnCdf=True)
                print('done averaging over months.')

        else:
            print(f'problem: unknown avg_type={self.avg_type}')
            return 1

        print('done averaging')
        return 0
