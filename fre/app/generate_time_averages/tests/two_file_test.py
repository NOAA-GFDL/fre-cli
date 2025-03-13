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
test_file_names = ['ocean_1x1.000101-000212.tos.nc','ocean_1x1.000301-000412.tos.nc']
test_file_names = [time_avg_file_dir+test_file_names[0],time_avg_file_dir+test_file_names[1]]

test_file_name = 'test_out_double_hist.nc'

#preamble tests
def test_time_avg_file_dir_exists():
    ''' look for input test file directory '''
    assert pl.Path(time_avg_file_dir).exists()


### cdo avgs, unweighted, all/seasonal/monthly ------------------------
def test_monthly_cdo_time_unwgt_avgs():
    ''' generates an unweighted monthly time averaged file using cdo '''
    assert run_avgtype_pkg_calculations(
        infile  = test_file_names,
        outfile = (time_avg_file_dir+'ymonmean_unwgt_'+test_file_name),
        pkg='cdo',avg_type='month',unwgt=True )

def test_seasonal_cdo_time_unwgt_avgs():
    ''' generates an unweighted seasonal time averaged file using cdo '''
    assert run_avgtype_pkg_calculations(
        infile  = test_file_names,
        outfile = (time_avg_file_dir+'yseasmean_unwgt_'+test_file_name),
        pkg='cdo',avg_type='seas',unwgt=True )

def test_cdo_time_unwgt_avgs():
    ''' generates an unweighted time averaged file using cdo '''
    assert run_avgtype_pkg_calculations(
        infile  = test_file_names,
        outfile = (time_avg_file_dir+'timmean_unwgt_'+test_file_name),
        pkg='cdo',avg_type='all',unwgt=True )
  
#### cdo avgs, weighted, all/seasonal/monthly ------------------------
def test_cdo_time_avgs():
    ''' generates a weighted time averaged file using cdo '''
    assert run_avgtype_pkg_calculations(
        infile  = (test_file_names),
        outfile = (time_avg_file_dir+'timmean_'+test_file_name),
        pkg='cdo',avg_type='all',unwgt=False )

### cdo stddevs, unweighted, all/seasonal/monthly ------------------------
def test_monthly_cdo_time_unwgt_stddevs():
    ''' generates a monthly time averaged file using cdo '''
    assert run_avgtype_pkg_calculations(
        infile  = (test_file_names),
        outfile = (time_avg_file_dir+'ymonstddev1_unwgt_'+test_file_name),
        pkg='cdo',avg_type='month',stddev_type='samp', unwgt=True )

def test_seasonal_cdo_time_unwgt_stddevs():
    ''' generates a seasonal time averaged file using cdo '''
    assert run_avgtype_pkg_calculations(
        infile  = (test_file_names),
        outfile = (time_avg_file_dir+'yseasstddev1_unwgt_'+test_file_name),
        pkg='cdo',avg_type='seas',stddev_type='samp',unwgt=True )

def test_cdo_time_unwgt_stddevs():
    ''' generates a time averaged file using cdo '''
    assert run_avgtype_pkg_calculations(
        infile  = (test_file_names),
        outfile = (time_avg_file_dir+'yseasmean_unwgt_'+test_file_name),
        pkg='cdo',avg_type='all',stddev_type='samp', unwgt=True )


## frepythontools avgs+stddevs, weighted+unweighted, all ------------------------
def test_fre_cli_time_avgs():
    ''' generates a time averaged file using fre_cli's version '''
    ''' weighted average, no std deviation '''
    assert run_avgtype_pkg_calculations(
        infile  = (test_file_names),
        outfile = (time_avg_file_dir+'frepytools_timavg_'+test_file_name),
        pkg='fre-python-tools',avg_type='all', unwgt=False )

def test_fre_cli_time_unwgt_avgs():
    ''' generates a time averaged file using fre_cli's version '''
    ''' weighted average, no std deviation '''
    assert run_avgtype_pkg_calculations(
        infile  = (test_file_names),
        outfile = (time_avg_file_dir+'frepytools_unwgt_timavg_'+test_file_name),
        pkg='fre-python-tools',avg_type='all', unwgt=True )

def test_fre_cli_time_avgs_stddevs():
    ''' generates a time averaged file using fre_cli's version '''
    ''' weighted average, no std deviation '''
    assert run_avgtype_pkg_calculations(
        infile  = (test_file_names),
        outfile = (time_avg_file_dir+'frepytools_stddev_'+test_file_name),
        pkg='fre-python-tools',avg_type='all', stddev_type='samp', unwgt=False )

def test_fre_cli_time_unwgt_avgs_stddevs():
    ''' generates a time averaged file using fre_cli's version '''
    ''' weighted average, no std deviation '''
    assert run_avgtype_pkg_calculations(
        infile  = (test_file_names),
        outfile = (time_avg_file_dir+'frepytools_unwgt_stddev_'+test_file_name),
        pkg='fre-python-tools',avg_type='all', stddev_type='samp', unwgt=True )
'''
To be implemnted when fre-nctools has been updated. these options currently work locally if a user has fre-nctools in their conda env.
## fre-nctools avgs+stddevs, weighted+unweighted, all ------------------------
def test_fre_nctool_time_avgs():
    # generates a time averaged file using fre_nctools's version 
    # weighted average, no std deviation 
    assert run_avgtype_pkg_calculations(
        infile  = (test_file_names),
        outfile = (time_avg_file_dir+'fre_nctools_timavg_'+test_file_name),
        pkg='fre-nctools',avg_type='all', unwgt=False )

def test_fre_nctools_time_unwgt_avgs():
    # generates a time averaged file using fre_nctools's version 
    # weighted average, no std deviation 
    assert run_avgtype_pkg_calculations(
        infile  = (test_file_names),
        outfile = (time_avg_file_dir+'fre_nctools_unwgt_timavg_'+test_file_name),
        pkg='fre-nctools',avg_type='all', unwgt=True )

def test_fre_nctool_time_avgs_stddevs():
    # generates a time averaged file using fre_nctool's version 
    # weighted average, no std deviation 
    assert run_avgtype_pkg_calculations(
        infile  = (test_file_names),
        outfile = (time_avg_file_dir+'fre_nctools_stddev_'+test_file_name),
        pkg='fre-nctools',avg_type='all', stddev_type='samp', unwgt=False )

def test_fre_nctool_time_unwgt_avgs_stddevs():
    # generates a time averaged file using fre_nctool's version 
    # weighted average, no std deviation 
    assert run_avgtype_pkg_calculations(
        infile  = (test_file_names),
        outfile = (time_avg_file_dir+'fre_nctools_unwgt_stddev_'+test_file_name),
        pkg='fre-nctools',avg_type='all', stddev_type='samp', unwgt=True )

'''
