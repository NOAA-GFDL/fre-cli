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

Converts a legacy ascii field_table to a yaml field_table.
        Author: Eric Stofferahn 07/14/2022

"""

import re
from collections import OrderedDict
import click
import yaml

global gverbose

def main():
    # Necessary to dump OrderedDict to yaml format
    yaml.add_representer(OrderedDict, lambda dumper, data: dumper.represent_mapping('tag:yaml.org,2002:map', data.items()))

    @click.command()
    @click.option('--file',
                  '-f',
                  type=str,
                  help='Name of the field_table file to convert')
    @click.option('--verbose',
                  '-v',
                  type=bool,
                  is_flag=True,
                  default=False,
                  help='Increase verbosity')
    def convert_field_table_to_yaml(file, verbose):
        gverbose = verbose
        field_table_name = file

        if verbose:
            print(field_table_name)

        field_yaml = FieldYaml(field_table_name)
        field_yaml.main()
        field_yaml.writeyaml()

def dont_convert_yaml_val(inval):
    # Yaml does some auto-conversions to boolean that we don't want, this will help fix it
    dontconvertus = ["yes", "Yes", "no", "No", "on", "On", "off", "Off"]

    if not isinstance(inval, str):
        return yaml.safe_load(inval)
    if inval in dontconvertus:
        return inval
    else:
        return yaml.safe_load(inval)

class Field:
    """ A Field Object, containing the variable attributes, methods, and subparameters """
    def __init__(self, in_field_type, entry_tuple):
        """ Initialize the Field Object with the provided entries, then process as a species or tracer """
        self.field_type = in_field_type
        self.name = entry_tuple[0]
        self.dict = OrderedDict()
        self.num_subparams = 0
        for in_prop in entry_tuple[1]:
            if 'tracer' == self.field_type:
                self.process_tracer(in_prop)
            else:
                self.process_species(in_prop)

    def process_species(self, prop):
        """ Process a species field """
        comma_split = prop.split(',')
        if gverbose:
            print(self.name)
            print(self.field_type)
            print(comma_split)
        if len(comma_split) > 1:
            eq_splits = [x.split('=') for x in comma_split]
            if gverbose:
                print('printing eq_splits')
                print(eq_splits)
            for idx, sub_param in enumerate(eq_splits):
                if gverbose:
                    print('printing len(sub_param)')
                    print(len(sub_param))
                if len(sub_param) < 2:
                    eq_splits[0][1] += f',{sub_param[0]}'
                    if gverbose:
                        print(eq_splits)
            eq_splits = [x for x in eq_splits if len(x) > 1]
            for sub_param in eq_splits:
                if ',' in sub_param[1]:
                    val = yaml.safe_load("'" + sub_param[1]+ "'")
                else:
                    val = dont_convert_yaml_val(sub_param[1])
                self.dict[sub_param[0].strip()] = val
        else:
            eq_split = comma_split[0].split('=')
            val = dont_convert_yaml_val(eq_split[1])
            self.dict[eq_split[0].strip()] = val

    def process_tracer(self, prop):
        """ Process a tracer field """
        if gverbose:
            print(len(prop))
        self.dict[prop[0]] = prop[1]
        if len(prop) > 2:
            self.dict[f'subparams{str(self.num_subparams)}'] = [OrderedDict()]
            self.num_subparams += 1
            if gverbose:
                print(self.name)
                print(self.field_type)
                print(prop[2:])
            for sub_param in prop[2:]:
                eq_split = sub_param.split('=')
                if len(eq_split) < 2:
                    self.dict[prop[0]] = 'fm_yaml_null'
                    val = dont_convert_yaml_val(eq_split[0])
                    if isinstance(val, list):
                        val = [dont_convert_yaml_val(b) for b in val]
                    self.dict[f'subparams{str(self.num_subparams-1)}'][0][prop[1].strip()] = val
                else:
                    val = dont_convert_yaml_val(eq_split[-1])
                    if isinstance(val, list):
                        val = [dont_convert_yaml_val(b) for b in val]
                    self.dict[f'subparams{str(self.num_subparams-1)}'][0][eq_split[0].strip()] = val

def list_items(brief_text, brief_od):
    """ Given text and an OrderedDict, make an OrderedDict and convert to list """
    return list(OrderedDict([(brief_text, brief_od)]).items())

def listify_ordered_dict(in_list, in_list2, in_od):
    """ Given two lists and an OrderedDict, return a list of OrderedDicts. Note this function is recursive. """
    if len(in_list) > 1:
        x = in_list.pop()
        y = in_list2.pop()
        return [OrderedDict(list_items(x, k) + list_items(y, listify_ordered_dict(in_list, in_list2, v))) for k, v in in_od.items()]
    else:
        x = in_list[0]
        y = in_list2[0]
        return [OrderedDict(list_items(x, k) + list_items(y, v)) for k, v in in_od.items()]

def zip_uneven(in_even, in_odd):
    """ Re-splice two uneven lists that have been split apart by a stride of 2 """
    result = [None]*(len(in_even)+len(in_odd))
    result[::2] = in_even
    result[1::2] = in_odd
    return result

def pound_signs_within_quotes(in_lines):
    """ Change pound signs within quotes to the word poundsign so they aren't expunged when eliminating comments. """
    odds = [x.split('"')[1::2] for x in in_lines]
    evens = [x.split('"')[::2] for x in in_lines]
    for idx, line in enumerate(odds):
        odds[idx] = [re.sub('#','poundsign',x) for x in line]
    newfilelines = [zip_uneven(e,o) for e, o in zip(evens,odds)]
    return ''.join(['"'.join(x) for x in newfilelines])

def process_field_file(my_file):
    """ Parse ascii field table into nested lists for further processing """
    with open(my_file, 'r') as fh:
        filelines = fh.readlines()
    # Change literal pound signs to the word poundsign
    whole_file = pound_signs_within_quotes(filelines)
    # Eliminate tabs and quotes
    whole_file = whole_file.replace('"', '').replace('\t', '')
    # Eliminate anything after a comment marker (#)
    whole_file = re.sub("\#"+r'.*'+"\n",'\n',whole_file)
    # Replace the word poundsign with a literal pound sign (#)
    whole_file = re.sub("poundsign","#",whole_file)
    # Eliminate extraneous spaces, but not in value names
    whole_file = re.sub(" *\n *",'\n',whole_file)
    whole_file = re.sub(" *, *",',',whole_file)
    whole_file = re.sub(" */\n",'/\n',whole_file)
    # Eliminate trailing commas (rude)
    whole_file = whole_file.replace(',\n', '\n')
    # Eliminate newline before end of entry
    whole_file = re.sub("\n/",'/',whole_file)
    # Eliminate spaces at very beginning and end
    whole_file = whole_file.strip()
    # Eliminate very last slash
    whole_file = whole_file.strip('/')
    # Split entries based upon the "/" ending character
    into_lines = [x for x in re.split("/\n", whole_file) if x]
    # Eliminate blank lines
    into_lines = [re.sub(r'\n+','\n',x) for x in into_lines]
    into_lines = [x[1:] if '\n' in x[:1] else x for x in into_lines]
    into_lines = [x[:-1] if '\n' in x[-1:] else x for x in into_lines]
    # Split already split entries along newlines to form nested list
    nested_lines = [x.split('\n') for x in into_lines]
    # Split nested lines into "heads" (field_type, model, var_name) and "tails" (the rest)
    heads = [x[0] for x in nested_lines]
    tails = [x[1:] for x in nested_lines]
    return heads, tails

class FieldYaml:
    def __init__(self, field_file):
        self.filename = field_file
        self.out_yaml = OrderedDict()
        self.heads, self.tails = process_field_file(self.filename)

    def init_ordered_keys(self):
        """ Get unique combination of field_type and model... in order provided """
        self.ordered_keys = OrderedDict.fromkeys([tuple([y.lower() for y in x.split(',')[:2]]) for x in self.heads])

    def initialize_lists(self):
        """ Initialize out_yaml and ordered_keys """
        for k in self.ordered_keys.keys():
            self.ordered_keys[k] = []
            if k[0] not in self.out_yaml.keys():
                self.out_yaml[k[0]] = OrderedDict()
            if k[1] not in self.out_yaml[k[0]].keys():
                self.out_yaml[k[0]][k[1]] = OrderedDict()

    def populate_entries(self):
       """ Populate entries as OrderedDicts """
       for h, t in zip(self.heads, self.tails):
              head_list = [y.lower() for y in h.split(',')]
              tail_list = [x.split(',') for x in t]
              if (head_list[0], head_list[1]) in self.ordered_keys.keys():
                if 'tracer' == head_list[0]:
                     self.ordered_keys[(head_list[0], head_list[1])].append((head_list[2], tail_list))
                else:
                     self.ordered_keys[(head_list[0], head_list[1])].append((head_list[2], t))

    def make_objects(self):
        """ Make Tracer and Species objects and assign to out_yaml """
        for k in self.ordered_keys.keys():
            for j in self.ordered_keys[k]:
                my_entry = Field(k[0], j)
                self.out_yaml[k[0]][k[1]][my_entry.name] = my_entry.dict

    def convert_yaml(self):
        """ Convert to list-style yaml """
        lists_yaml = listify_ordered_dict(['model_type', 'field_type'], ['varlist', 'modlist'], self.out_yaml)
        for i in range(len(lists_yaml)):
            for j in range(len(lists_yaml[i]['modlist'])):
                lists_yaml[i]['modlist'][j]['varlist'] = [OrderedDict(list(OrderedDict([('variable', k)]).items()) +
                    list(v.items())) for k, v in lists_yaml[i]['modlist'][j]['varlist'].items()]
        self.lists_wh_yaml = {"field_table": lists_yaml}

    def writeyaml(self):
        """ Write yaml out to file """
        raw_out = yaml.dump(self.lists_wh_yaml, None, default_flow_style=False)
        final_out = re.sub('subparams\d*:','subparams:',raw_out)
        with open(f'{self.filename}.yaml', 'w') as yaml_file:
            yaml_file.write(final_out)

    def main(self):
        self.init_ordered_keys()
        self.initialize_lists()
        self.populate_entries()
        self.make_objects()
        self.convert_yaml()


if __name__ == '__main__':
    main()
