#! /usr/bin/env python

import sys
import argparse
from process_ss import db_process
from pangenome_elements import pangenome_elements
from pangenome_hashes import pangenome_hashes


def pangenome_hashes():
    for i, (key, nested_dict) in enumerate(ss_dict.items()):
        nested_keys = []
        for k, v in nested_dict.items(): # remove `v` to get a (key, value) list...
            small_key = k
            nested_keys.append(small_key)
   
    key_array = np.array(nested_keys)
    
    central_core_keys = [item[0] for item in central_core]
    external_core_keys = [item[0] for item in external_core]
    shell_keys = [item[0] for item in shell]
    inner_cloud_keys = [items[0] for item in inner_cloud]
    surface_keys = [item[0] for item in surface_cloud]
    
    only_central_core = list(central_core_keys)
    only_external_core = list(set(external_core_keys) - set(central_core_keys)) #nothin from inner_core
    only_shell = list(set(shell_keys) - set(external_core_keys)) #nothin from inner or outer_core
    only_inner_cloud = list(set(inner_cloud_keys) - set(shell_keys)) # nothing from inner, outer, or shell
    only_surface_cloud = list(set(surface_cloud_keys) - set(inner_cloud_keys)) # nothing from inner, outer, shell, or small_cloud
    only_full_cloud = list(set(inner_cloud_keys) - set(shell_keys)) #nothing from inner, outer_core, shell

    return only_central_core, only_external_core, only_shell, only_inner_cloud, only_surface_cloud, only_full_cloud

def main():
    p = argparse.ArgumentParser(description='Create a list of hashes for the pangenome elements')
    p.add_argument('-d', '--data', metavar='SOURMASH_DATABASE', help='The sourmash dictionary created from `process_ss.py`')
    p.add_argument('-k', '--ksize', type=int, default=31, help='The ksize of the sourmash pangenome database')
    p.add_argument('-l', '--lineage', help='The specific lineage to extract from the sourmash pangenome database (e.g. "s__Escherichia coli")')
    args = p.parse_args()

    ss_dict = db_process(filename=args.data, k=args.ksize, lineage_name=args.lineage)
    nested_key, central_core, external_core, shell, inner_cloud, surface_cloud = pangenome_elements(data=ss_dict)
    pangenome_hashes()

if __name__ == '__main__':
    sys.exit(main())
