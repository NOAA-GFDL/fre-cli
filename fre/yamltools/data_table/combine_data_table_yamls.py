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
from .. import __version__

""" Combines a series of data_table.yaml files into one file
    Author: Uriel Ramirez 04/11/2023
"""


def is_duplicate(data_table, new_entry):
    """
    Check if a data_table entry was already defined in a different file

    Args:
        data_table: List of dictionaries containing all of the data_table
                    entries that have been combined
        new_entry: Dictionary of the data_table entry to check
    """

    for entry in data_table:
        if entry == new_entry:
            is_duplicate = True
            return is_duplicate
        else:
            if entry['fieldname_code'] == new_entry['fieldname_code']:
                raise Exception("A data_table entry is defined twice for the "
                                "field_name_code:" + entry['fieldname_code'] +
                                " with different keys/values!")
    is_duplicate = False
    return is_duplicate


def combine_yaml(files):
    """
    Combines a list of yaml files into one

    Args:
        files: List of yaml file names to combine
    """
    data_table = {}
    data_table['data_table'] = []
    for f in files:
        # Check if the file exists
        if not path.exists(f):
            raise FileNotFoundError(errno.ENOENT,
                                    strerror(errno.ENOENT),
                                    f)

        with open(f) as fl:
            my_table = yaml.safe_load(fl)
            entries = my_table['data_table']
            for entry in entries:
                if not is_duplicate(data_table['data_table'], entry):
                    data_table['data_table'].append(entry)
    return data_table


def main():
    #: parse user input
    @click.command()
    @click.option('-f',
                    '--in_files',
                    type=str,
                    multiple=True,
                    default=["data_table"],
                    help='Space seperated list with the '
                         'Names of the data_table.yaml files to combine',
                    required=True)
    @click.option('-o',
                    '--out_file',
                    type=str,
                    default='data_table.yaml',
                    help="Ouput file name of the converted YAML \
                          (Default: 'diag_table.yaml')",
                    required=True)
    @click.option('-F'
                    '--force',
                    is_flag=True,
                    help="Overwrite the output data table yaml file.")
    @click.version_option(version=__version__,
                          prog_name='combine_data_table_yaml')
    def combine_data_table_yaml(in_files, out_file, force):
        """
        Combines a list of data_table.yaml files into one file" + "Requires pyyaml (https://pyyaml.org/)
        """
        try:
            data_table = combine_yaml(in_files)
            out_file_op = "x"  # Exclusive write
            if force:
                out_file_op = "w"
            with open(out_file, out_file_op) as myfile:
                yaml.dump(data_table, myfile, default_flow_style=False)
        except Exception as err:
            raise SystemExit(err)


if __name__ == "__main__":
    main()
