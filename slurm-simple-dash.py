#!/usr/bin/env python3
import sys
import os
import json
import subprocess
import argparse
import pandas as pd


_DEBUG = False
_VERBOSE = False


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

    if _DEBUG:
        for k,v in sinfo_dict.items():
            print(f'{k}:\n\t{v}')

    #print(f'type(sinfo_dict["sinfo"] = {type(sinfo_dict["sinfo"])}')

    node_loads = {}
    print('SINFO:')
    for s in sinfo_dict['sinfo']:
        nthreads = s['sockets']['maximum'] * s['cores']['maximum'] * s['threads']['maximum']
        load = float(s['cpus']['load']['maximum']) / 100.
        gres_total = s['gres']['total']
        gres_used = s['gres']['used']

        if _DEBUG and _VERBOSE:
            print(f's.keys() = {s.keys()}')
            #for k,v in s.items():
            #    print(f'{k}: {v}')
            if s['cpus']['load']['minimum'] != s['cpus']['load']['maximum']:
                print('XXX DIFFERENT')
            print(f'    {s["nodes"]["nodes"][0]} : nthreads = {nthreads:2d} ; allocated = {s["cpus"]["allocated"]:2d} ; load = {load:7.2f}')
            print()

        fractional_load = load / float(nthreads) * 100.
        node_loads[s['nodes']['nodes'][0]] = {'nthreads': nthreads,
                                              'allocated': s['cpus']['allocated'],
                                              'load': load,
                                              'fractional load': fractional_load,
                                              'gres total': gres_total,
                                              'gres used': gres_used}

    if _DEBUG and _VERBOSE:
        for k,v in node_loads.items():
            print(k, v)

    node_load_df = pd.DataFrame.from_dict(node_loads, orient='index')
    print(node_load_df.describe())
    print(node_load_df)


def main():
    global _DEBUG
    global _VERBOSE

    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', action='store_true', help='debugging output')
    parser.add_argument('-v', '--verbose', action='store_true', help='verbose output')
    parser.add_argument('-p', '--partition', help='partition', default='all')
    args = parser.parse_args()

    _DEBUG = args.debug
    _VERBOSE = args.verbose

    # pandas display options
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)

    get_sinfo(args.partition)


if __name__ == '__main__':
    main()
