''' tests for the cdoTimeAverager class specifically '''

import pytest

try:
    import cdo  # noqa: F401
    HAS_CDO = True
except ImportError:
    HAS_CDO = False

@pytest.mark.skipif(not HAS_CDO, reason='python-cdo not installed (deprecated)')
def test_cdotimavg_init_error():
    ''' test that a value error is raised appropriately '''
    from .. import cdoTimeAverager as cdo_timavg  # pylint: disable=import-outside-toplevel
    with pytest.raises(ValueError):
        test_avgr = cdo_timavg.cdoTimeAverager(pkg = 'cdo', var = None, unwgt = False, avg_type = 'FOO')
        test_avgr.generate_timavg(infile = None,
                                  outfile = None)
