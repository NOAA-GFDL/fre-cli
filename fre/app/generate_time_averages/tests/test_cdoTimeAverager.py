''' tests for the cdoTimeAverager class specifically '''

import pytest

from .. import cdoTimeAverager as cdo_timavg

def test_cdotimavg_init_error():
    ''' test that a value error is raised appropriately '''
    with pytest.raises(ValueError):
        test_avgr = cdo_timavg.cdoTimeAverager(pkg = 'cdo', var = None, unwgt = False, avg_type = 'FOO')
        test_avgr.generate_timavg(infile = None,
                                  outfile = None)
