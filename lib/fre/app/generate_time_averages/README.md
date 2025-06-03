From an input netCDF file, output a time-averaged netCDF file.

Will average all available information on a given variable across time,
but can also handle monthly+seasonal averaging.

To run time-averaging tests, return to root directory and call just those
tests with `python -m pytest tests/test_generate_time_averages.py`, or run
all tests with `python -m pytests tests/`