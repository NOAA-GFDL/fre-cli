''' quick tests to make sure rose handles certain types of values with quotes correctly '''
from fre.pp.configure_script_yaml import quote_rose_values

def test_boolean():
    ''' check that boolean values with quotes are handled correctly by rose'''
    assert quote_rose_values(True) == 'True'

def test_string():
    ''' check that string values with quotes are handled correctly by rose'''
    assert quote_rose_values('foo') == "'foo'"
