# -*- coding: utf-8 -*-
"""Convert the Yelp Dataset Challenge dataset from json format to csv.
For more information on the Yelp Dataset Challenge please visit http://yelp.com/dataset_challenge
"""
import argparse
import collections
import csv
import json
from collections import OrderedDict
import ast

columns2use=[]

def read_and_write_file(json_file_path, csv_file_path, column_names):
    """Read in the json dataset file and write it out to a csv file, given the column names."""
    with open(csv_file_path, 'wb+') as fout:
        csv_file = csv.writer(fout)
        csv_file.writerow([unicode(s).encode("utf-8") for s in column_names])
        with open(json_file_path) as fin:
            for line in fin:
                line_contents = json.loads(line.decode('utf-8'), object_pairs_hook=OrderedDict)
                csv_file.writerow([unicode(s).encode("utf-8") for s in get_row(line_contents, column_names)])

def get_superset_of_column_names_from_file(json_file_path):
    """Read in the json dataset file and return the superset of column names."""
    column_names = list()
    with open(json_file_path) as fin:
        for line in fin:
            line_contents = json.loads(line.decode('utf-8'), object_pairs_hook=OrderedDict)
            for k in get_column_names(line_contents):
                if k not in column_names:
                    column_names.append(k)
    return column_names

def get_column_names(line_contents, parent_key=''):
    """Return a list of flattened key names given a dict.
    Example:
        line_contents = {
            'a': {
                'b': 2,
                'c': 3,
                },
        }
        will return: ['a.b', 'a.c']
    These will be the column names for the eventual csv file.
    """
    column_names = []
    for k, v in line_contents.items():
        column_name = "{0}.{1}".format(parent_key, k) if parent_key else k
        if isinstance(v, collections.MutableMapping):
            column_names.extend(get_column_names(v, column_name))
        else:
            try:
                if isinstance(ast.literal_eval(v), dict):
                    v=ast.literal_eval(v)
                    column_names.extend(get_column_names(v, column_name))
                else:
                    column_names.append(str(column_name))
            except (SyntaxError, ValueError) as e:
                column_names.append(str(column_name))
    return column_names

def get_nested_value(d, key):
    """Return a dictionary item given a dictionary `d` and a flattened key from `get_column_names`.

    Example:
        d = {
            'a': {
                'b': 2,
                'c': 3,
                },
        }
        key = 'a.b'
        will return: 2

    """
    if '.' not in key:
        if key not in d:
            return None
        # if isinstance(ast.literal_eval(d), dict):
        #     d=ast.literal_eval(d)
        try:
            return d[key]
        except TypeError:
            return ast.literal_eval(d)[key]
    base_key, sub_key = key.split('.', 1)
    if base_key not in d:
        return None
    sub_dict = d[base_key]
    if sub_dict is None:
        return None
    return get_nested_value(sub_dict, sub_key)

def get_row(line_contents, column_names):
    """Return a csv compatible row given column names and a dict."""
    row = []
    for column_name in column_names:
        line_value = get_nested_value(line_contents,column_name)
        if isinstance(line_value, collections.OrderedDict):
            row.append(get_nested_value(dict(line_value.items()),column_name))
        elif isinstance(line_value, unicode):
            if "u'" in line_value:
                line_value=line_value[2:-1]
            if len(line_value)>2 and line_value[0]=="'" and line_value[-1]=="'":
                line_value=line_value[1:-1]
            row.append(line_value)
        elif line_value is not None:
            row.append('{0}'.format(line_value))
        else:
            row.append('')
    return row

if __name__ == '__main__':
    """Convert a yelp dataset file from json to csv."""

    parser = argparse.ArgumentParser(
            description='Convert Yelp Dataset Challenge data from JSON format to CSV.',
            )

    parser.add_argument(
            'json_file',
            type=str,
            help='The json file to convert.',
            )

    args = parser.parse_args()

    json_file = args.json_file
    csv_file = '{0}.csv'.format(json_file.split('.json')[0])
    col_file = '{0}_columns.txt'.format(json_file.split('.json')[0])
    print "col file:", col_file
    with open(col_file, 'r') as fin:
        lines = fin.readlines()
        for line in lines:
            columns2use.append(line.strip())
    print "Converting from json to csv..."
    column_names = columns2use #get_superset_of_column_names_from_file(json_file)
    read_and_write_file(json_file, csv_file, column_names)
