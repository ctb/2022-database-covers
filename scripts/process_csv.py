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


def parse_args():
    p = argparse.ArgumentParser(description='Process a pangenome CSV file.')
    p.add_argument('filename', metavar='CSV', help='This is the pangenome CSV file to process')
    args = p.parse_args()

    pangenome_csv(args.filename)


if __name__=='__main__':
    parse_args()
