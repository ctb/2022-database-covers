#! /usr/bin/env python

import sys
import argparse
from process_ss import db_process
import csv


CENTRAL_CORE=1
EXTERNAL_CORE=2
SHELL=3
INNER_CLOUD=4
SURFACE_CLOUD=5


def pangenome_elements(data):
    # get the pangenome elements of the dicts for each rank pangenome
    for i, (key, nested_dict) in enumerate(data.items()):
        max_value = max(nested_dict.values())

        central_core_threshold = 0.95 #0.95 is core , 90% is technically soft core
        external_core_threshold = 0.90
        shell_threshold = 0.10 #0.10
        inner_cloud_threshold = 0.01 # 0.0 is the full cloud, but trimming (0.001?) may be necessary to create the viz...?
        surface_cloud_threshold = 0.00

        central_core = []
        external_core = []
        shell = []
        inner_cloud = []
        surface_cloud = []

        for nested_key, nested_value in nested_dict.items():
            if nested_value >= max_value * central_core_threshold:
                central_core.append((nested_key, nested_value))
            elif nested_value >= max_value * external_core_threshold:
                external_core.append((nested_key, nested_value))
            elif nested_value >= max_value * shell_threshold:
                shell.append((nested_key, nested_value))
            elif nested_value >= max_value * inner_cloud_threshold:
                inner_cloud.append((nested_key, nested_value))
            elif nested_value >= max_value * surface_cloud_threshold:
                surface_cloud.append((nested_key, nested_value))
        return central_core, external_core, shell, inner_cloud, surface_cloud

def main():
    p = argparse.ArgumentParser(description='Create pangenome elements from sourmash pangenome database')
    p.add_argument('-d', '--data', metavar='SOURMASH_DATABASE', help='The sourmash dictionary created from `process_ss.py`', required=True)
    p.add_argument('-k', '--ksize', type=int, default=31, help='The ksize of the sourmash pangenome database')
    p.add_argument('-l', '--lineage', help='The specific lineage to extract from the sourmash pangenome database (e.g. "s__Escherichia coli")')
    p.add_argument('-o', '--output-hash-classification', required=False,
                   help='pickled dictionary containing classification of each hash')
    args = p.parse_args()

    ss_dict = db_process(filename=args.data, k=args.ksize, lineage_name=args.lineage)
    results = pangenome_elements(data=ss_dict)

    if args.output_hash_classification:
        print(f"Writing hash classification to CSV file '{args.output_hash_classification}'")
        with open(args.output_hash_classification, 'w', newline='') as fp:
            w = csv.writer(fp)
            w.writerow(['hashval', 'pangenome_classification'])
            central_core, external_core, shell, inner_cloud, surface_cloud = results

            for xx, classify_code in (
                    (central_core, CENTRAL_CORE),
                    (external_core, EXTERNAL_CORE),
                    (shell, SHELL),
                    (inner_cloud, INNER_CLOUD),
                    (surface_cloud, SURFACE_CLOUD)
                    ):
                for hashval, _ in xx:
                    w.writerow([hashval, classify_code])

if __name__ == '__main__':
    sys.exit(main())
