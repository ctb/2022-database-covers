#! /usr/bin/env python

import argparse
import matplotlib
from process_csv import pangenome_csv, gather_difference

def plot_novels(data, line_width=1, marker='none', yaxis='kmers', scaled=1000):
    plt.figure(figsize=(12,5))
    if yaxis=="hashes":
        plt.plot(range(len(data)), data, linewidth=line_width, marker=marker) #marker='o' for circles
    elif yaxis=="kmers":
        plt.plot(range(len(data)), [i * scaled for i in diff], linewidth=line_width, marker=marker)
    else:
        print("Invalid value for yaxis. Defaulting to 'kmers'.")
        plt.plot(range(len(data)), [i * scaled for i in diff], linewidth=line_width, marker=marker)
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.xlabel('New Genomes')
    if yaxis=="hashes":
        plt.ylabel('Novel hashes')
        plt.title(f'Novel pangenome hashes per genome for Lineage: {lineage}')
    elif yaxis=="kmers":
        plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0), useMathText=True)
        plt.ylabel('Novel k-mers')
        plt.title(f'Novel pangenome k-mers per genome for Lineage: {lineage}')
    else:
        #print("Invalid value for yaxis. Defaulting to 'kmers'.")
        plt.ylabel('Novel k-mers')
        plt.title(f'Novel pangenome k-mers per genome for Lineage: {lineage}')
    plt.show()

csv_data = pangenome_csv(args.filename)
diff = gather_difference(csv_data, args.lineage)

plot_novels(data = diff, line_width=0.65, marker='_', yaxis='hashes')
plot_novels(data = diff, line_width=0.65, marker='o', yaxis='kmers')
plot_novels(data = diff, line_width=0.65, yaxis='kmes')
