#!/usr/bin/env python3
# ***********************************************************************
# *                   GNU Lesser General Public License
# *
# * This file is part of the GFDL Flexible Modeling System (FMS) YAML
# * tools.
# *
# * FMS_yaml_tools is free software: you can redistribute it and/or
# * modify it under the terms of the GNU Lesser General Public License
# * as published by the Free Software Foundation, either version 3 of the
# * License, or (at your option) any later version.
# *
# * FMS_yaml_tools is distributed in the hope that it will be useful, but
# * WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# * General Public License for more details.
# *
# * You should have received a copy of the GNU Lesser General Public
# * License along with FMS.  If not, see <http://www.gnu.org/licenses/>.
# ***********************************************************************

from os import path, strerror
import errno
import click
import yaml
from .. import __version__, TableParseError


""" Converts a legacy ascii data_table to a yaml data_table.
    Run `python3 data_table_to_yaml.py -h` for more details
    Author: Uriel Ramirez 05/27/2022
"""


class DataType:
    def __init__(self, data_table_file='data_table',
                 yaml_table_file='data_table.yaml',
                 force_write=False):
        """Initialize the DataType"""
        self.data_table_file = data_table_file
        self.yaml_table_file = yaml_table_file
        self.out_file_op = "x"  # Exclusive write
        if force_write:
            self.out_file_op = "w"

        self.data_type = {}
        self.data_type_keys = ['gridname',
                               'fieldname_code',
                               'fieldname_file',
                               'file_name',
                               'interpol_method',
                               'factor',
                               'lon_start',
                               'lon_end',
                               'lat_start',
                               'lat_end',
                               'region_type']
        self.data_type_values = {'gridname': str,
                                 'fieldname_code': str,
                                 'fieldname_file': str,
                                 'file_name': str,
                                 'interpol_method': str,
                                 'factor': float,
                                 'lon_start': float,
                                 'lon_end': float,
                                 'lat_start': float,
                                 'lat_end': float,
                                 'region_type': str}

        self.data_table_content = []

        #: check if data_table file exists
        if not path.exists(self.data_table_file):
            raise FileNotFoundError(errno.ENOENT,
                                    strerror(errno.ENOENT),
                                    data_table_file)

        # Check if path to the output yaml file exists
        if not path.exists(path.abspath(path.dirname(self.yaml_table_file))):
            raise NotADirectoryError(errno.ENOTDIR,
                                     "Directory does not exist",
                                     path.abspath(
                                        path.dirname(self.yaml_table_file)))

    def read_data_table(self):
        """Open and read the legacy ascii data_table file"""
        with open(self.data_table_file, 'r') as myfile:
            self.data_table_content = myfile.readlines()

    def parse_data_table(self):
        """Loop through each line in the ascii data_Table file and fill in
           data_type class"""
        iline_count = 0
        self.data_type['data_table'] = []
        for iline in self.data_table_content:
            iline_count += 1
            if iline.strip() != '' and '#' not in iline.strip()[0]:
                # get rid of comment at the end of line
                iline_list = iline.split('#')[0].split(',')
                try:
                    tmp_list = {}
                    for i in range(len(iline_list)):
                        mykey = self.data_type_keys[i]
                        myfunct = self.data_type_values[mykey]
                        myval = myfunct(
                            iline_list[i].strip('"\' \n'))
                        if i == 4:
                            # If LIMA format convert to the regular format
                            # #FUTURE
                            if ("true" in myval):
                                myval = 'bilinear'
                            if ("false" in myval):
                                myval = 'none'
                        tmp_list[mykey] = myval
                except Exception:
                    raise TableParseError(self.data_table_file,
                                          iline_count,
                                          iline)
                # If the fieldname_file is empty (i.e no interpolation just
                # multiplying by a constant), remove fieldname_file,
                # file_name, and interpol_method
                if (tmp_list['fieldname_file'] == ""):
                    del tmp_list['fieldname_file']
                    del tmp_list['file_name']
                    del tmp_list['interpol_method']
                self.data_type['data_table'].append(tmp_list)

    def read_and_parse_data_table(self):
        """Open, read, and parse the legacy ascii data_table file"""
        if self.data_table_content != []:
            self.data_table_content = []
        self.read_data_table()
        self.parse_data_table()

    def convert_data_table(self):
        """Convert the legacy ascii data_table file to yaml"""
        self.read_and_parse_data_table()

        with open(self.yaml_table_file, self.out_file_op) as myfile:
            yaml.dump(self.data_type, myfile, sort_keys=False)


def main():
    #: parse user input
    @click.command()
    @click.option('-f',
                    '--in_file',
                    type=str,
                    default="data_table",
                    help="Name of the data_table file to convert",
                    required=True)
    @click.option('-o',
                    '--output',
                    type=str,
                    default='data_table.yaml',
                    help="Ouput file name of the converted YAML \
                          (Default: 'diag_table.yaml')",
                    required=True)
    @click.option('-F'
                    '--force',
                    is_flag=True,
                    help="Overwrite the output data table yaml file.")
    @click.version_option(version='1.0',
                          prog_name='combine_data_table_yaml')
    def data_table_to_yaml(in_file, output, force):
        """
        Converts a legacy ascii data_table to a yaml data_table. \
        Requires pyyaml (https://pyyaml.org/) \
        More details on the data_table yaml format can be found \
        in \
        https://github.com/NOAA-GFDL/FMS/tree/main/data_override")
        """
        try:
            test_class = DataType(data_table_file=in_file,
                                  yaml_table_file=output,
                                  force_write=force)
            test_class.convert_data_table()
        except Exception as err:
            raise SystemError(err)


if __name__ == "__main__":
    main()
