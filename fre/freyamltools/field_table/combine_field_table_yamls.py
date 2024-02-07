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

""" Combines a series of field_table.yaml files into one file
    Author: Uriel Ramirez 11/20/2023
"""


def is_duplicate(field_table, new_entry):
    """
    Check if a field_table entry was already defined in a different file

    Args:
        field_table: List of dictionaries containing all of the field_table
                    entries that have been combined
        new_entry: Dictionary of the field_table entry to check
    """
    is_duplicate = False
    return is_duplicate

def field_type_exists(field_type, curr_entries):
    for entry in curr_entries:
        if field_type == entry['field_type']:
            return True
    return False

def add_new_field(new_entry, curr_entries):
    new_field_type = new_entry['field_type']
    for entry in curr_entries:
        if new_field_type == entry['field_type']:
            if entry == new_entry:
                # If the field_type already exists but it is exactly the same, move on
                continue
            new_modlist = new_entry['modlist']
            for mod in new_modlist:
                if model_type_exists(mod['model_type'], entry):
                    add_new_mod(mod, entry)
                else:
                    #If the model type does not exist, just append it
                    entry['modlist'].append(mod)

def add_new_mod(new_mod, curr_entries):
    model_type = new_mod['model_type']
    for entry in curr_entries['modlist']:
        if model_type == entry['model_type']:
            if new_mod == entry:
                # If the model_type already exists but it is exactly the same, move on
                continue
            new_varlist = new_mod['varlist']
            curr_varlist = entry['varlist']
            for new_var in new_varlist:
                for curr_var in curr_varlist:
                    if new_var == curr_var:
                        continue
                curr_varlist.append(new_var)    

def model_type_exists(model_type, curr_entries):
    for entry in curr_entries['modlist']:
        if model_type == entry['model_type']:
            return True
    return False

def combine_yaml(files):
    """
    Combines a list of yaml files into one

    Args:
        files: List of yaml file names to combine
    """
    field_table = {}
    field_table['field_table'] = []
    for f in files:
        print("File:" + f)
        # Check if the file exists
        if not path.exists(f):
            raise FileNotFoundError(errno.ENOENT,
                                    strerror(errno.ENOENT),
                                    f)
        with open(f) as fl:
            my_table = yaml.safe_load(fl)
            entries = my_table['field_table']
            for entry in entries:
                if not field_type_exists(entry['field_type'], field_table['field_table']):
                    #  If the field table does not exist, just add it to the current field table
                    field_table['field_table'].append(entry)
                else:
                    add_new_field(entry, field_table['field_table'])
    return field_table

def main():
    #: parse user input
    @click.command()
    @click.option('-f',
                    '--in_files',
                    type=str,
                    multiple=True,
                    default=["field_table"],
                    help='Space seperated list with the '
                         'Names of the field_table.yaml files to combine')
    @click.option('-o',
                    '--out_file',
                    type=str,
                    default='field_table.yaml',
                    help="Ouput file name of the converted YAML \
                          (Default: 'field_table.yaml')")
    @click.option('-F',
                    '--force',
                    is_flag=True,
                    help="Overwrite the output field table yaml file.")
    @click.version_option(version=__version__,
                          prog_name="combine_field_table_yaml")
    def combine_field_table_yaml(in_files, out_file, force):
        """
        Combines a list of field_table.yaml files into one file
        Requires pyyaml (https://pyyaml.org/)
        """
        try:
            field_table = combine_yaml(in_files)
            out_file_op = "x"  # Exclusive write
            if force:
                out_file_op = "w"
            with open(out_file, out_file_op) as myfile:
                yaml.dump(field_table, myfile, default_flow_style=False)

        except Exception as err:
            raise SystemExit(err)
  

if __name__ == "__main__":
    main()