''' tests for the frenctoolsTimeAverager class, mocking timavg.csh so these
run without a real fre-nctools installation (e.g. in CI) '''

from unittest.mock import patch, MagicMock

import pytest

from .. import frenctoolsTimeAverager as frenc_timavg


def _mock_subp(stdout=b'ok', stderr=b'', returncode=0):
    ''' build a MagicMock standing in for the Popen context manager '''
    subp = MagicMock()
    subp.communicate.return_value = (stdout, stderr)
    subp.returncode = returncode
    return subp


@patch(f'{frenc_timavg.__name__}.Popen')
@patch(f'{frenc_timavg.__name__}.shutil.which')
def test_generate_timavg_all_single_infile(mock_which, mock_popen):
    ''' successful run with a single string infile builds the right command
    and survives non-utf8 bytes on stdout/stderr '''
    mock_which.return_value = '/usr/bin/timavg.csh'
    mock_popen.return_value.__enter__.return_value = _mock_subp(
        stdout=b'all good \xff', stderr=b'\xfe some warning')

    avgr = frenc_timavg.frenctoolsTimeAverager(pkg='fre-nctools', var=None,
                                                unwgt=False, avg_type='all')
    exitstatus = avgr.generate_timavg(infile='atmos.1980-1981.nc',
                                       outfile='atmos.1980-1981.ann.nc')

    assert exitstatus == 0
    called_cmd = mock_popen.call_args[0][0]
    assert called_cmd == ['/usr/bin/timavg.csh', '-dmb', '-o',
                           'atmos.1980-1981.ann.nc', 'atmos.1980-1981.nc']


@patch(f'{frenc_timavg.__name__}.Popen')
@patch(f'{frenc_timavg.__name__}.shutil.which')
def test_generate_timavg_all_multiple_infiles(mock_which, mock_popen):
    ''' a list of infiles is appended as individual command args, not
    embedded as a nested list (the bug this PR fixes) '''
    mock_which.return_value = '/usr/bin/timavg.csh'
    mock_popen.return_value.__enter__.return_value = _mock_subp()

    avgr = frenc_timavg.frenctoolsTimeAverager(pkg='fre-nctools', var=None,
                                                unwgt=False, avg_type='all')
    exitstatus = avgr.generate_timavg(infile=['a.nc', 'b.nc'], outfile='out.nc')

    assert exitstatus == 0
    called_cmd = mock_popen.call_args[0][0]
    assert called_cmd == ['/usr/bin/timavg.csh', '-dmb', '-o', 'out.nc',
                           'a.nc', 'b.nc']


@patch(f'{frenc_timavg.__name__}.Popen')
@patch(f'{frenc_timavg.__name__}.shutil.which')
def test_generate_timavg_all_nonzero_returncode_raises(mock_which, mock_popen):
    ''' a failing timavg.csh call raises ValueError '''
    mock_which.return_value = '/usr/bin/timavg.csh'
    mock_popen.return_value.__enter__.return_value = _mock_subp(returncode=1)

    avgr = frenc_timavg.frenctoolsTimeAverager(pkg='fre-nctools', var=None,
                                                unwgt=False, avg_type='all')
    with pytest.raises(ValueError):
        avgr.generate_timavg(infile='atmos.1980-1981.nc', outfile='out.nc')


@patch(f'{frenc_timavg.__name__}.Popen')
@patch(f'{frenc_timavg.__name__}.Cdo')
@patch(f'{frenc_timavg.__name__}.shutil.which')
def test_generate_timavg_month(mock_which, mock_cdo, mock_popen, tmp_path, monkeypatch):
    ''' monthly climatology branch survives non-utf8 bytes on stdout/stderr,
    without needing a real cdo/timavg.csh install '''
    monkeypatch.chdir(tmp_path)
    mock_which.return_value = '/usr/bin/timavg.csh'
    mock_cdo.return_value.select = MagicMock()
    mock_popen.return_value.__enter__.return_value = _mock_subp(
        stdout=b'monthly ok \xff', stderr=b'\xfe some warning')

    avgr = frenc_timavg.frenctoolsTimeAverager(pkg='fre-nctools', var=None,
                                                unwgt=False, avg_type='month')
    exitstatus = avgr.generate_timavg(infile='atmos.nc',
                                       outfile=str(tmp_path / 'out' / 'atmos.nc'))

    assert exitstatus == 0
    assert mock_popen.call_count == 12
