#! /usr/bin/env python
import sys
import csv
import argparse
import sourmash
from collections import defaultdict
import pprint


from pangenome_elements import CENTRAL_CORE, EXTERNAL_CORE, SHELL, \
    INNER_CLOUD, SURFACE_CLOUD, NAMES


def main():
    p = argparse.ArgumentParser()
    p.add_argument('metagenome_sig')
    p.add_argument('-k', '--ksize', default=31, help='k-mer size', type=int)
    p.add_argument('classify_csv_files', nargs='+')
    args = p.parse_args()

    db = sourmash.load_file_as_index(args.metagenome_sig)
    db = db.select(ksize=args.ksize)
    sketches = list(db.signatures())
    assert len(sketches) == 1
    sketch = sketches[0]
    minhash = sketch.minhash
    hashes = minhash.hashes

    for csv_file in args.classify_csv_files:
        with open(csv_file, 'r', newline='') as fp:
            r = csv.DictReader(fp)

            classify_d = {}
            for row in r:
                hashval = int(row['hashval'])
                classify_as = int(row['pangenome_classification'])
                classify_d[hashval] = classify_as

        # now, classify_d has the classifications we care about. Let's
        # do terrible things to the sketch now.

        counter_d = defaultdict(int)
        total_classified = 0
        for hashval in hashes:
            classify = classify_d.get(hashval, -1)
            counter_d[classify] += 1
            if classify >= 0:
                total_classified += 1

        print(f"For '{csv_file}', signature '{sketch.name}' contains:")
        for int_id in sorted(NAMES):
            name = NAMES[int_id]
            count = counter_d.get(int_id)
            percent = count / total_classified * 100
            print(f"\t {count} ({percent:.1f}%) hashes are classified as {name}")

        count = counter_d.get(-1)
        print(f"\t ...and {count} hashes are NOT IN the csv file")


if __name__ == '__main__':
    sys.exit(main())

