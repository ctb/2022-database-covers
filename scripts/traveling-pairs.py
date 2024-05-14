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
from collections import Counter
import re
import os

import sourmash
from sourmash import sourmash_args
from process_ss import db_process
from pangenome_elements import pangenome_elements
from pangenome_elements import CENTRAL_CORE, EXTERNAL_CORE, SHELL, \
    INNER_CLOUD, SURFACE_CLOUD, NAMES

import time
from collections import defaultdict
import polars as pl
 
def read_pangenome_csv(csv_file, pangenome_elements):
     with open(csv_file, 'r', newline='') as fp:
         r = csv.DictReader(fp)

         classify_d = {}
         for row in r:
             hashval = int(row['hashval'])
             classify_as = int(row['pangenome_classification'])
             if classify_as in pangenome_elements:
                  classify_d[hashval] = classify_as
#                 if classify_as in classify_d:
#                     classify_d[classify_as].append(hashval)
#                 else:
#                     classify_d[] = [hashval]

     return classify_d

def create_pangenome_dict(results, pangenome_elements):
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

    sub_d = {}
    for element in pangenome_elements:
        sub_d[element] = classify_d.get(element, [])

    return sub_d
   

from concurrent.futures import ThreadPoolExecutor

def load_signature(sig_file, k):
    sig = sourmash.load_one_signature(sig_file, k)
    return os.path.basename(sig_file), sig.minhash # str(sig) may be used to return the sig filename

def prep_ss(sig_files, k):
    sig_dict = {}
    with ThreadPoolExecutor() as executor:
        # Load signatures in parallel
        futures = [executor.submit(load_signature, sig_file, k) for sig_file in sig_files]

        for n, future in enumerate(futures):
            sig_name, mh = future.result()
            sig_dict[sig_name] = mh
            print(n, sig_name)

    return sig_dict
#def prep_ss(sig_files, k):
#    sig_dict = {}
#
#    for sig in sig_files:
#        #bname = os.path.basename(sig)
#        sig = sourmash.load_one_signature(sig, k)
#        mh = sig.minhash
#
#        sig_dict[str(sig)] = mh
#
#        print(str(sig))
#    return sig_dict
   # bname = os.path.basename(sig_file)

   # idx = sourmash.load_file_as_index(sig_file)
   # idx = idx.select(ksize=k)
   # sketches = list(idx.signatures())
   # assert len(sketches) == 1
   # sketch = sketches[0]
   # mh = sketch.minhash
   # #hashes = mh.hashes
   # return bname, mh

def pan_meta_compare(mh, pangenome_d):
    hashes = mh.hashes

    #for e, hashval in pangenome_d:
    
    


def main():
 
# here i will need to use the following cmds in order

# from process_ss import db_process
# db_process(
# pangenome_elements    

    p = argparse.ArgumentParser(description='Create pangenome elements from sourmash pangenome database')
    p.add_argument('sig', metavar='SOURMASH_SIGNATURE', nargs='+', help='The sourmash signature files to compare with pangenome element/s')
    p.add_argument('-d', '--data', metavar='SOURMASH_DATABASE', help='The sourmash dictionary created from `make_pangneome_sketches.py`')
    p.add_argument('-c', '--csv', metavar='CLASSIFIED_HASH_CSV', help='The CSV file containing pangenomic classification for each hash')
    p.add_argument('-k', '--ksize', type=int, default=31, help='The ksize of the sourmash pangenome database')
    p.add_argument('-l', '--lineage', help='The specific lineage to extract from the sourmash pangenome database (e.g. "s__Escherichia coli")')
    p.add_argument('-p', '--pangenome', type=int, nargs='+', help='Select the pangenome element/s to compare with metagenome files')
    p.add_argument('-i', '--ignore-case', action='store_true', help='Ignore the casing of search terms')
    p.add_argument('-o', '--output', required=False, help='CSV file containing classification of each hash')
    args = p.parse_args()

    if args.csv:
        pangenome_dict = read_pangenome_csv(args.csv, args.pangenome)
    else:
        ss_dict = db_process(filename=args.data, k=args.ksize, lineage_name=args.lineage, ignore_case=args.ignore_case, invert_match=False)
        results = pangenome_elements(data=ss_dict)
        pangenome_dict = create_pangenome_dict(results, args.pangenome)

#    print(sig_dict)

    start_time = time.time()
    pangenome_keys = set(pangenome_dict.keys())

    data = {'hashval': list(pangenome_keys)}
    
    # Preload signatures
    sig_dict = prep_ss(args.sig, args.ksize)

    counts = defaultdict(dict)

    for filename, minhash in sig_dict.items():
        common_keys = pangenome_keys.intersection(minhash.hashes)
        diff_keys = pangenome_keys.difference(minhash.hashes)
        c = Counter(minhash.hashes)
        for hashval in pangenome_keys:
            data.setdefault(filename, []).append(hashval in common_keys)

            #https://stackoverflow.com/questions/4746812/count-the-multiple-occurrences-in-a-set
            if hashval in common_keys:
                hash_counts = counts[hashval]
                for h in minhash.hashes:
                    #hash_counts[h] += 1
                    hash_counts[h] = hash_counts.get(h, 0) + 1 # get the minhash hash and add 1 if in hashval key:value. If not, set to 0
            #else:
            #    hash_counts = counts[hashval]
            #    for h in minhash.hashes:
            #        hash_counts[h] = hash_counts.get(h, 0)
            
            #if hashval in common_keys:
            #    for h in minhash.hashes:
            #        counts.setdefault(hashval, dict()).setdefault(h, 0)
            #        counts[hashval][h] += 1
            #else:
            #    for h in minhash.hashes:
            #        counts.setdefault(hashval, dict()).setdefault(h, 0)
            #counts[hashval].update(c)

    for n, (key, value) in enumerate(counts.items()):
        print(key, len(value.items()))

    print(len(counts))

#    for n, (key, value) in enumerate(counts.items()):
#        if n == 8:
#            print(key, len(value.items()))
#            
#            for k, v in value.items():
#                if v == 0:
#                    print(k, v)
#
#            break

    for n, (key, value) in enumerate(counts.items()):
        if n == 9:
            print(key, len(value.items()))
            
            for k, v in value.items():
                if v >= 3:
                    print(k, v)
            break

#    for k, v in data.items():
#        if len(v) >= 9:
#            print(f"The 10th value of the list for key '{k}' is: {v[9]}")

#            if hashval in common_keys:
#                data.setdefault(filename, []).append(True)
#                if hashval in counts:
#                    counts[hashval].update(c)
#                else:
#                    counts[hashval] = c
#            else:
#                data.setdefault(filename, []).append(False)
#    
    #print(counts)
    #print(list(data.values())[:10]) 

#    df = pl.DataFrame(data)
#
#    transposed_counts = {'hashval': list(counts.keys())}
#    for key, value in counts.items():
#        for k, v in value.items():
#            transposed_counts.setdefault(str(k), []).append(v)
#
#    count_df = pl.DataFrame(transposed_counts)

#    for n, row in enumerate(df.iter_rows(named=True)):
#        
#        print(row )
#        if n == 10:
#            break
#        #if True in row.values:
#            # Run your function here
#            # For example:
#        #    print("Running function for row:", index)
#    


#    transposed_counts = {'hashval': list(counts.keys())}
#    max_length = max(len(v) for v in transposed_counts.values())
#    for key, value in counts.items():
#        transposed_counts[str(key)] = [value.get(k, None) for k in transposed_counts['hashval']]
#        if len(transposed_counts[str(key)]) < max_length:
#            transposed_counts[str(key)] += [None] * (max_length - len(transposed_counts[str(key)]))    
#    count_df = pl.DataFrame(transposed_counts)
    # End benchmark
    end_time = time.time()

    # Calculate time taken
    elapsed_time = end_time - start_time
    print("Time taken:", elapsed_time, "seconds")

    #print(df.filter(pl.col(f"{filename}") == True))
#    print(df)
#    print(count_df)
# Now for each row (hashval) with a value in column == 1, get all hashes from file (minhash), and count them all

#        pan_meta_compare(minhash, pangenome_dict)


if __name__=="__main__":
    sys.exit(main())

