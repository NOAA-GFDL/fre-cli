#!/usr/bin/env python3
"""
***********************************************************************
*                   GNU Lesser General Public License
*
* This file is part of the GFDL Flexible Modeling System (FMS) YAML tools.
*
* FMS_yaml_tools is free software: you can redistribute it and/or modify it under
* the terms of the GNU Lesser General Public License as published by
* the Free Software Foundation, either version 3 of the License, or (at
* your option) any later version.
*
* FMS_yaml_tools is distributed in the hope that it will be useful, but WITHOUT
* ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
* FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
* for more details.
*
* You should have received a copy of the GNU Lesser General Public
* License along with FMS.  If not, see <http://www.gnu.org/licenses/>.
***********************************************************************
"""

""" Determine if a yaml data_table is valid.
    Run `python3 is_valid_data_table_yaml.py -h` for more details
    Author: Uriel Ramirez 05/27/2022
"""

import yaml
import sys
import click

def check_gridname(grid_name):
    """Check if the input grid_name is valid. Crashes if it not."""
    valid = ["OCN", "LND", "ATM", "ICE"]
    if (grid_name not in valid): raise Exception(grid_name+ ' is not a valid gridname. The only values allowed are "OCN", "LND", "ATM", "ICE"')

def check_fieldname_code(fieldname):
    if (fieldname == ""): raise Exception("Fieldname can't be empty")

def check_filename_and_field(field, interp_method):
    if (field =="" and interp_method != ""): raise Exception('If "fieldname_file" is empty, interp_method must be empty')

def check_interp_method(interp_method):
    """Check if the interp method is valid. Crashes if it not. """
    valid = ["bilinear", "bicubic", "none"]
    if (interp_method not in valid): raise Exception(interp_method + ' is not a valid interp_method. The only values allowed are "bilinear", "bicubic", and "none"')

def check_region_type(region_type):
    """Check if the input region type is valid. Crashes if it is not."""
    valid = ["inside_region", "outside_region"]
    if (region_type not in valid): raise Exception(region_type + 'is not a valid region_type. The only values allowed are "inside_region" and "outside_region"')

def check_if_bounds_present(entry):
    """Check if the region bounds are valid, crashes if they are not """
    if ("lat_start" not in entry): raise Exception('lat_start must be present if region_type is set')
    if ("lat_end" not in entry): raise Exception('lat_end must be present if region_type is set')
    if ("lon_start" not in entry): raise Exception('lon_start must be present if region_type is set')
    if ("lon_end" not in entry): raise Exception('lon_end must be present if region_type is set')

def check_region(my_type, start, end):
    """Check if the region is defined correctly. Crashes if it not. """
    if (start > end): raise Exception(my_type+"_start is greater than "+my_type+"_end")


def main():
    @click.command()
    @click.option('-f',
                    '--file',
                    type=str,
                    default="data_table",
                    help="Name of the data_table file to convert",
                    required=True)
    def is_valid_data_table_yaml(file):
        """
        Determines if a yaml data_table is valid. \
        Requires pyyaml (https://pyyaml.org/) \
        More details on the yaml format can be found in \
        https://github.com/NOAA-GFDL/FMS/tree/main/data_override"
        """
        with open(file, 'r') as fl:
            my_table = yaml.safe_load(fl)
            for key, value in my_table.items():
                for i in range(0, len(value)):
                    entry = value[i]
                    if "gridname" not in entry:
                        raise Exception("gridname is a required key!")
                    gridname = entry["gridname"]
                    check_gridname(gridname)

                    if "fieldname_code" not in entry:
                        raise Exception("fieldname_code is a required key!")

                    fieldname_code = entry["fieldname_code"]
                    check_fieldname_code(fieldname_code)

                    if "fieldname_file" in entry:
                        fieldname_file = entry["fieldname_file"]

                    if "file_name" in entry:
                        file_name = entry["file_name"]

                    if "interpol_method" in entry:
                        interp_method = entry["interpol_method"]

                    check_interp_method(interp_method)
                    check_filename_and_field(fieldname_file, interp_method)

                    if "factor" not in entry:
                        raise Exception("factor is a required key")

                    factor = entry["factor"]

                    if "region_type" in entry:
                        region_type = entry["region_type"]
                        check_region_type(region_type)
                        check_if_bounds_present(entry)

                        lat_start = entry["lat_start"]
                        lat_end = entry["lat_end"]
                        check_region("lat", lat_start, lat_end)

                        lon_start = entry["lon_start"]
                        lon_end = entry["lon_end"]
                        check_region("lon", lon_start, lon_end)


if __name__ == "__main__":
    main()
