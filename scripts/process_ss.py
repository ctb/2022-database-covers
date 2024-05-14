#! /usr/bin/env python

import sourmash
from sourmash import sourmash_args
import argparse
import sys
import os
import re


def db_process(filename, ignore_case, invert_match, user_input, process_db, k=31, lineage_name='None'):
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


        selected_sigs = []
        print(f'Found {len(sub_mf)} signatures in {bname}:')

        for n, row in enumerate(sub_mf.rows, start=1):
            print(f'{n:<15} \033[0;31m{row.get("name")}\033[0m')
            selected_sigs.append(row.get('name'))


        if user_input:
            while True:
                user_input = input('\nSelect signatures to process (Comma-separated index value, "all", or "quit"): ')

                if user_input.strip().lower() == 'quit' or user_input.strip().lower() == 'q':
                    print("Exiting...")
                    sys.exit(0)

                if user_input.strip().lower() == 'all' or user_input.strip().lower() == 'a':
                    break

                else:
                    try:
                        #create a list of only digits no matter if letters or additional commas
                        indices = [int(idx.strip()) for idx in user_input.split(',') if idx.strip().isdigit()]
                        if not indices:
                            raise ValueError("Invalid input string: Please enter a comma-separated integer list, 'all', or 'quit'.")

                        outlier = [idx for idx in indices if not 1 <= idx <= len(selected_sigs)]

                        if outlier:
                            raise ValueError(f'Out of range integers: {", ".join([str(item) for item in outlier])}')

                        indices = [n - 1 for n in indices]
                        selected_names = [selected_sigs[n] for n in indices]

                        def search_name(vals):
                            return any(val in selected_names for val in vals)

                        sub_mf = sub_mf.filter_on_columns(search_name, ["name"])

                        break
                    except Exception as e:
                        print(f'{e}')
                        continue

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

        total_rows_examined = 0
        total_rows_examined += len(mf)

        print(f"\nloaded {total_rows_examined} total that matched ksize & molecule type")

        if ss_dict:
            print(f"extracted {len(ss_dict)} signatures from {len(db)} file(s)\n")

        else:
            print("no matching signatures found!\n")
            sys.exit(-1)

    else:
        #process the entire database

        if process_db:
            for n, ss in enumerate(db.signatures()):

                if n % 10 ==0:
                    print(f'...Processing {n} of {len(mf)}', end='\r', flush=True)

                    name = ss.name


                    mh = ss.minhash
                    hashes = mh.hashes
                    ss_dict[name] = hashes

                print(f'...Processed {n} of {len(mf)} \n')

        else:
            print('\nDid you mean to use `-l/--lineage-name` to process specific signatures?')
            print('Nothing to process. Exiting...\n')
            sys.exit()

    return ss_dict


def main():
    p = argparse.ArgumentParser(description='Read in sourmash pangenome database with lineage selection option')
    p.add_argument('data', metavar='SOURMASH_DATABASE', help='The sourmash pangenome database')
    p.add_argument('-k', '--ksize', type=int, default=31, help='The ksize of the sourmash pangenome database')
    p.add_argument('-l', '--lineage', help='The specific lineage to extract from the sourmash pangenome database (e.g. "s__Escherichia coli")')
    p.add_argument('-i', '--ignore-case', action='store_true')
    p.add_argument('-v', '--invert-match', action='store_true')
    p.add_argument('-u', '--user_input', action='store_true')
    p.add_argument('-p', '--process_db', action='store_true', help='Process the entire sourmash pangenome database')

    args = p.parse_args()

    db_process(filename=args.data, ignore_case=args.ignore_case, invert_match=args.invert_match, k=args.ksize, lineage_name=args.lineage, user_input=args.user_input, process_db=args.process_db)


if __name__=='__main__':
    sys.exit(main())
