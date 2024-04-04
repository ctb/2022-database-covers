#! /usr/bin/env python

import sys
import argparse
from process_ss import db_process


def pangenome_elements(data):
    # get the pangenome elements of the dicts
    for i, (key, nested_dict) in enumerate(data.items()):
        max_value = 0
        max_count = 0

        for nested_value in nested_dict.values():
            if nested_value > max_value:
                max_value = nested_value
                max_count = 1  # Reset count for new maximum value
            elif nested_value == max_value:
                max_count += 1  # Increment count for each occurrence of maximum value

        core_threshold = 0.95 #0.95 is core , 90% is technically soft core
        soft_core_threshold = 0.90
        shell_threshold = 0.10 #0.10
        small_cloud_threshold = 0.01 # 0.0 is the full cloud, but trimming (0.001?) may be necessary to create the viz...?
        cloud_threshold = 0.00

        core = []
        soft_core = []
        shell = []
        small_cloud = []
        cloud = []

        for nested_key, nested_value in nested_dict.items():
            if nested_value >= max_value * core_threshold:
                core.append((nested_key, nested_value))
            if nested_value >= max_value * soft_core_threshold:
                soft_core.append((nested_key, nested_value))
            if nested_value >= max_value * shell_threshold:
                shell.append((nested_key, nested_value))
            if nested_value >= max_value * small_cloud_threshold:
                small_cloud.append((nested_key, nested_value))
            if nested_value >= max_value * cloud_threshold:
                cloud.append((nested_key, nested_value))
        return nested_key, core, soft_core, shell, small_cloud, cloud

def main():
    p = argparse.ArgumentParser(description='Create pangenome elements from sourmash pangenome database')
    p.add_argument('-d', '--data', metavar='SOURMASH_DATABASE', help='The sourmash dictionary created from `process_ss.py`')
    p.add_argument('-k', '--ksize', type=int, default=31, help='The ksize of the sourmash pangenome database')
    p.add_argument('-l', '--lineage', help='The specific lineage to extract from the sourmash pangenome database (e.g. "s__Escherichia coli")')
    args = p.parse_args()

    ss_dict = db_process(filename=args.data, k=args.ksize, lineage_name=args.lineage)
    pangenome_elements(data=ss_dict)

if __name__ == '__main__':
    sys.exit(main())
