from fre_python_tools.utilities.subtract_durations import subtract_durations
import metomi.isodatetime.parsers as parse

def test_months():
    '''13 months - 3 months = 10 months'''
    ten_months = parse.DurationParser().parse('P10M')
    assert subtract_durations('P13M', 'P3M') == ten_months

def test_hour():
    '''2 hours minus 30 minutes = 90 minutes'''
    ninety_mins = parse.DurationParser().parse('PT90M')
    assert subtract_durations('PT2H', 'PT30M') == ninety_mins

def test_fail():
    '''2 hours minus 60 minutes != 90 minutes'''
    ninety_mins = parse.DurationParser().parse('PT90M')
    assert subtract_durations('PT2H', 'PT60M') != ninety_mins
