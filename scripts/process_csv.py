#! /usr/bin/env python

import argparse
import csv


def pangenome_csv(filename):
    total_rows = sum(1 for line in open(filename))
    processed_rows = 0
    csv_data = []
    fieldnames = ['lineage', 'sig_name', 'hash_count', 'genome_count']
    
    try:
        with open(filename, newline = '') as fp:
            csv_file = csv.DictReader(fp, fieldnames)
            for row in csv_file:
                processed_rows += 1
                if processed_rows % 1000 == 0:
                    print(f"Processed {processed_rows}/{total_rows} rows ({processed_rows/total_rows*100:.2f}% complete)", end='\r', flush=True)
                
                csv_data.append(dict(row))
            print(' ' * 80) # or "\n"?
            print(f"Pangenome CSV file contained {total_rows} rows.")
            print(f"Processing of {processed_rows} rows has been completed.\n")
            return csv_data
    except Exception as e:
        print(f"An error occurred: {str(e)}")


def gather_difference(data, lineage):
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

    for index in range(len(sorted_genome_counts) - 1):
        genome_count1 = sorted_genome_counts[index]
        genome_count2 = sorted_genome_counts[index + 1]
        hash_counts1 = lineage_list[lineage].get(genome_count1, 0)
        hash_counts2 = lineage_list[lineage].get(genome_count2, 0)
        difference = hash_counts2 - hash_counts1
        differences.append(difference)

    differences.insert(0, [v for v in lineage_list[lineage].values()][0])  # Slap the first genome kmer count on the front

    for i in range(5):
        print(f"In {lineage}, genome {i} has {differences[i]} new kmers.")

    return differences, lineage, lineage_list


p = argparse.ArgumentParser(description='Process a pangenome CSV file.')
p.add_argument('filename', metavar='CSV', help='This is the pangenome CSV file to process')
p.add_argument('-l', '--lineage', metavar='LINEAGE_STRING', help='This is the lineage name to isolate from the dataset')
args = p.parse_args()

csv_data = pangenome_csv(args.filename)
gather_difference(csv_data, args.lineage)
