"""
experimentation file for integrating one file's functions into main prototype fre file
authored by Bennett.Chang@noaa.gov | bcc2761
NOAA | GFDL
"""


def check_test_function(uppercase=None):
    """Execute fre list testfunction2."""
    statement = "testingtestingtestingtesting"
    if uppercase:
        statement = statement.upper()
    print(statement)


if __name__ == '__main__':
    check_test_function()
