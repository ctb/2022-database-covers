#! /usr/bin/env python

import sys
import argparse
import csv
import re

def pangenome_csv(filename):
    processed_rows = 0
    csv_data = []
    fieldnames = ['lineage', 'sig_name', 'hash_count', 'genome_count']
    
    try:
        with open(filename, newline='') as fp:
            lines = fp.readlines()
        csv_file = csv.DictReader(lines, fieldnames)
        total_rows = len(lines)
        for row in csv_file:
            processed_rows += 1
            if processed_rows % 1000 == 0:
               print(f"Processed {processed_rows}/{total_rows} rows ({processed_rows/total_rows*100:.2f}% complete)", end='\r', flush=True)
            csv_data.append(dict(row))
        print(' ' * 80) # or "\n"?
        print(f"Pangenome CSV file contained {total_rows} rows.")
        print(f"Processing of {processed_rows} rows has been completed.\n")

## This readlines segment does well but can not process the " , " in column three 
## s__Fusobacterium nucleatum,"GCA_000007325.1 Fusobacterium nucleatum subsp. nucleatum ATCC 25586 strain=ATCC 25586, ASM732v1",2139,1
#            lines = fp.readlines()
#            total_rows = len(lines)
#            for line in lines:
#                processed_rows += 1
#                if processed_rows % 1000 == 0:
#                    print(f"Processed {processed_rows}/{total_rows} rows ({processed_rows/total_rows*100:.2f}% complete)", end='\r', flush=True)
#                #values = line.strip().split(',') 
#                values = re.split(r',(?=(?:[^"]*"[^"]*")*[^"]*$)', line.strip()) # split by , 
#                row = dict(zip(fieldnames, values))
#                csv_data.append(row)
#            print(' ' * 80) # or "\n"?
#            print(f"Pangenome CSV file contained {total_rows} rows.")
#            print(f"Processing of {processed_rows} rows has been completed.\n")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        csv_data = None
#raise after print statement 
#return none if there is an exception I do not want to return `csv_data` 
# exception would set csv_data to none
    return csv_data

def parse_args():
    p = argparse.ArgumentParser(description='Process a pangenome CSV file.')
    p.add_argument('filename', metavar='CSV', help='This is the pangenome CSV file to process')
    args = p.parse_args()

    if pangenome_csv(args.filename) is None:
        return -1

#try to have only one return statement at the end of function 
#return error to command line with sys.exit()
#try to return info to user for why it failed
#Now, how to create a test file for automating a raised exception
if __name__=='__main__':
    sys.exit(parse_args()) 
