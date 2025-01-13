"""
experimentation file for integrating one file's functions into main prototype fre file
authored by Bennett.Chang@noaa.gov | bcc2761
NOAA | GFDL
"""

def test_test_function(uppercase=None):
    """Execute fre list test_test_function"""
    statement = "testingtestingtestingtesting"
    if uppercase:
        statement = statement.upper()
    print(statement)

if __name__ == '__main__':
    test_test_function()
