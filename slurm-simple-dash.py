#!/usr/bin/env python3
import sys
import os
import math
import json
import subprocess
import argparse
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pylab as plt


_DEBUG = False
_VERBOSE = False


def html_head():
    global _DEBUG
    global _VERBOSE

    outstr = """<!DOCTYPE html>
    <HTML>
    <HEAD>
        <TITLE>CUBIC load</TITLE>
        <style>
            body {font-family: Calibri, "Lucida Sans", sans-serif;}
            p { font-family: Consolas, monospace;}
            pre {font-family: Consolas, monospace;}
        </style>
    </HEAD>"""

    return outstr


def html_body():
    global _DEBUG
    global _VERBOSE

    outstr = """<BODY>
    <h1>CUBIC load</h1>

    <h2>"all" partition</h2>

    <p><img src="load_all.svg"/></p>

    <h2>"ai" partition</h2>

    <p>Load based on GPUs occupied by jobs.</p>
    <p><img src="load_ai.svg"/></p>

    <h2>"bigmem" partition</h2>

    <p><img src="load_bigmem.svg"/></p>
    </BODY>
    </HTML>"""

    return outstr


def get_sinfo(partition='all'):
    global _DEBUG
    global _VERBOSE

    sinfo_cmdline = f'sinfo --Node --json -p {partition}'.split()

    sinfo_dict = None
    try:
        p = subprocess.run(sinfo_cmdline, stdout=subprocess.PIPE, check=True)
        sinfo_dict = json.loads(p.stdout.decode('utf-8'))
    except Exception as e:
        print(f'EXCEPTION: {e}')
        sys.exit(1)

    if _DEBUG and _VERBOSE:
        for k,v in sinfo_dict.items():
            print(f'{k}:\n\t{v}')

    #print(f'type(sinfo_dict["sinfo"] = {type(sinfo_dict["sinfo"])}')

    node_loads = {}
    for s in sinfo_dict['sinfo']:
        nthreads = s['sockets']['maximum'] * s['cores']['maximum'] * s['threads']['maximum']
        load = float(s['cpus']['load']['maximum']) / 100.

        if len(s['gres']['total']) > 0:
            gres_total = s['gres']['total'].split('(')[0]
            gres_used = s['gres']['used'].split('(')[0]
            pct_gres_used = float(100. * int(gres_used.split(':')[-1]) / int(gres_total.split(':')[-1]))
        else:
            gres_total = None
            gres_used = None
            pct_gres_used = None

        if _DEBUG and _VERBOSE:
            print('SINFO:')
            print(f's.keys() = {s.keys()}')
            #for k,v in s.items():
            #    print(f'{k}: {v}')
            if s['cpus']['load']['minimum'] != s['cpus']['load']['maximum']:
                print('XXX DIFFERENT')
            print(f'    {s["nodes"]["nodes"][0]} : nthreads = {nthreads:2d} ; allocated = {s["cpus"]["allocated"]:2d} ; load = {load:7.2f}')
            print()

        pct_load = load / float(nthreads) * 100.
        node_loads[s['nodes']['nodes'][0]] = {'nthreads': nthreads,
                                              'allocated': s['cpus']['allocated'],
                                              'load': load,
                                              '% load': pct_load,
                                              'gres total': gres_total,
                                              'gres used': gres_used,
                                              '% gres used': pct_gres_used}

    if _DEBUG and _VERBOSE:
        for k,v in node_loads.items():
            print(k, v)

    node_load_df = pd.DataFrame.from_dict(node_loads, orient='index')

    if _DEBUG:
        print(math.ceil(math.sqrt(len(node_load_df))))
        print(node_load_df.describe())
        print()
        print(node_load_df)
        print()

    side_a = math.floor(math.sqrt(len(node_load_df)))
    side_b = side_a + 1
    plot_array = np.full((side_a, side_b), -1.)

    if _DEBUG and _VERBOSE:
        print(f'FOO: plot_array = \n{plot_array}')
        print()
        print(f'FOO: side_a = {side_a}')
        print(f'FOO: side_b = {side_b}')

    for x in range(side_a):
        for y in range(side_b):
            ind = (x * side_b) + y

            if _DEBUG and _VERBOSE:
                print(f'FOO: x = {x}, y = {y}, ind = {ind}')

            if ind < len(node_load_df):
                if _DEBUG and _VERBOSE:
                    print(f'    {node_load_df.iloc[ind]}')

                if partition == 'ai':
                    plot_array[x][y] = node_load_df.iloc[ind]['% gres used']
                else:
                    plot_array[x][y] = node_load_df.iloc[ind]['% load']

    if _DEBUG:
        print(plot_array)

    ax = sns.heatmap(plot_array, vmin=0., vmax=100., xticklabels='', yticklabels='')
    ax.set(xlabel='', ylabel='')
    fig = ax.get_figure()

    fig.savefig(f'load_{partition}.svg')
    plt.clf()


def main():
    global _DEBUG
    global _VERBOSE

    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', action='store_true', help='debugging output')
    parser.add_argument('-v', '--verbose', action='store_true', help='verbose output')
    args = parser.parse_args()

    _DEBUG = args.debug
    _VERBOSE = args.verbose

    # pandas display options
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)

    # numpy display options
    np.set_printoptions(threshold=np.inf)
    np.set_printoptions(linewidth=np.inf)

    for partition in ['all', 'ai', 'bigmem']:
        get_sinfo(partition)

    with open('cubic_load.html', 'w') as f:
        f.write(html_head())
        f.write(html_body())


if __name__ == '__main__':
    main()
