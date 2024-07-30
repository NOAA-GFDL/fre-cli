from fre.pp.configure_script_yaml import quote_rose_values

def test_boolean():
    assert quote_rose_values(True) == 'True'

def test_string():
    assert quote_rose_values('foo') == "'foo'"
