#!/usr/bin/env python3
# ***********************************************************************
# *                   GNU Lesser General Public License
# *
# * This file is part of the GFDL Flexible Modeling System (FMS) YAML tools.
# *
# * FMS_yaml_tools is free software: you can redistribute it and/or modify it under
# * the terms of the GNU Lesser General Public License as published by
# * the Free Software Foundation, either version 3 of the License, or (at
# * your option) any later version.
# *
# * FMS_yaml_tools is distributed in the hope that it will be useful, but WITHOUT
# * ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# * FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
# * for more details.
# *
# * You should have received a copy of the GNU Lesser General Public
# * License along with FMS.  If not, see <http://www.gnu.org/licenses/>.
# ***********************************************************************

""" Converts a legacy ascii diag_table to a yaml diag_table.
    Run `python3 diag_table_to_yaml.py -h` for more details
    Author: Uriel Ramirez 05/27/2022
"""

import copy as cp
from os import path
import click
import yaml
from .. import __version__#, TableParseError

def main():
    #: parse user input
    @click.command()
    @click.option('-f'
                  '--in_file',
                  type=str,
                  help='Name of the diag_table to convert')
    @click.option('-s',
                  '--is_segment',
                  is_flag=True,
                  help='The diag_table is a segment and a not a full table, \
                        so the tile and the base_date are not expected')
    @click.option('-o',
                  '--out_file',
                  type=str,
                  default='diag_table.yaml',
                  help="Ouput file name of the converted YAML \
                        (Default: 'diag_table.yaml')")
    @click.option('-F',
                  '--force',
                  is_flag=True,
                  help="Overwrite the output data table yaml file.")
    @click.version_option(__version__,
                          prog_name='diag_table_to_yaml')
    def diag_table_to_yaml(in_file, is_segment, out_file, force):
        """
        Converts a legacy ascii diag_table to a yaml diag_table
        Requires pyyaml (https://pyyaml.org)
        More details on the diag_table yaml format can be found in
        https://github.com/NOAA-GFDL/FMS/tree/main/diag_table
        """
        #: start
        test_class = DiagTable(diag_table_file=in_file, is_segment=is_segment)
        test_class.read_and_parse_diag_table()
        test_class.construct_yaml(yaml_table_file=out_file, force_write=force)


def is_duplicate(current_files, diag_file):

    """
    Determine if a diag file has already been defined.

    Args:
        current_files (list): List of dictionary containing all the diag files that have been defined
        diag_file (dictionary): Dictionary defining a diag file

    Returns:
        logical: If the diag_file has been defined and has the same keys, returns True
                 If it has been defined but it does not have the same keys, return an error
                 If it has not been defined, return False
    """
    for curr_diag_file in current_files['diag_files']:
        if curr_diag_file['file_name'] != diag_file['file_name']:
            continue
        if curr_diag_file == diag_file:
            return True
        else:
            raise Exception("The diag_table defines " + diag_file['file_name'] + " more than once with different keys")
    return False


class DiagTable:
    def __init__(self, diag_table_file='Diag_Table', is_segment=False):
        '''Initialize the diag_table type'''

        self.diag_table_file = diag_table_file
        self.is_segment = is_segment
        self.global_section = {}
        self.global_section_keys = ['title', 'base_date']
        self.global_section_fvalues = {'title': str,
                                       'base_date': [int, int, int, int, int, int]}
        self.max_global_section = len(self.global_section_keys) - 1  # minus title

        self.file_section = []
        self.file_section_keys = ['file_name',
                                  'freq_int',
                                  'freq_units',
                                  'time_units',
                                  'unlimdim',
                                  'new_file_freq_int',
                                  'new_file_freq_units',
                                  'start_time',
                                  'file_duration_int',
                                  'file_duration_units',
                                  'filename_time_bounds']
        self.file_section_fvalues = {'file_name': str,
                                     'freq_int': int,
                                     'freq_units': str,
                                     'time_units': str,
                                     'unlimdim': str,
                                     'new_file_freq_int': int,
                                     'new_file_freq_units': str,
                                     'start_time': str,
                                     'file_duration_int': int,
                                     'file_duration_units': str,
                                     'filename_time_bounds': str}
        self.max_file_section = len(self.file_section_keys)

        self.region_section = []
        self.region_section_keys = ['grid_type',
                                    'corner1',
                                    'corner2',
                                    'corner3',
                                    'corner4',
                                    'zbounds',
                                    'is_only_zbounds',
                                    'file_name'
                                    'line']
        self.region_section_fvalues = {'grid_type': str,
                                       'corner1': [float, float],
                                       'corner2': [float, float],
                                       'corner3': [float, float],
                                       'corner4': [float, float],
                                       'zbounds': [float, float],
                                       'is_only_zbounds': bool,
                                       'file_name': str,
                                       'line': str}
        self.max_file_section = len(self.file_section_keys)
        self.field_section = []
        self.field_section_keys = ['module',
                                   'var_name',
                                   'output_name',
                                   'file_name',
                                   'reduction',
                                   'spatial_ops',
                                   'kind',
                                   'zbounds']
        self.field_section_fvalues = {'module': str,
                                      'var_name': str,
                                      'output_name': str,
                                      'file_name': str,
                                      'reduction': str,
                                      'spatial_ops': str,
                                      'kind': str,
                                      'zbounds': str}
        self.max_field_section = len(self.field_section_keys)

        self.diag_table_content = []

        #: check if diag_table file exists
        if not path.exists(self.diag_table_file):
            raise Exception('file ' + self.diag_table_file + ' does not exist')

    def read_diag_table(self):
        """ Open and read the diag_table"""
        with open(self.diag_table_file, 'r') as myfile:
            self.diag_table_content = myfile.readlines()

    def set_sub_region(self, myval, field_dict):
        """
        Loop through the defined sub_regions, determine if the file already has a sub_region defined
        if it does crash. If the sub_region is not already defined add the region to the list

        Args:
            myval (string): Defines the subregion as read from the diag_table in the format
                            [starting x, ending x, starting y, ending y, starting z, ending z]
            field_dict(dictionary): Defines the field
        """
        tmp_dict2 = {}
        file_name = field_dict['file_name']
        found = False
        is_same = True
        for iregion_dict in self.region_section:
            if iregion_dict['file_name'] == file_name:
                found = True
                if iregion_dict['line'] != myval:
                    """
                    Here the file has a already a sub_region defined and it is not the same as the current
                    subregion.
                    """
                    is_same = False
        if (found and is_same):
            return

        tmp_dict2["line"] = myval
        tmp_dict2["file_name"] = file_name
        if "none" in myval:
            tmp_dict2[self.region_section_keys[0]] = myval
        else:
            tmp_dict2[self.region_section_keys[0]] = "latlon"
            stuff = myval.split(' ')
            k = -1
            for j in range(len(stuff)):
                if (stuff[j] == ""):
                    continue  # Some lines have extra spaces ("1 10  9 11 -1 -1")
                k = k + 1

                # Set any -1 values to -999
                if float(stuff[j]) == -1:
                    stuff[j] = "-999"

                # Define the 4 corners and the z bounds
                if k == 0:
                    corner1 = stuff[j]
                    corner2 = stuff[j]
                elif k == 1:
                    corner3 = stuff[j]
                    corner4 = stuff[j]
                elif k == 2:
                    corner1 = corner1 + ' ' + stuff[j]
                    corner2 = corner2 + ' ' + stuff[j]
                elif k == 3:
                    corner3 = corner3 + ' ' + stuff[j]
                    corner4 = corner4 + ' ' + stuff[j]
                elif k == 4:
                    zbounds = stuff[j]
                elif k == 5:
                    zbounds = zbounds + ' ' + stuff[j]

            tmp_dict2["corner1"] = corner1
            tmp_dict2["corner2"] = corner2
            tmp_dict2["corner3"] = corner3
            tmp_dict2["corner4"] = corner4
            tmp_dict2["zbounds"] = zbounds
            tmp_dict2["is_only_zbounds"] = False
            field_dict['zbounds'] = zbounds

            if corner1 == "-999 -999" and corner2 == "-999 -999" and corner3 == "-999 -999" and corner4 == "-999 -999":
                tmp_dict2["is_only_zbounds"] = True
            elif not is_same:
                raise Exception("The " + file_name + " has multiple sub_regions defined. Be sure that all the variables"
                                "in the file are in the same sub_region! "
                                "Region 1:" + myval + "\n"
                                "Region 2:" + iregion_dict['line'])
        self.region_section.append(cp.deepcopy(tmp_dict2))

    def parse_diag_table(self):
        """ Loop through each line in the diag_table and parse it"""

        if self.diag_table_content == []:
            raise Exception('ERROR:  The input diag_table is empty!')

        iline_count, global_count = 0, 0

        if self.is_segment:
            global_count = 2

        #: The first two lines should be the title and base_time
        while global_count < 2:
            iline = self.diag_table_content[iline_count]
            iline_count += 1
            # Ignore comments and empty lines
            if iline.strip() != '' and '#' not in iline.strip()[0]:
                #: The second uncommented line is the base date
                if global_count == 1:
                    try:
                        iline_list, tmp_list = iline.split('#')[0].split(), []  #: not comma separated integers
                        mykey = self.global_section_keys[1]
                        self.global_section[mykey] = iline.split('#')[0].strip()
                        global_count += 1
                    except:
                        raise Exception(" ERROR with line # " + str(iline_count) + '\n'
                                        " CHECK:            " + str(iline) + '\n'
                                        " Ensure that the second uncommented line of the diag table defines \n"
                                        " the base date in the format [year month day hour min sec]")
                #: The first uncommented line is the title
                if global_count == 0:
                    try:
                        mykey = self.global_section_keys[0]
                        myfunct = self.global_section_fvalues[mykey]
                        myval = myfunct(iline.strip().strip('"').strip("'"))
                        self.global_section[mykey] = myval
                        global_count += 1
                    except:
                        raise Exception(" ERROR with line # " + str(iline_count) + '\n'
                                        " CHECK:            " + str(iline) + '\n'
                                        " Ensure that the first uncommented line of the diag table defines the title")

        #: The rest of the lines are either going to be file or field section
        for iline_in in self.diag_table_content[iline_count:]:
            iline = iline_in.strip().strip(',')  # get rid of any leading spaces and the comma that some file lines have in the end #classic
            iline_count += 1
            if iline.strip() != '' and '#' not in iline.strip()[0]:  # if not blank line or comment
                iline_list = iline.split('#')[0].split(',')  # get rid of any comments in the end of a line
                try:
                    #: Fill in the file section
                    tmp_dict = {}
                    for i in range(len(iline_list)):
                        j = i
                        # Do not do anything with the "file_format" column
                        if (i == 3):
                            continue
                        if (i > 3):
                            j = i - 1
                        mykey = self.file_section_keys[j]
                        myfunct = self.file_section_fvalues[mykey]
                        myval = myfunct(iline_list[i].strip().strip('"').strip("'"))

                        # Ignore file_duration if it less than 0
                        if (i == 9 and myval <= 0):
                            continue

                        # Ignore the file_duration_units if it is an empty string
                        if (i == 10 and myval == ""):
                            continue
                        tmp_dict[mykey] = myval
                    self.file_section.append(cp.deepcopy(tmp_dict))
                except:
                    #: Fill in the field section
                    try:
                        tmp_dict = {}
                        for i in range(len(self.field_section_keys)):
                            j = i
                            buf = iline_list[i]
                            # Do nothing with the "time_sampling" section
                            if (i == 4):
                                continue
                            if (i > 4):
                                j = i - 1
                            if (i == 5):
                                # Set the reduction to average or none instead of the other options
                                if "true" in buf.lower() or "avg" in buf.lower() or "mean" in buf.lower():
                                    buf = "average"
                                elif "false" in buf.lower():
                                    buf = "none"

                            # Set the kind to either "r4" or "r8"
                            if (i == 7):
                                if ("2" in buf):
                                    buf = "r4"
                                elif ("1" in buf):
                                    buf = "r8"
                                else:
                                    raise Exception(" ERROR with line # " + str(iline_count) + '\n'
                                                    " CHECK:            " + str(iline) + '\n'
                                                    " Ensure that kind is either 1 or 2")
                            mykey = self.field_section_keys[j]
                            myfunct = self.field_section_fvalues[mykey]
                            myval = myfunct(buf.strip().strip('"').strip("'"))

                            # Do not add the region to the field section. This will be added to the file later
                            if (i != 6):
                                tmp_dict[mykey] = myval
                            else:
                                self.set_sub_region(myval, tmp_dict)
                        self.field_section.append(cp.deepcopy(tmp_dict))
                    except:
                        raise Exception(" ERROR with line # " + str(iline_count) + '\n'
                                        " CHECK:            " + str(iline) + '\n'
                                        " Ensure that the line defines a field in the format: \n"
                                        " 'module_name', 'field_name', 'output_name', 'file_name', 'time_sampling', 'reduction_method',"
                                        " 'regional_section', 'packing' \n"
                                        " Or that the line defined a file in the format: \n"
                                        " 'file_name', 'output_freq', 'output_freq_units', 'file_format', "
                                        " 'time_axis_units', 'time_axis_name' "
                                        " 'new_file_freq', 'new_file_freq_units', 'start_time', 'file_duration', 'file_duration_units'")

    def construct_yaml(self,
                       yaml_table_file='diag_table.yaml',
                       force_write=False):
        """ Combine the global, file, field, sub_region sections into 1 """

        out_file_op = "x" # Exclusive write
        if force_write:
            out_file_op = "w"

        yaml_doc = {}
        #: title

        if not self.is_segment:
            mykey = self.global_section_keys[0]
            yaml_doc[mykey] = self.global_section[mykey]
            #: basedate
            mykey = self.global_section_keys[1]
            yaml_doc[mykey] = self.global_section[mykey]

        #: diag_files
        yaml_doc['diag_files'] = []
        #: go through each file
        for ifile_dict in self.file_section:  #: file_section = [ {}, {}, {} ]
            if 'ocean' in ifile_dict['file_name']:
                ifile_dict['is_ocean'] = True
            ifile_dict['sub_region'] = []

            # Combine freq_int and freq_units into 1 key
            ifile_dict['freq'] = str(ifile_dict['freq_int']) + ' ' + ifile_dict['freq_units']
            del ifile_dict['freq_int']
            del ifile_dict['freq_units']

            # Combine new_file_freq_int and new_file_freq_units into 1 key
            if "new_file_freq_int" in ifile_dict:
                ifile_dict['new_file_freq'] = str(ifile_dict['new_file_freq_int']) + ' ' + ifile_dict['new_file_freq_units']
                del ifile_dict['new_file_freq_int']
                del ifile_dict['new_file_freq_units']

            # Combine file_duration_int and file_duration_units into 1 key
            if "file_duration_int" in ifile_dict:
                ifile_dict['file_duration'] = str(ifile_dict['file_duration_int']) + ' ' + ifile_dict['file_duration_units']
                del ifile_dict['file_duration_int']
                del ifile_dict['file_duration_units']

            found = False
            for iregion_dict in self.region_section:
                if iregion_dict['file_name'] == ifile_dict['file_name']:
                    tmp_dict = cp.deepcopy(iregion_dict)
                    del tmp_dict['file_name']
                    del tmp_dict['line']
                    if (tmp_dict['grid_type'] != "none"):
                        ifile_dict['sub_region'].append(tmp_dict)
                        found = True
                        if tmp_dict['is_only_zbounds']:
                            found = False
                        del tmp_dict['is_only_zbounds']
                        del tmp_dict['zbounds']
            if not found:
                del ifile_dict['sub_region']

            ifile_dict['varlist'] = []
            found = False
            for ifield_dict in self.field_section:  #: field_section = [ {}, {}. {} ]
                if ifield_dict['file_name'] == ifile_dict['file_name']:
                    tmp_dict = cp.deepcopy(ifield_dict)

                    # Ensure that the output_name contains "min"
                    # if the reduction method is "min"
                    if tmp_dict['reduction'] == "min" and "min" not in tmp_dict['output_name']:
                        tmp_dict['output_name'] = tmp_dict['output_name'] + "_min"

                    # Ensure that the output_name contains "max"
                    # if the reduction method is "max"
                    if tmp_dict['reduction'] == "max" and "max" not in tmp_dict['output_name']:
                        tmp_dict['output_name'] = tmp_dict['output_name'] + "_max"

                    # If the output_name and the var_name are the same
                    # there is no need for output_name
                    if tmp_dict['output_name'] == tmp_dict['var_name']:
                        del tmp_dict['output_name']

                    del tmp_dict['file_name']
                    ifile_dict['varlist'].append(tmp_dict)
                    found = True
                    continue
            if not found:
                del ifile_dict['varlist']
            if not is_duplicate(yaml_doc, ifile_dict):
                yaml_doc['diag_files'].append(ifile_dict)
        myfile = open(yaml_table_file, out_file_op)
        yaml.dump(yaml_doc, myfile, sort_keys=False)

    def read_and_parse_diag_table(self):
        """ Read and parse the file """
        self.read_diag_table()
        self.parse_diag_table()


if __name__ == "__main__":
    main()
