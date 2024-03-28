#! /usr/bin/env python

import argparse
from process_csv import pangenome_csv


def counting_kmers(data, lineage):
    lineage_list = {}
    lineage = lineage

    for d in data:
        l = d['lineage']
        hash_count = int(d['hash_count'])
        genome_count = int(d['genome_count'])

        if l not in lineage_list:
            lineage_list[l] = {}

        if genome_count not in lineage_list[l]:
            lineage_list[l][genome_count] = hash_count  # Store as single integer
        else:
            lineage_list[l][genome_count] += hash_count  # Accumulate hash count if already exists


    sorted_genome_counts = sorted(lineage_list[lineage].keys())
    differences = []

    for index in range(len(sorted_genome_counts)-1):
        genome_count1 = sorted_genome_counts[index]
        genome_count2 = sorted_genome_counts[index+1]
        hash_counts1 = lineage_list[lineage].get(genome_count1, 0)
        hash_counts2 = lineage_list[lineage].get(genome_count2, 0)
        difference = hash_counts2 - hash_counts1
        differences.append(difference)

    differences.insert(0, [v for v in lineage_list[lineage].values()][0]) #slap the first genome kmer count on the front

    #for i in range(5):
    #    print(f"In {lineage}, genome {i} has {differences[i]} new kmers.")
    return differences, lineage, lineage_list

p = argparse.ArgumentParser(description='Gather difference data from lineage counts')
p.add_argument('data', metavar='CSV_DATA', help='This is the processed CSV data from the pangenome CSV file')
p.add_argument('-l', '--lineage', metavar='LINEAGE_STRING', help='This is the lineage name to isolate from the dataset')
args = p.parse_args()

#pangenome_csv(args.filename)
#counting_kmers(args.data, args.lineage)
# Call pangenome_csv to process the CSV file
csv_data = pangenome_csv(args.data)

# Call counting_kmers with the processed CSV data
diff, lineage, lineage_list = counting_kmers(csv_data, args.lineage)

#diff, lineage, lineage_list = counting_kmers(csv_data, 's__Escherichia coli')
