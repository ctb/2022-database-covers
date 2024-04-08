#! /usr/bin/env python

import sys
import argparse
import matplotlib.pyplot as plt
from process_ss import db_process
from pangenome_elements import pangenome_elements

def pangenome_circles(line_width=1, edge_color='black', colors = ['magenta', 'purple', 'red', 'green', 'blue'], percents = ['95%', '90%', '10%', '1%'], **kwargs):
    max_length = max(len(value) for value in kwargs.values())
    sizes = [len(kwargs[key]) / max_length for key in kwargs.keys()]
    names = list(kwargs.keys())
    colors = colors

    # Sort the sizes, colors, and names in descending order of size
    sortie = sorted(range(len(sizes)), key=lambda i: sizes[i], reverse=True)
    sizes = [sizes[i] for i in sortie]
    names = [names[i] for i in sortie]
    colors = [colors[i] for i in sortie]
    percs = [percents[i] for i in sortie]

    # Generate non-overlapping circles with colors filling in-between
    fig, ax = plt.subplots()

    # plot the largest radius first place the next smaller on top!
    for i, (size, color, name, perc) in enumerate(zip(sizes, colors, names, percs), start=1):
        theta = [2 * math.pi * j / 100 for j in range(101)]  # Generate theta values (101 to complete the circle!)
        radius = size
        x = [radius * math.cos(t) for t in theta]
        y = [radius * math.sin(t) for t in theta]

        ax.plot(x, y, color=edge_color, linestyle='-', linewidth=line_width) #draw a circle
        ax.fill(x, y, color=color, alpha=1,  label=f'{perc}, {name}') #fill that circle (changing alpha causes color bleed?)

    ax.set_aspect('equal')

    ax.axis([-max(sizes) - 0.01, max(sizes) + 0.01, -max(sizes) - 0.01, max(sizes) + 0.01])
    ax.set_title(f'Pangenome plot for {lineage}')
    legend = ax.legend(loc='lower left', bbox_to_anchor=(0.8, 0.75),
              ncol=1, fancybox=True, shadow=True)
    for handle in legend.get_patches():
        handle.set_edgecolor('black') # set_edgecolors
    for text in legend.get_texts():
    #    text.set_fontfamily("Montserrat")
    #    text.set_color("#b13f64")
    #    text.set_fontstyle("italic")
        text.set_fontweight("bold")
        text.set_fontsize(10)

    # https://stackoverflow.com/questions/14908576/how-to-remove-frame-from-a-figure
    ax.axis('off')
    fig.set_tight_layout(True)
    plt.savefig("overlapping_filled_circles.png", bbox_inches="tight", transparent=True)

def main():
    p = argparse.ArgumentParser(description='Create a pangenome element circle plot for sourmash data')
    p.add_argument('-d', '--data', metavar='SOURMASH_DATABASE', help='The sourmash dictionary created from process_ss.py')
    p.add_argument('-k', '--ksize', type=int, default=31, help='The ksize of the sourmash pangenome database')
    p.add_argument('-l', '--lineage', help='The specific lineage to extract from the sourmash pangenome database (e.g. "s__Escherichia coli"')
    p.add_argument('-ic', '--inner-core', help='The set of features that are shared across 95%% of the genomes of the pangenome')
    p.add_argument('-oc', '--outer-core', help='The set of features that are shared across 90%% of the genomes of the pangenome')
    p.add_argument('-s', '--shell', help='The set of features that are shared across 10%% of the genomes of the pangenome')
    p.add_argument('-sc', '--small-cloud', help='The set of features that are shared across 1%% of the genomes of the pangenome')
    p.add_argument('-fc', '--full-cloud', help='The set of features that are shared across all of the genomes of the pangenome')
    args = p.parse_args()

    ss_dict = db_process(filename=args.data, k=args.ksize, lineage_name=args.lineage)
    pangenome_elements(data=ss_dict)
    pangenome_circles(inner_core=args.inner_core, outer_core=args.outer_core, shell=args.shell, cloud=args.small_cloud, colors=['m','r','b','y'], percents=['95%', '90%', '10%', '  1%'], line_width=2)

if __name__ == '__main__':
    sys.exit(main())
