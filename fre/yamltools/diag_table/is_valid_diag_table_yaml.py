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
    Determine if a yaml diag_table is valid.
    Run `python3 is_valid_diag_table_yaml.py -h` for more details
    Author: Uriel Ramirez 05/27/2022
"""

import sys
import argparse
import yaml

parser = argparse.ArgumentParser(prog='is_valid_diag_table_yaml', \
                                 description="Determine if a yaml diag_table is valid. \
                                              Requires pyyaml (https://pyyaml.org/) \
                                              More details on the yaml format can be found in \
                                              https://github.com/NOAA-GFDL/FMS/tree/main/diag_table")
parser.add_argument('-f', type=str, help='Name of the diag_table yaml to check' )

in_diag_table = parser.parse_args().f

class UniqueKeyLoader(yaml.SafeLoader):
  """ Special loader to check if duplicate keys are present"""
  def construct_mapping(self, node, deep=False):
    mapping = []
    for key_node, value_node in node.value:
      key = self.construct_object(key_node, deep=deep)
      if key in mapping : sys.exit('ERROR: You have defined the key:' + key + ' multiple times')
      mapping.append(key)
    return super().construct_mapping(node, deep)

def check_time_units(file_name, key_name, time_units) :
  """Check if the input time_units are valid, crashes if they are not """
  valid = ["seconds", "minutes", "hours", "days", "months", "years"]
  if (time_units not in valid) :
    sys.exit('ERROR: ' + time_units + ' is not a valid unit. Check your ' + key_name + ' entry for file:' + file_name)

def check_freq(file_name, freq, freq_units) :
  """Check if the input freq is valid, crashes if they are not """
  if (freq < -1) : sys.exit('ERROR: freq needs to greater than -1. Check your freq entry for file:' + file_name)
  check_time_units(file_name, 'freq_units', freq_units)

def check_required_diag_files_key(diag_file) :
  """Checks if all the required key are present in diag_file block. Crashes if any are missing."""
  if 'file_name' not in diag_file : sys.exit('ERROR: file_name is a required key!')
  if 'freq' not in diag_file : sys.exit('ERROR: freq is a required key! Add it for file:' + diag_file['file_name'])
  if 'freq_units' not in diag_file : sys.exit('ERROR: freq_units is a required key! Add it for file:' + diag_file['file_name'])
  if 'time_units' not in diag_file : sys.exit('ERROR: time_units is a required key! Add it for file:' + diag_file['file_name'])
  if 'unlimdim' not in diag_file : sys.exit('ERROR: unlimdim is a required key! Add it for file:' + diag_file['file_name'])

def check_new_file_freq(diag_file) :
  """Check if the input new_file_freq and new_file_freq_units are valid, crashes if they are not """
  if 'new_file_freq' in diag_file :
    if 'new_file_freq_units' not in diag_file :
      sys.exit('ERROR: new_file_freq is present, but not new_file_freq_units. Check you entry for file:' + diag_file['file_name'])
    if (diag_file['new_file_freq'] < 1) :
      sys.exit('ERROR: new_file_freq needs to be greater than 0. Check your new_file_freq for ' + diag_file['file_name'])
    check_time_units(diag_file['file_name'], 'new_file_freq_units', diag_file['new_file_freq_units'])
  else:
    if 'new_file_freq_units' in diag_file :
      sys.exit('ERROR: new_file_freq_units is present, but not new_file_freq. Check your entry for file:' + diag_file['file_name'])

def check_file_duration(diag_file) :
  """Check if the input file_duration and file_duration_units are valid, crashes if they are not """
  if 'file_duration' in diag_file :
    if 'file_duration_units' not in diag_file :
      sys.exit('ERROR: file_duration is present, but not file_duration_units. Check you entry for file:' + diag_file['file_name'])
    if (diag_file['file_duration'] < 1) :
      sys.exit('ERROR: file_duration_units needs to be greater than 0. Check your file_duration_units for ' + diag_file['file_name'])
    check_time_units(diag_file['file_name'], 'file_duration_units', diag_file['file_duration_units'])
  else:
    if 'file_duration_units' in diag_file :
      sys.exit('ERROR: file_duration_units is present, but not file_duration. Check your entry for file:' + diag_file['file_name'])

def check_start_time(diag_file) :
  """Check if the start_time is valid, crashes if it is not """
  if 'start_time' not in diag_file : return
  if 'file_duration' not in diag_file :
    sys.exit('ERROR: file_duration is needed if start_time is present. Check your entry for file:' + diag_file['file_name'])
  check_date(diag_file['start_time'], 'start_time')

def check_sub_region(diag_file) :
  """Check if the sub_regeion is defined correctly, crashes if it is not """
  if 'sub_region' not in diag_file : return

  sub_regions = diag_file['sub_region']
  sub_region = sub_regions[0]

  valid = ["latlon", "index"]
  if 'grid_type' not in sub_region :
    sys.exit('ERROR: grid_type is required if defining a sub_region. Add it your file:' + diag_file['file_name'])

  if sub_region['grid_type'] not in valid:
    sys.exit('ERROR: the grid_type (' + sub_region['grid_type'] + ') and file:' + diag_file['file_name']+ ' is not valid')

  if 'dim1_begin' in sub_region and 'dim1_end' in sub_region :
    if sub_region['dim1_begin'] > sub_region['dim1_end'] :
      sys.exit('ERROR: dim1_begin in your subregion of file:' + diag_file['file_name']+ ' is greater than dim1_end')

  if 'dim2_begin' in sub_region and 'dim2_end' in sub_region :
    if sub_region['dim2_begin'] > sub_region['dim2_end'] :
      sys.exit('ERROR: dim2_begin in your subregion of file:' + diag_file['file_name']+ ' is greater than dim2_end')

  if 'dim3_begin' in sub_region and 'dim3_end' in sub_region :
    if sub_region['dim3_begin'] > sub_region['dim3_end'] :
      sys.exit('ERROR: dim3_begin in your subregion of file:' + diag_file['file_name']+ ' is greater than dim3_end')

  if 'dim4_begin' in sub_region and 'dim4_end' in sub_region :
    if sub_region['dim4_begin'] > sub_region['dim4_end'] :
      sys.exit('ERROR: dim4_begin in your subregion of file:' + diag_file['file_name']+ ' is greater than dim4_end')

def check_diag_file(diag_file) :
  """Check if the diag_file is defined correctly. Crashes if it is not. """
  check_required_diag_files_key(diag_file)
  check_freq(diag_file['file_name'], diag_file['freq'], diag_file['freq_units'])
  check_time_units(diag_file['file_name'], 'time_units', diag_file['time_units'])
  check_new_file_freq(diag_file)
  check_file_duration(diag_file)
  check_start_time(diag_file)
  check_sub_region(diag_file)

def check_required_diag_field_key(diag_field, file_name):
  """Check if all the required keys in the diag_field are present, crashes if any are missing """
  if 'var_name' not in diag_field :
    sys.exit('ERROR: var_name is a required field! Check your var_name in file: ' + file_name)
  if 'module' not in diag_field :
    sys.exit('ERROR: module is a required field! Add it for variable:' + diag_field['var_name'] + ' in file: ' + file_name)
  if 'reduction' not in diag_field :
    sys.exit('ERROR: reduction is a required field! Add it for variable:' + diag_field['var_name'] + ' in file: ' + file_name)
  if 'kind' not in diag_field :
    sys.exit('ERROR: kind is a required field! Add it for variable:' + diag_field['var_name'] + ' in file: ' + file_name)

def check_date(date_str, date_name):
  """Check if the input date is valid, crashes if it is not """
  date_int = date_str.split() # [yr month day hour minute second]
  if (len(date_int) != 6 ) :
    sys.exit('ERROR: The size of ' + date_name + ' (' + date_str + ') should be 6')
  if int(date_int[1]) <= 0 :
    sys.exit('ERROR: The month in the ' + date_name + ' (' + date_str + ') should greater than 0')
  if int(date_int[2]) <= 0 :
    sys.exit('ERROR: The day in the ' + date_name + ' (' + date_str + ') should be greater than 0')

def check_reduction(diag_field, file_name):
  """Check if the reduction is valid, crashes if it is not """
  valid = ["none", "average", "min", "max", "rms"]
  reduction = diag_field['reduction']

  if "diurnal" in reduction :
    if int(reduction[7:9]) < 0 :
      sys.exit('ERROR: The number of diurnal samples in ' + reduction + ' for variable:' + diag_field['var_name'] + ' and file:' + file_name + ' is not valid')
  elif "pow" in reduction :
    if int(reduction[3:5]) < 0 :
      sys.exit('ERROR: The power value in ' + reduction + ' for variable:' + diag_field['var_name'] + ' and file:' + file_name + ' is not valid')
  elif reduction not in valid :
    sys.exit('ERROR: The reduction (' + reduction + ') in variable:' + diag_field['var_name'] + ' and file:' + file_name + ' is not valid')

def check_kind(diag_field, file_name) :
  """Check if the variable type is valid. Crashes if it not. """
  valid = ["r4", "r8"]
  if diag_field['kind'] not in valid :
    sys.exit('ERROR: The kind (' + diag_field['kind'] + ') in variable:' + diag_field['var_name'] + ' and file:' + file_name + ' is not valid')

def check_diag_field(diag_field, file_name) :
  """Check if the diag_field is defined correctly, crashes if it is not """
  check_required_diag_field_key(diag_field, file_name)
  check_reduction(diag_field, file_name)
  check_kind(diag_field, file_name)

def check_for_duplicates(my_list, list_name) :
  """Check if there any duplicates in a list. Crashes if they are """
  if len(set(my_list)) != len(my_list):
    sys.exit('ERROR: Found duplicate ' + list_name )

""" Loop thorugh all the files and field and checks if they are defined correctly"""
file_names = []
with open(in_diag_table) as fl:
  my_table = yaml.load(fl, Loader=UniqueKeyLoader)
  if 'title' not in my_table : sys.exit('ERROR: title is a required key!')
  if 'base_date' not in my_table : sys.exit('ERROR: base_date is a required key!')
  check_date(my_table['base_date'], 'base_date')

  diag_files = my_table['diag_files']
  for i in range(0, len(diag_files)) :
    diag_file = diag_files[i]
    check_diag_file(diag_file)

    if 'varlist' not in diag_file: continue
    diag_fields = diag_file['varlist']
    var_names = []
    for j in range(0, len(diag_fields)) :
      diag_field = diag_fields[j]
      check_diag_field(diag_field, diag_file['file_name'])
      if "output_name" in diag_field :
          var_names = var_names + [diag_field['output_name']]
      else :
          var_names = var_names + [diag_field['var_name']]
    check_for_duplicates(var_names, 'var_names in file: ' + diag_file['file_name'])
    file_names = file_names + [diag_file['file_name']]
check_for_duplicates(file_names, "file_names")
