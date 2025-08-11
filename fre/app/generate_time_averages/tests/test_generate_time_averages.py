''' for testing fre app generate-time-averages '''
import pathlib as pl
import pytest
import subprocess
import os

def run_avgtype_pkg_calculations(infile=None,outfile=None, pkg=None, avg_type=None, unwgt=None):
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
                               avg_type = avg_type)
    return pl.Path(outfile).exists()

### preamble tests. if these fail, none of the others will succeed. -----------------
time_avg_file_dir=str(pl.Path.cwd())+'/fre/app/generate_time_averages/tests/test_data/'
base_file_name='atmos.197901-198312.LWP'

ncgen_input = (time_avg_file_dir + base_file_name+".cdl")
ncgen_output = (time_avg_file_dir + base_file_name+".nc")
test_file_name = 'atmos.197901-198312.LWP.nc'

if pl.Path(ncgen_output).exists():
    pl.Path(ncgen_output).unlink()
assert pl.Path(ncgen_input).exists()
ex = [ 'ncgen3', '-k', 'netCDF-4', '-o', ncgen_output, ncgen_input ]
subprocess.run(ex, check = True)

### Also recreate frenctools_timavg_atmos.197901-198312.LWP
time_avg_file_dir=str(pl.Path.cwd())+'/fre/app/generate_time_averages/tests/test_data/'
base_file_name_2='frenctools_timavg_atmos.197901-198312.LWP'

ncgen_input = (time_avg_file_dir + base_file_name_2+".cdl")
ncgen_output = (time_avg_file_dir + base_file_name_2+".nc")

if pl.Path(ncgen_output).exists():
    pl.Path(ncgen_output).unlink()
assert pl.Path(ncgen_input).exists()
ex = [ 'ncgen3', '-k', 'netCDF-4', '-o', ncgen_output, ncgen_input ]
subprocess.run(ex, check = True)


def test_time_avg_file_dir_exists():
    ''' look for input test file directory '''
    assert pl.Path(time_avg_file_dir).exists()

def test_time_avg_input_file_exists():
    ''' look for input test file '''
    assert pl.Path( time_avg_file_dir + test_file_name ).exists()

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


#### cdo avgs, weighted, all/seasonal/monthly ------------------------
## (TODO) WRITE THESE VERSIONS FOR CDOTIMEAVERAGER CLASS THEN MAKE THESE TESTS
##def test_monthly_cdo_time_avgs():
##def test_seasonal_cdo_time_avgs():

def test_cdo_time_avgs():
    ''' generates a weighted time averaged file using cdo '''
    assert run_avgtype_pkg_calculations(
        infile  = (time_avg_file_dir+test_file_name),
        outfile = (time_avg_file_dir+'timmean_'+test_file_name),
        pkg='cdo',avg_type='all',unwgt=False )


## frepythontools avgs, weighted+unweighted, all ------------------------
def test_fre_cli_time_avgs():
    ''' generates a time averaged file using fre_cli's version '''
    ''' weighted average, no std deviation '''
    assert run_avgtype_pkg_calculations(
        infile  = (time_avg_file_dir+test_file_name),
        outfile = (time_avg_file_dir+'frepytools_timavg_'+test_file_name),
        pkg='fre-python-tools',avg_type='all', unwgt=False )

def test_fre_cli_time_unwgt_avgs():
    ''' generates a time averaged file using fre_cli's version '''
    ''' weighted average, no std deviation '''
    assert run_avgtype_pkg_calculations(
        infile  = (time_avg_file_dir+test_file_name),
        outfile = (time_avg_file_dir+'frepytools_unwgt_timavg_'+test_file_name),
        pkg='fre-python-tools',avg_type='all', unwgt=True )


## (TODO) WRITE THESE VERSIONS FOR FREPYTOOLSTIMEAVERAGER CLASS THEN MAKE THESE TESTS
#def test_monthly_fre_cli_time_avgs():
#def test_monthly_fre_cli_time_unwgt_avgs():
#
#def test_seasonal_fre_cli_time_avgs():
#def test_seasonal_fre_cli_time_unwgt_avgs():



## this will only work at GFDL. dev convenience only.
#alt_str_fre_nctools_inf= \
#    'tests/time_avg_test_files/fre_nctools_timavg_CLI_test_r8_b_atmos_LWP_1979_5y.nc'
#def test_fre_nctools_time_avgs():
#    ''' generates a time averaged file using fre_cli's version '''
#    ''' weighted average, no std deviation '''
#    infile =time_avg_file_dir+test_file_name
#    all_outfile=time_avg_file_dir+'frenctools_timavg_'+test_file_name
#
#    if pl.Path(all_outfile).exists():
#        print('output test file exists. deleting before remaking.')
#        pl.Path(all_outfile).unlink() #delete file so we check that it can be recreated
#
#    from fre_cli.generate_time_averages import generate_time_averages as gtas
#    gtas.generate_time_average(infile = infile, outfile = all_outfile,
#        pkg='fre-nctools', unwgt=False, avg_type='all')
#    assert pl.Path(all_outfile).exists()


# Numerics-based tests. these have room for improvement for sure (TODO)
# compare frepytools, cdo time-average output to fre-nctools where possible
var='LWP'
str_fre_nctools_inf=time_avg_file_dir+'frenctools_timavg_'+test_file_name # this is now in the repo
str_fre_pytools_inf=time_avg_file_dir+'frepytools_timavg_'+test_file_name
str_cdo_inf=time_avg_file_dir+'timmean_'+test_file_name
str_unwgt_fre_pytools_inf=time_avg_file_dir+'frepytools_unwgt_timavg_'+test_file_name
str_unwgt_cdo_inf=time_avg_file_dir+'timmean_unwgt_'+test_file_name


def test_compare_fre_cli_to_fre_nctools():
    ''' compares fre_cli pkg answer to fre_nctools pkg answer '''
    import numpy as np
    import netCDF4 as nc
    fre_pytools_inf=nc.Dataset(str_fre_pytools_inf,'r')

    try:
        fre_nctools_inf=nc.Dataset(str_fre_nctools_inf,'r')
    except:
        print('fre-nctools input file not found. \
        probably because you are not at GFDL! run the shell script \
        example if you would like to see this pass. otherwise, \
        i will error right after this message.')
        try:
            fre_nctools_inf=nc.Dataset(alt_str_fre_nctools_inf,'r')
        except:
            print('fre-nctools output does not exist. create it first!')
            assert False

    fre_pytools_timavg=fre_pytools_inf[var][:].copy()
    fre_nctools_timavg=fre_nctools_inf[var][:].copy()
    assert all([ len(fre_pytools_timavg)==len(fre_nctools_timavg),
                len(fre_pytools_timavg[0])==len(fre_nctools_timavg[0]),
                 len(fre_pytools_timavg[0][0])==len(fre_nctools_timavg[0][0]) ])
'''
    diff_pytools_nctools_timavg=fre_pytools_timavg-fre_nctools_timavg
    for lat in range(0,len(diff_pytools_nctools_timavg[0])):
        for lon in range(0,len(diff_pytools_nctools_timavg[0][0])):
            print(f'lat={lat},lon={lon}')
            #diff_at_latlon=diff_pytools_nctools_timavg[0][lat][lon]
            #print(f'diff_pytools_nctools_timavg[0][lat][lon]={diff_at_latlon}')
            if lon>10: break
        break

    non_zero_count=np.count_nonzero(diff_pytools_nctools_timavg[:])
    #assert (non_zero_count == 0.) # bad way to check for zero.
    assert not( (non_zero_count > 0.) or (non_zero_count < 0.) )
'''
@pytest.mark.skip(reason='test fails b.c. cdo cannot bitwise-reproduce fre-nctools answer')
def test_compare_fre_cli_to_cdo():
    ''' compares fre_cli pkg answer to cdo pkg answer '''
    import numpy as np
    import netCDF4 as nc
    fre_pytools_inf=nc.Dataset(str_fre_pytools_inf,'r')

    try:
        cdo_inf=nc.Dataset(str_cdo_inf,'r')
    except:
        print('cdo input file not found. run cdo tests first.')
        assert False

    fre_pytools_timavg=fre_pytools_inf[var][:].copy()
    cdo_timavg=cdo_inf[var][:].copy()

    assert all([ len(fre_pytools_timavg)==len(cdo_timavg),
                len(fre_pytools_timavg[0])==len(cdo_timavg[0]),
                 len(fre_pytools_timavg[0][0])==len(cdo_timavg[0][0]) ])

    diff_pytools_cdo_timavg=fre_pytools_timavg-cdo_timavg
    for lat in range(0,len(diff_pytools_cdo_timavg[0])):
        for lon in range(0,len(diff_pytools_cdo_timavg[0][0])):
            print(f'lat={lat},lon={lon}')
            print(f'diff_pytools_cdo_timavg[0][lat][lon]={diff_pytools_cdo_timavg[0][lat][lon]}')
            if lon>10: break
        break

    non_zero_count=np.count_nonzero(diff_pytools_cdo_timavg[:])
    assert not( (non_zero_count > 0.) or (non_zero_count < 0.) )


def test_compare_unwgt_fre_cli_to_unwgt_cdo():
    ''' compares fre_cli pkg answer to cdo pkg answer '''
    import numpy as np
    import netCDF4 as nc
    fre_pytools_inf=nc.Dataset(str_unwgt_fre_pytools_inf,'r')

    try:
        cdo_inf=nc.Dataset(str_unwgt_cdo_inf,'r')
    except:
        print('cdo input file not found. run cdo tests first.')
        assert False

    fre_pytools_timavg=fre_pytools_inf[var][:].copy()
    cdo_timavg=cdo_inf[var][:].copy()
    assert all([ len(fre_pytools_timavg)==len(cdo_timavg),
                len(fre_pytools_timavg[0])==len(cdo_timavg[0]),
                 len(fre_pytools_timavg[0][0])==len(cdo_timavg[0][0]) ])

    diff_pytools_cdo_timavg=fre_pytools_timavg-cdo_timavg
    for lat in range(0,len(diff_pytools_cdo_timavg[0])):
        for lon in range(0,len(diff_pytools_cdo_timavg[0][0])):
            print(f'lat={lat},lon={lon}')
            print(f'diff_pytools_cdo_timavg[0][lat][lon]={diff_pytools_cdo_timavg[0][lat][lon]}')
            if lon>10: break
        break

    non_zero_count=np.count_nonzero(diff_pytools_cdo_timavg[:])
    assert not( (non_zero_count > 0.) or (non_zero_count < 0.) )

@pytest.mark.skip(reason='test fails b.c. cdo cannot bitwise-reproduce fre-nctools answer')
def test_compare_cdo_to_fre_nctools():
    ''' compares cdo pkg answer to fre_nctools pkg answer '''
    import numpy as np
    import netCDF4 as nc
    cdo_inf=nc.Dataset(str_cdo_inf,'r')

    try:
        fre_nctools_inf=nc.Dataset(str_fre_nctools_inf,'r')
    except:
        print('fre-nctools input file not found. \
        probably because you are not at GFDL! run the shell script \
        example if you would like to see this pass. otherwise, \
        i will error right after this message.')
        alt_str_fre_nctools_inf = \
            'tests/time_avg_test_files/fre_nctools_timavg_CLI_test_r8_b_atmos_LWP_1979_5y.nc'
        try:
            fre_nctools_inf=nc.Dataset(alt_str_fre_nctools_inf,'r')
        except:
            print('fre-nctools output does not exist. create it first!')
            assert False

    cdo_timavg=cdo_inf[var][:].copy()
    fre_nctools_timavg=fre_nctools_inf[var][:].copy()
    assert all([ len(cdo_timavg)==len(fre_nctools_timavg),
                len(cdo_timavg[0])==len(fre_nctools_timavg[0]),
                 len(cdo_timavg[0][0])==len(fre_nctools_timavg[0][0]) ])

    diff_cdo_nctools_timavg=cdo_timavg-fre_nctools_timavg
    for lat in range(0,len(diff_cdo_nctools_timavg[0])):
        for lon in range(0,len(diff_cdo_nctools_timavg[0][0])):
            print(f'lat={lat},lon={lon}')
            print(f'diff_cdo_nctools_timavg[0][lat][lon]={diff_cdo_nctools_timavg[0][lat][lon]}')
            if lon>10: break
        break

    non_zero_count=np.count_nonzero(diff_cdo_nctools_timavg[:])
    assert not( (non_zero_count > 0.) or (non_zero_count < 0.) )

#################################################################################################
time_avg_file_dir=str(pl.Path.cwd())+'/fre/app/generate_time_averages/tests/test_data/'
base_file_names=['ocean_1x1.000101-000212.tos','ocean_1x1.000301-000412.tos']
for base_file_name in base_file_names:
    ncgen_input = (time_avg_file_dir + base_file_name+".cdl")
    ncgen_output = (time_avg_file_dir + base_file_name+".nc")

    if pl.Path(ncgen_output).exists():
        pl.Path(ncgen_output).unlink()
    assert pl.Path(ncgen_input).exists()
    ex = [ 'ncgen3', '-k', 'netCDF-4', '-o', ncgen_output, ncgen_input ]
    subprocess.run(ex, check = True)


''' for testing fre app generate-time-averages with multiple files'''

#now test running of time averager with two different files
two_test_file_names = ['ocean_1x1.000101-000212.tos.nc','ocean_1x1.000301-000412.tos.nc']
two_test_file_names = [time_avg_file_dir+two_test_file_names[0],time_avg_file_dir+two_test_file_names[1]]

two_out_file_name = 'test_out_double_hist.nc'

#preamble tests
def test_time_avg_file_dir_exists_two_files():
    ''' look for input test file directory '''
    assert pl.Path(time_avg_file_dir).exists()


### cdo avgs, unweighted, all/seasonal/monthly ------------------------
def test_monthly_cdo_time_unwgt_avgs_two_files():
    ''' generates an unweighted monthly time averaged file using cdo '''
    assert run_avgtype_pkg_calculations(
        infile  = two_test_file_names,
        outfile = (time_avg_file_dir+'ymonmean_unwgt_'+two_out_file_name),
        pkg='cdo',avg_type='month',unwgt=True )

def test_seasonal_cdo_time_unwgt_avgs_two_files():
    ''' generates an unweighted seasonal time averaged file using cdo '''
    assert run_avgtype_pkg_calculations(
        infile  = two_test_file_names,
        outfile = (time_avg_file_dir+'yseasmean_unwgt_'+two_out_file_name),
        pkg='cdo',avg_type='seas',unwgt=True )

def test_cdo_time_unwgt_avgs_two_files():
    ''' generates an unweighted time averaged file using cdo '''
    assert run_avgtype_pkg_calculations(
        infile  = two_test_file_names,
        outfile = (time_avg_file_dir+'timmean_unwgt_'+two_out_file_name),
        pkg='cdo',avg_type='all',unwgt=True )

#### cdo avgs, weighted, all/seasonal/monthly ------------------------
def test_cdo_time_avgs_two_files():
    ''' generates a weighted time averaged file using cdo '''
    assert run_avgtype_pkg_calculations(
        infile  = (two_test_file_names),
        outfile = (time_avg_file_dir+'timmean_'+two_out_file_name),
        pkg='cdo',avg_type='all',unwgt=False )

### cdo stddevs, unweighted, all/seasonal/monthly ------------------------
def test_monthly_cdo_time_unwgt_stddevs_two_files():
    ''' generates a monthly time averaged file using cdo '''
    assert run_avgtype_pkg_calculations(
        infile  = (two_test_file_names),
        outfile = (time_avg_file_dir+'ymonstddev1_unwgt_'+two_out_file_name),
        pkg='cdo',avg_type='month', unwgt=True )

def test_seasonal_cdo_time_unwgt_stddevs_two_files():
    ''' generates a seasonal time averaged file using cdo '''
    assert run_avgtype_pkg_calculations(
        infile  = (two_test_file_names),
        outfile = (time_avg_file_dir+'yseasstddev1_unwgt_'+two_out_file_name),
        pkg='cdo',avg_type='seas', unwgt=True )

def test_cdo_time_unwgt_stddevs_two_files():
    ''' generates a time averaged file using cdo '''
    assert run_avgtype_pkg_calculations(
        infile  = (two_test_file_names),
        outfile = (time_avg_file_dir+'yseasmean_unwgt_'+two_out_file_name),
        pkg='cdo',avg_type='all', unwgt=True )


## frepythontools avgs+stddevs, weighted+unweighted, all ------------------------
def test_fre_cli_time_avgs_two_files():
    ''' generates a time averaged file using fre_cli's version '''
    ''' weighted average, no std deviation '''
    assert run_avgtype_pkg_calculations(
        infile  = (two_test_file_names),
        outfile = (time_avg_file_dir+'frepytools_timavg_'+two_out_file_name),
        pkg='fre-python-tools',avg_type='all', unwgt=False )

def test_fre_cli_time_unwgt_avgs_two_files():
    ''' generates a time averaged file using fre_cli's version '''
    ''' weighted average, no std deviation '''
    assert run_avgtype_pkg_calculations(
        infile  = (two_test_file_names),
        outfile = (time_avg_file_dir+'frepytools_unwgt_timavg_'+two_out_file_name),
        pkg='fre-python-tools',avg_type='all', unwgt=True )

def test_fre_cli_time_avgs_stddevs_two_files():
    ''' generates a time averaged file using fre_cli's version '''
    ''' weighted average, no std deviation '''
    assert run_avgtype_pkg_calculations(
        infile  = (two_test_file_names),
        outfile = (time_avg_file_dir+'frepytools_stddev_'+two_out_file_name),
        pkg='fre-python-tools',avg_type='all', unwgt=False )

def test_fre_cli_time_unwgt_avgs_stddevs_two_files():
    ''' generates a time averaged file using fre_cli's version '''
    ''' weighted average, no std deviation '''
    assert run_avgtype_pkg_calculations(
        infile  = (two_test_file_names),
        outfile = (time_avg_file_dir+'frepytools_unwgt_stddev_'+two_out_file_name),
        pkg='fre-python-tools',avg_type='all',  unwgt=True )

def test_zzz_cleanup():
    ''' Removes all .nc files in fre/app/generate_time_averages/tests/test_data/ '''
    nc_files = [os.path.join(time_avg_file_dir, el) for el in os.listdir(time_avg_file_dir)
                 if el.endswith(".nc")]
    nc_files = [pl.Path(el) for el in nc_files]
    for nc in nc_files:
        pl.Path.unlink(nc)
    nc_remove = [not pl.Path(el).exists() for el in nc_files]
    assert all(nc_remove)

'''
To be implemented when fre-nctools has been updated. these options currently work locally if a user has fre-nctools in their conda env.
## fre-nctools avgs+stddevs, weighted+unweighted, all ------------------------
def test_fre_nctool_time_avgs():
    # generates a time averaged file using fre_nctools's version
    # weighted average, no std deviation
    assert run_avgtype_pkg_calculations(
        infile  = (two_test_file_names),
        outfile = (time_avg_file_dir+'fre_nctools_timavg_'+two_out_file_name),
        pkg='fre-nctools',avg_type='all', unwgt=False )

def test_fre_nctools_time_unwgt_avgs():
    # generates a time averaged file using fre_nctools's version
    # weighted average, no std deviation
    assert run_avgtype_pkg_calculations(
        infile  = (two_test_file_names),
        outfile = (time_avg_file_dir+'fre_nctools_unwgt_timavg_'+two_out_file_name),
        pkg='fre-nctools',avg_type='all', unwgt=True )

def test_fre_nctool_time_avgs_stddevs():
    # generates a time averaged file using fre_nctool's version
    # weighted average, no std deviation
    assert run_avgtype_pkg_calculations(
        infile  = (two_test_file_names),
        outfile = (time_avg_file_dir+'fre_nctools_stddev_'+two_out_file_name),
        pkg='fre-nctools',avg_type='all',  unwgt=False )

def test_fre_nctool_time_unwgt_avgs_stddevs():
    # generates a time averaged file using fre_nctool's version
    # weighted average, no std deviation
    assert run_avgtype_pkg_calculations(
        infile  = (two_test_file_names),
        outfile = (time_avg_file_dir+'fre_nctools_unwgt_stddev_'+two_out_file_name),
        pkg='fre-nctools',avg_type='all',  unwgt=True )

# This set of tests is for the monthly frenctools option
def test_fre_nctools_all():
    # tests run of frenctools climatology with all flag
    assert run_avgtype_pkg_calculations(
        infile  = (time_avg_file_dir+test_file_name),
        outfile = (time_avg_file_dir+'frepytools_timavg_'+test_file_name),
        pkg='fre-nctools',avg_type='all', unwgt=False )
    
def test_fre_nctools_month():
    # tests run of frenctools climatology with month flag
    assert run_avgtype_pkg_calculations(
        infile  = (time_avg_file_dir+test_file_name),
        outfile = (time_avg_file_dir+'frepytools_timavg_'+test_file_name),
        pkg='fre-nctools',avg_type='month', unwgt=False )
        
def test_path_frenctools_month():
    #tests if files are being generated in the right spot for frenctools monthly climatology
    run_avgtype_pkg_calculations(
        infile  = (time_avg_file_dir+test_file_name),
        outfile = (time_avg_file_dir+'frepytools_timavg_'+test_file_name),
        pkg='fre-nctools',avg_type='month', unwgt=False )
    assert pl.Path(time_avg_file_dir+'../monthly_output_files/April_out.nc').exists()
'''


