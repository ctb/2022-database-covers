#! /usr/bin/env python
import sys
import csv
import argparse
import sourmash
from collections import defaultdict, Counter
import pprint
import seaborn
import matplotlib.pyplot as plt

from sourmash.save_load import SaveSignaturesToLocation

from pangenome_elements import CENTRAL_CORE, EXTERNAL_CORE, SHELL, \
    INNER_CLOUD, SURFACE_CLOUD, NAMES


def main():
    p = argparse.ArgumentParser()
    p.add_argument('metagenome_sig')
    p.add_argument('-k', '--ksize', default=31, help='k-mer size', type=int)
    p.add_argument('classify_csv_file')
    p.add_argument('-o', '--output-figure', required=True)
    p.add_argument('-m', '--hist-x-min', default=0, type=int)
    p.add_argument('-M', '--hist-x-max', default=None, type=int)
    args = p.parse_args()

    db = sourmash.load_file_as_index(args.metagenome_sig)
    db = db.select(ksize=args.ksize)
    sketches = list(db.signatures())
    assert len(sketches) == 1
    sketch = sketches[0]
    minhash = sketch.minhash
    hashes = minhash.hashes

    abunds = {}
    for k in NAMES:
        abunds[k] = []

    central_core_mh = minhash.copy_and_clear()
    shell_mh = minhash.copy_and_clear()

    with open(args.classify_csv_file, 'r', newline='') as fp:
        r = csv.DictReader(fp)

        classify_d = {}
        for row in r:
            hashval = int(row['hashval'])
            classify_as = int(row['pangenome_classification'])
            classify_d[hashval] = classify_as

    # now, classify_d has the classifications we care about. Let's
    # do terrible things to the sketch now.

    for hashval, abund in hashes.items():
        classify = classify_d.get(hashval)
        if classify is not None:
            abunds[classify].append(abund)

    max_abund = 0
    for i in abunds:
        if abunds[i]:
            max_this_abund = max(abunds[i])
            max_abund = max(max_abund, max_this_abund)

    print('XXX', max_abund)
    xmin = args.hist_x_min
    xmax = args.hist_x_max
    if xmax is None:
        xmax = max_abund
    binrange=(xmin, xmax)

    # make histograms
    for i in abunds:
        name = NAMES[i]
        seaborn.histplot(abunds[i], kde=True, label=name, binrange=binrange)

    plt.xlim(binrange)
    plt.legend(loc='upper right')
    plt.savefig(args.output_figure)


if __name__ == '__main__':
    sys.exit(main())

