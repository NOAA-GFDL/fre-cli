from fre_python_tools.utilities.multiply_duration import multiply_duration
import metomi.isodatetime.parsers as parse

def test_month():
    '''1 month x 2 = 2 months'''
    two_months = parse.DurationParser().parse('P2M')
    assert multiply_duration('P1M', 2) == two_months

def test_minutes():
    '''12 minutes x 5 = 1 hour'''
    hour = parse.DurationParser().parse('PT1H')
    assert multiply_duration('PT12M', 5) == hour

def test_fail():
    '''10 minutes x 5 != 1 hour'''
    hour = parse.DurationParser().parse('PT1H')
    assert multiply_duration('PT10M', 5) != hour
