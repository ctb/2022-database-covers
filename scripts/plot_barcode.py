#! /usr/bin/env python

import os
import sys
import argparse
import matplotlib.pyplot as plt
from process_ss import db_process
from pangenome_elements import pangenome_elements
from pangenome_hashes import pangenome_hashes


def vertical_line_plot(sorted_values, path, ext='png', color='black', style='-', core_list=None, soft_core_list=None, shell_list=None, cloud_list=None, ref_list=None):
    fpath = os.path.join(path + '.' + ext)
    num_values = len(sorted_values)
    x_ticks = np.linspace(0, num_values-1, num_values)

    # For assigning colors
    category_colors = {
        'core': 'blue',
        'soft_core': 'green',
        'shell': 'red',
        'cloud': 'purple',
        'Reference': 'black'
    }

    line_color = np.full(num_values, color, dtype=object)
    line_style = np.full(num_values, style)
    line_min = np.zeros(num_values)
    line_max = np.ones(num_values)

    if core_list:
        core_indices = np.isin(sorted_values, core_list)
        line_color[core_indices] = category_colors['core']
        line_min[core_indices] = 0
        line_max[core_indices] = 0.25

    if soft_core_list:
        soft_core_indices = np.isin(sorted_values, soft_core_list)
        line_color[soft_core_indices] = category_colors['soft_core']
        line_min[soft_core_indices] = 0.25
        line_max[soft_core_indices] = 0.50

    if shell_list:
        shell_indices = np.isin(sorted_values, shell_list)
        line_color[shell_indices] = category_colors['shell']
        line_min[shell_indices] = 0.50
        line_max[shell_indices] = 0.75

    if cloud_list:
        cloud_indices = np.isin(sorted_values, cloud_list)
        line_color[cloud_indices] = category_colors['cloud']
        line_min[cloud_indices] = 0.75
        line_max[cloud_indices] = 1

    if ref_list:
        ref_indices = np.isin(sorted_values, ref_list)
        line_color[ref_indices] = category_colors['Reference']
        line_min[ref_indices] = 1
        line_max[ref_indices] = 1.25

    mplstyle.use('fast')
    fig, ax = plt.subplots(dpi=600)
    fig.set_size_inches(15, 4, forward=True)

    if num_values > 10000:
      line_width = 0.1
    else:
      line_width = 0.5

    ax.vlines(x=x_ticks, ymin=line_min, ymax=line_max, color=line_color, linestyle=line_style, linewidth=line_width)

    # Format the axes
    tick_positions = np.linspace(0, num_values-1, 5)
    ax.set_xticks(tick_positions, [sorted_values[int(pos)] for pos in tick_positions])

    for tick in ax.xaxis.get_major_ticks()[1::2]:
        tick.set_pad(15)
    ax.get_yaxis().set_visible(False)
    ax.set_title(f'Hashes of the {lineage} Pangenome', pad=16)

    # Format the legend
    lines = []
    for category, color in category_colors.items():
        lines.append(ax.vlines([], [], [], color=color, label=category))

    ax.legend(handles=lines, loc='upper center', bbox_to_anchor=(0.5, 1.065),
          ncol=5, fancybox=True, shadow=True)
    fig.set_tight_layout(True)
    plt.savefig(fpath, format=ext, bbox_inches="tight", transparent=True)

def main():
    p = argparse.ArgumentParser(description='Create a pangenome element representive bar plot for sourmash data')
    p.add_argument('-d', '--data', metavar='SOURMASH_DATABASE', help='The sourmash dictionary created from process_ss.py')
    p.add_argument('-k', '--ksize', type=int, default=31, help='The ksize of the sourmash pangenome database')
    p.add_argument('-l', '--lineage', help='The specific lineage to extract from the sourmash pangenome database (e.g. "s__Escherichia coli"')
    p.add_argument('-cc', '--central-core', help='The set of features that are shared across 95%% of the genomes of the pangenome')
    p.add_argument('-ec', '--external-core', help='The set of features that are shared across 90%% of the genomes of the pangenome')
    p.add_argument('-s', '--shell', help='The set of features that are shared across 10%% of the genomes of the pangenome')
    p.add_argument('-ic', '--inner-cloud', help='The set of features that are shared across 1%% of the genomes of the pangenome')
    p.add_argument('-fc', '--full-cloud', help='The set of features that are shared across all of the genomes of the pangenome')
    p.add_argument('-o', '--output', help='The output path for the plot image file')
    p.add_argument('-e', '--ext', choices=['png', 'svg', 'pdf'], default='png', help='The image file extention (e.g. png, svg, pdf)')
    
    args = p.parse_args()

    ss_dict = db_process(filename=args.data, k=args.ksize, lineage_name=args.lineage)
    nested_key, central_core, external_core, shell, inner_cloud, surface_cloud = pangenome_elements(data=ss_dict)
    only_central_core, only_external_core, only_shell, only_inner_cloud, only_surface_cloud, only_full_cloud = pangenome_hashes()

    vertical_line_plot(nested_keys, path=args.output, ext=args.ext, color='black', style='-', central_core_list=args.central_core, external_core_list=args.external_core, shell_list=args.shell, cloud_list=args.inner_cloud, ref_list=None)

if __name__ == '__main__':
    sys.exit(main())
