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

""" Combines a series of diag_table.yaml files into one file
    Author: Uriel Ramirez 04/11/2023
"""


def compare_key_value_pairs(entry1, entry2, key, is_optional=False):
    if not is_optional:
        if entry1[key] != entry2[key]:
            raise Exception("The diag_file:" + entry1['file_name'] + " is defined twice " +
                            " with different " + key)
    else:
        if key not in entry1 and key not in entry2:
            return
        if key in entry1 and key in entry2:
            if entry1[key] != entry2[key]:
                raise Exception("The diag_file:" + entry1['file_name'] + " is defined twice " +
                                " with different " + key)
        if key in entry1 and key not in entry2:
            raise Exception("The diag_file:" + entry1['file_name'] + " is defined twice " +
                            " with different " + key)
        if key not in entry1 and key in entry2:
            raise Exception("The diag_file:" + entry1['file_name'] + " is defined twice " +
                            " with different " + key)


def is_field_duplicate(diag_table, new_entry, file_name):
    for entry in diag_table:
        if entry == new_entry:
            return True
        else:
            if entry['var_name'] != new_entry['var_name']:
                # If the variable name is not the same, then it is a brand new variable
                return False
            elif entry['var_name'] == new_entry['var_name'] and entry['module'] != new_entry['module']:
                # If the variable name is the same but it a different module, then it is a brand new variable
                return False
            else:
                raise Exception("The variable " + entry['var_name'] + " from module " + entry['module'] +
                                " in file " + file_name + " is defined twice with different keys")


def is_file_duplicate(diag_table, new_entry):
    # Check if a diag_table entry was already defined
    for entry in diag_table:
        if entry == new_entry:
            return True
        else:
            # If the file_name is not the same, then it is a brand new file
            if entry['file_name'] != new_entry['file_name']:
                return False

            # Since there are duplicate files, check fhat all the keys are the same:
            compare_key_value_pairs(entry, new_entry, 'freq')
            compare_key_value_pairs(entry, new_entry, 'time_units')
            compare_key_value_pairs(entry, new_entry, 'unlimdim')

            compare_key_value_pairs(entry, new_entry, 'write_file', is_optional=True)
            compare_key_value_pairs(entry, new_entry, 'new_file_freq', is_optional=True)
            compare_key_value_pairs(entry, new_entry, 'start_time', is_optional=True)
            compare_key_value_pairs(entry, new_entry, 'file_duration', is_optional=True)
            compare_key_value_pairs(entry, new_entry, 'global_meta', is_optional=True)
            compare_key_value_pairs(entry, new_entry, 'sub_region', is_optional=True)
            compare_key_value_pairs(entry, new_entry, 'is_ocean', is_optional=True)

            # Since the file is the same, check if there are any new variables to add to the file:
            for field_entry in new_entry['varlist']:
                if not is_field_duplicate(entry['varlist'], field_entry, entry['file_name']):
                    entry['varlist'].append(field_entry)
            return True


def combine_yaml(files):
    diag_table = {}
    diag_table['title'] = ""
    diag_table['base_date'] = ""
    diag_table['diag_files'] = []
    for f in files:
        # Check if the file exists
        if not path.exists(f):
            raise FileNotFoundError(errno.ENOENT,
                                    strerror(errno.ENOENT),
                                    f)

        with open(f) as fl:
            my_table = yaml.safe_load(fl)

        if 'base_date' in my_table:
            diag_table['base_date'] = my_table['base_date']
        if 'title' in my_table:
            diag_table['title'] = my_table['title']

        if 'diag_files' not in my_table:
            continue

        diag_files = my_table['diag_files']
        for entry in diag_files:
            if not is_file_duplicate(diag_table['diag_files'], entry):
                diag_table['diag_files'].append(entry)
    return diag_table


def main():
    #: parse user input
    @click.command()
    @click.option('-f',
                    '--in_files',
                    type=str,
                    multiple=True,
                    default=["diag_table"],
                    help='Space seperated list with the '
                        'Names of the diag_table.yaml files to combine')
    @click.option('-o',
                    '--out_file',
                    type=str,
                    default='diag_table.yaml',
                    help="Ouput file name of the converted YAML \
                          (Default: 'diag_table.yaml')")
    @click.option('-F',
                    '--force',
                    is_flag=True,
                    help="Overwrite the output diag table yaml file.")
    @click.version_option(version=__version__,
                          prog_name='combine_diag_table_yaml')
    def combine_diag_table_yaml(in_files, out_file, force):
        """
        Combines a series of diag_table.yaml files into one file
        Requires pyyaml (https://pyyaml.org/)
        """
        try:
            diag_table = combine_yaml(in_files)
            out_file_op = "x"  # Exclusive write
            if force:
                out_file_op = "w"
            with open(out_file, out_file_op) as myfile:
                yaml.dump(diag_table, myfile, default_flow_style=False, sort_keys=False)

        except Exception as err:
            raise SystemExit(err)


if __name__ == "__main__":
    main()
