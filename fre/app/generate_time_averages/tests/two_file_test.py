''' for testing fre app generate-time-averages '''
import pathlib as pl
import pytest

def run_avgtype_pkg_calculations(infile=None,outfile=None, pkg=None, avg_type=None, unwgt=None,
                                 stddev_type=None):
    ''' test-harness function, called by other test functions. '''
    assert all( [infile is not None, outfile is not None,
                 pkg is not None, avg_type is not None,
                 unwgt is not None] )
    if pl.Path(outfile).exists():
        print('output test file exists. deleting before remaking.')
        pl.Path(outfile).unlink() #delete file so we check that it can be recreated
    from fre.app.generate_time_averages import generate_time_averages as gtas
    gtas.generate_time_average(infile = infile, outfile = outfile,
                               pkg = pkg, unwgt = unwgt,
                               avg_type = avg_type, stddev_type = stddev_type)
    return pl.Path(outfile).exists()

#now test running of time averager with two different files
time_avg_file_dir=str(pl.Path.cwd())+'/fre/app/generate_time_averages/tests/time_avg_test_files/'
test_file_name=['ocean_1x1.000101-000212.tos.nc','ocean_1x1.000301-000412.tos.nc']

### cdo avgs, unweighted, all/seasonal/monthly ------------------------
def test_monthly_cdo_time_unwgt_avgs():
    ''' generates an unweighted monthly time averaged file using cdo '''
    assert run_avgtype_pkg_calculations(
        infile  = (time_avg_file_dir+test_file_name),
        outfile = (time_avg_file_dir+'ymonmean_unwgt_'+test_file_name),
        pkg='cdo',avg_type='month',unwgt=True )

def test_seasonal_cdo_time_unwgt_avgs():
    ''' generates an unweighted seasonal time averaged file using cdo '''
    assert run_avgtype_pkg_calculations(
        infile  = (time_avg_file_dir+test_file_name),
        outfile = (time_avg_file_dir+'yseasmean_unwgt_'+test_file_name),
        pkg='cdo',avg_type='seas',unwgt=True )

def test_cdo_time_unwgt_avgs():
    ''' generates an unweighted time averaged file using cdo '''
    assert run_avgtype_pkg_calculations(
        infile  = (time_avg_file_dir+test_file_name),
        outfile = (time_avg_file_dir+'timmean_unwgt_'+test_file_name),
        pkg='cdo',avg_type='all',unwgt=True )
