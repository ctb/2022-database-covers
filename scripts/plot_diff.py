#! /usr/bin/env python

import argparse
import matplotlib.pyplot as plt
import os
from scipy.signal import savgol_filter
from process_csv import pangenome_csv
from diff_csv import gather_difference

def plot_novels(data, lineage, path, ext='png', h=5, w=12, line_width=1, marker='none', yaxis='kmers', scaled=1000):
    fpath = os.path.join(path + '.' + ext)
    plt.figure(figsize=(w,h))
    if yaxis=="hashes":
        plt.plot(range(len(data)), data, linewidth=line_width, marker=marker) #marker='o' for circles
    elif yaxis=="kmers":
        plt.plot(range(len(data)), [i * scaled for i in data], linewidth=line_width, marker=marker)
    else:
        print("Invalid value for yaxis. Defaulting to 'kmers' and 'scaled=1000'.")
        plt.plot(range(len(data)), [i * scaled for i in data], linewidth=line_width, marker=marker)
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
    plt.savefig(fpath, format=ext, bbox_inches="tight", transparent=True)

def total_features(data, lineage, path, ext='png', h=5, w=12, smooth=False, box_size=11, padding=3, fancy_smooth=False, window_length=11, polyorder=3):
    fpath = os.path.join(path + '.' + ext)
    x = range(len(data[lineage]))
    y = np.array(list(data[lineage].values()))

    # Apply Savitzky-Golay filter for smoothing
    y_smoothed = savgol_filter(y, window_length, polyorder)

    # Create a sliding box for smoothing
    box = np.ones(box_size) / box_size
    padded_y = list(data[lineage].values()) + [list(data[lineage].values())[-1]] * padding
    y_smooth = np.convolve(padded_y, box, mode='same')

    plt.figure(figsize=(w,h))
    if smooth:
        plt.plot(x, y_smooth[:len(data[lineage].values())])
    elif fancy_smooth:
        plt.plot(x, y_smoothed)
    else:
        plt.plot(range(len(data[lineage])), data[lineage].values())
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.xlabel('New Genomes')
    plt.ylabel('Total k-mers')
    plt.title(f'Total pangenome k-mers per genome for Lineage: {lineage}')
    plt.savefig(fpath, format=ext, bbox_inches="tight", transparent=True)


def parse_args():
    gp = argparse.ArgumentParser(prog='plot_diff', description='Plot the novel k-mers/hashes of a sourmash pangenome.')
    # Can not have positional arguments with subcommands if I want subcommand help without something filling that position...
    gp.add_argument('-d', '--data', metavar='CSV_DATA', help='This is the processed CSV data from the pangenome CSV file')
    gp.add_argument('-l', '--lineage', metavar='LINEAGE_STRING', help='This is the lineage name to isolate from the dataset')

    subparsers = gp.add_subparsers(title='subcommands', help='plotting operations')

    novel_parser = subparsers.add_parser('novel', help='Plot the novel features of a pangenome')
    novel_parser.add_argument('-o', '--output', help='The output path for the plot image file')
    novel_parser.add_argument('-e', '--ext', choices=['png', 'svg', 'pdf'], default='png', help='The image file extention (e.g. png, svg, pdf)')
    novel_parser.add_argument('-H', '--height', type=int, default=5, help='The plot image height')
    novel_parser.add_argument('-w', '--width', type=int, default=12, help='The plot image width')
    novel_parser.add_argument('-lw', '--line-width', type=int, default=1, help='The line width of the plotted lines')
    novel_parser.add_argument('-m', '--marker', type=str, default='_', help='The marker decoration to place on top of each line (e.g. "o", "_")')
    novel_parser.add_argument('-y', '--yaxis', type=str, default='kmers', help='Choose between "hashes" or "kmers" for the y-axis')
    novel_parser.add_argument('-s', '--scaled', type=int, default=1000, help='The scaled value of the sourmash database')
    novel_parser.set_defaults(func=plot_novels)


    total_parser = subparsers.add_parser('total', help='Plot the total features of a pangenome')
    group = total_parser.add_mutually_exclusive_group(required=True)
    total_parser.add_argument('-o', '--output', help='The output path for the plot image file')
    total_parser.add_argument('-e', '--ext', choices=['png', 'svg', 'pdf'], default='png', help='The image file extention (e.g. png, svg, pdf)')
    total_parser.add_argument('-H', '--height', type=int, default=5, help='The plot image height')
    total_parser.add_argument('-w', '--width', type=int, default=12, help='The plot image width')
    group.add_argument('-s', '--smooth', action="store_true", help='The plot line will be smoothed with sliding box')
    total_parser.add_argument('-b', '--boxsize', type=int, default=11, help='The size of the sliding box from `--smooth`')
    total_parser.add_argument('-p', '--padding', type=int, default=11, help='Padding the data to prevent drop-off')
    group.add_argument('-fs', '--fancy-smooth', action="store_true", help='The plot line will be smoothed with the Savitzky-Golay filter')
    total_parser.add_argument('-wl', '--window-length', type=int, default=11, help='The length of the smoothing window for `--fancy-smooth`')
    total_parser.add_argument('-po', '--polyorder', type=int, default=3, help='')
    total_parser.set_defaults(func=total_features)


    args = gp.parse_args()

    csv_data = pangenome_csv(filename=args.data)
    diff, lineage, line_list = gather_difference(csv_data, args.lineage)
    plot_novels(diff, path=args.output, ext=args.ext, lineage=args.lineage)


#plot_novels(data = diff, line_width=0.65, marker='_', yaxis='hashes')
#plot_novels(data = diff, line_width=0.65, marker='o', yaxis='kmers')
#plot_novels(data = diff, line_width=0.65, yaxis='kmes')

if __name__=='__main__':
    parse_args()
