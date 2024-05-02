#! /usr/bin/env python

# for each hash in a pangenome element included in the input
# create a vertex that stores which signature contains the 
# hash. (i.e. h1 -> sig1, sig12, sig53, sig90)
# for the signatures return the unique hashes that are found in all (or by thresholds?)

# use the output csv of classified_hashes.py
# set an argument to choose the pangenome element/s to compare
# 
# need a hash_count/pangenome element and total
# , sig_count

#hashval,pangenome_classification
#17551373616191,1
#21150285087017,1 
#32603191963564,1   

import sys
import argparse
import csv
import collections
import re
import os

from sourmash import sourmash_args
from process_ss import db_process
from pangenome_elements import pangenome_elements
from pangenome_elements import CENTRAL_CORE, EXTERNAL_CORE, SHELL, \
    INNER_CLOUD, SURFACE_CLOUD, NAMES


def read_pangenome_csv(csv_file):
     with open(csv_file, 'r', newline='') as fp:
         r = csv.DictReader(fp)

         classify_d = {}
         for row in r:
             hashval = int(row['hashval'])
             classify_as = int(row['pangenome_classification'])
             if classify_as in classify_d:
                 classify_d[classify_as].append(hashval)
             else:
                 classify_d[classify_as] = [hashval]

     return classify_d

def create_pangenome_dict(results):
    # Results are from the pangenome_elements() 
    central_core, external_core, shell, inner_cloud, surface_cloud = results

    classify_d = {}
    for xx, classify_code in (
            (central_core, CENTRAL_CORE),
            (external_core, EXTERNAL_CORE),
            (shell, SHELL),
            (inner_cloud, INNER_CLOUD),
            (surface_cloud, SURFACE_CLOUD)
            ):
        for hashval, _ in xx:
            if classify_code in classify_d:
                classify_d[classify_code].append(hashval)
            else:
                classify_d[classify_code] = [hashval]
    #compare `awk -F',' '$2 == 1 {print}' ecoli.csv | wc -l` to print statement below
    #print(len(classify_d[1]))                   
    return classify_d
   

#def pan_meta_compare():

def main():
 
# here i will need to use the following cmds in order

# from process_ss import db_process
# db_process(
# pangenome_elements    

    p = argparse.ArgumentParser(description='Create pangenome elements from sourmash pangenome database')
    p.add_argument('-d', '--data', metavar='SOURMASH_DATABASE', help='The sourmash dictionary created from `make_pangneome_sketches.py`')
    p.add_argument('-c', '--csv', metavar='CLASSIFIED_HASH_CSV', help='The CSV file containing pangenomic classification for each hash')
    p.add_argument('-k', '--ksize', type=int, default=31, help='The ksize of the sourmash pangenome database')
    p.add_argument('-l', '--lineage', help='The specific lineage to extract from the sourmash pangenome database (e.g. "s__Escherichia coli")')
    p.add_argument('-i', '--ignore-case', action='store_true', help='Ignore the casing of search terms')
    p.add_argument('-o', '--output', required=False, help='CSV file containing classification of each hash')
    args = p.parse_args()


    if args.csv:
        pangenome_dict = read_pangenome_csv(args.csv)
    else:
        ss_dict = db_process(filename=args.data, k=args.ksize, lineage_name=args.lineage, ignore_case=args.ignore_case, invert_match=False)
        results = pangenome_elements(data=ss_dict)
        pangenome_dict = create_pangenome_dict(results)

    # quick test to check that both functions return the same values
    #print(pangenome_dict[1][:10])

if __name__=="__main__":
    sys.exit(main())

