''' tests for the cdoTimeAverager class specifically '''

import pytest

from .. import cdoTimeAverager as cdo_timavg

def test_cdotimavg_init_error():
    ''' test that a value error is raised appropriately '''
    with pytest.raises(ValueError):
        test_avgr = cdo_timavg.cdoTimeAverager(pkg = 'cdo', var = None, unwgt = False, avg_type = 'FOO')
        test_avgr.generate_timavg(infile = None,
                                  outfile = None)

def test_cdotimavg_warns_future():
    ''' test that FutureWarning is emitted when generate_timavg is called '''
    with pytest.warns(FutureWarning, match='CDO/python-cdo has been REMOVED'):
        test_avgr = cdo_timavg.cdoTimeAverager(pkg = 'cdo', var = None, unwgt = False, avg_type = 'all')
        # this will fail because infile is None, but the warning should fire first
        try:
            test_avgr.generate_timavg(infile = 'nonexistent.nc', outfile = 'out.nc')
        except (FileNotFoundError, ValueError, OSError):
            pass
