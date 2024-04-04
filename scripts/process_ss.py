#! /usr/bin/env python

import sourmash
from sourmash import sourmash_args
import argparse
import sys
import os

def db_process(filename, k=31, lineage_name='None'):
    bname = os.path.basename(filename)
    ss_dict = {}
    print(f"loading file {bname} as index => manifest")

    db = sourmash_args.load_file_as_index(filename)
    db = db.select(ksize=k)
    mf = db.manifest
    print(f"{bname} contains {len(mf)} signatures")

    assert mf, "no matching sketches for given ksize!?"

    print(f"Looking for {lineage_name} signature")
    
    for n, ss in enumerate(db.signatures()):

        if lineage_name and n and n % 10 == 0:
            print(f'...Searching {n} of {len(mf)}', end='\r', flush=True)
        elif lineage_name is None and n and n % 10 ==0:
            print(f'...Processing {n} of {len(mf)}', end='\r', flush=True)

        name = ss.name

        if lineage_name and name == lineage_name:
            mh = ss.minhash
            hashes = mh.hashes
            ss_dict[name] = hashes
            
            break

        elif lineage_name is None:
            mh = ss.minhash
            hashes = mh.hashes
            ss_dict[name] = hashes

    if lineage_name:
        print(f'...Searched {n} of {len(mf)} ')
    else:
        print(f'...Processed {n} of {len(mf)} ')
    return ss_dict


def main():
    p = argparse.ArgumentParser(description='Read in sourmash pangenome database with lineage selection option')
    p.add_argument('-d', '--data', metavar='SOURMASH_DATABASE', help='The sourmash pangenome database')
    p.add_argument('-k', '--ksize', type=int, default=31, help='The ksize of the sourmash pangenome database')
    p.add_argument('-l', '--lineage', help='The specific lineage to extract from the sourmash pangenome database (e.g. "s__Escherichia coli")')
    args = p.parse_args()

    db_process(filename=args.data, k=args.ksize, lineage_name=args.lineage)


if __name__=='__main__':
    sys.exit(main())
#ss_dict = db_process(filename=['dbs/gtdb-rs214-k21.pangenomes.species-abund.zip'], lineage_name='GCF_944611425 s__Escherichia coli')
#ref_ecoli = db_process(filename=['ref-ecoli.sig'])
#ref_ecoli2 = db_process(filename=['ref-ecoli2.sig'])
