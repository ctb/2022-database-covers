#! /usr/bin/env python

import sourmash
from sourmash import sourmash_args
from sourmash.logging import notify
import argparse
import sys
import os
import re


def db_process(filename, ignore_case, invert_match, k=31, lineage_name='None'):
    bname = os.path.basename(filename)
    ss_dict = {}
    print(f"\nloading file {bname} as index => manifest")

    db = sourmash_args.load_file_as_index(filename)
    db = db.select(ksize=k)
    mf = db.manifest
    print(f"{bname} contains {len(mf)} signatures")

    assert mf, "no matching sketches for given ksize!?"
    if lineage_name:
        print(f"Looking for {lineage_name} signature\n")
    
        # build the search pattern
        pattern = lineage_name
        if ignore_case:
            pattern = re.compile(pattern, re.IGNORECASE)
        else:
            pattern = re.compile(pattern)
    
        if invert_match:
    
            def search_pattern(vals):
                return all(not pattern.search(val) for val in vals)
        else:
    
            def search_pattern(vals):
                return any(pattern.search(val) for val in vals)
    
        # find all matching rows.
        sub_mf = mf.filter_on_columns(
            search_pattern, ["name", "filename", "md5"]
            )
        total_rows_examined = 0
        total_rows_examined += len(mf)
    
        sub_picklist = sub_mf.to_picklist()
    
        try:
            db = db.select(picklist=sub_picklist)
        except ValueError:
            error("Chosen lineage name input not supported")

        for ss in db.signatures():
            name = ss.name

            print(f'Found \033[0;31m{name}\033[0m in {bname}')

            mh = ss.minhash
            hashes = mh.hashes
            ss_dict[name] = hashes
    
        notify(f"\nloaded {total_rows_examined} total that matched ksize & molecule type")
    
        if ss_dict:
            notify(
                f"extracted {len(ss_dict)} signatures from {len(db)} file(s)\n"
            )
            
        else:
            error("no matching signatures found!\n")
            sys.exit(-1)

    else:
        #process the entire database
        while True:
            #make sure the user wants to commit to this action
            user_input = input('\nDo you want to process the entire database? ')

            yes_choices = ['yes', 'y']
            no_choices = ['no', 'n']

            if user_input.lower() in no_choices:
                print('\nDid you mean to use `--lineage-name` to process specific signatures?')
                print('Nothing to process. Exiting...\n')
                break
            elif user_input.lower() in yes_choices:
    
                for n, ss in enumerate(db.signatures()):
            
                    if n % 10 ==0:
                        print(f'...Processing {n} of {len(mf)}', end='\r', flush=True)
            
                    name = ss.name
            
            
                    mh = ss.minhash
                    hashes = mh.hashes
                    ss_dict[name] = hashes
        
                print(f'...Processed {n} of {len(mf)} \n')

            else:
                print('Type yes/y or no/n')
                continue

    return ss_dict


def main():
    p = argparse.ArgumentParser(description='Read in sourmash pangenome database with lineage selection option')
    p.add_argument('data', metavar='SOURMASH_DATABASE', help='The sourmash pangenome database')
    p.add_argument('-k', '--ksize', type=int, default=31, help='The ksize of the sourmash pangenome database')
    p.add_argument('-l', '--lineage', help='The specific lineage to extract from the sourmash pangenome database (e.g. "s__Escherichia coli")')
    p.add_argument('-i', '--ignore-case', action='store_true')
    p.add_argument('-v', '--invert-match', action='store_true')

    args = p.parse_args()

    db_process(filename=args.data, ignore_case=args.ignore_case, invert_match=args.invert_match, k=args.ksize, lineage_name=args.lineage)


if __name__=='__main__':
    sys.exit(main())
