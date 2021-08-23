'''
Version 0.3.0
'''

import argparse
import fileinput
import os
import re
import shutil
import subprocess
import sys

def create_parser():
    parser = argparse.ArgumentParser(prog = 'gfamap',
                                     usage = '%(prog)s [options] --edges ... --graph assembly_graph.gfa --reference genome.fasta',
                                     description = 'Map edges of a genome graph to a reference genome database.',
                                     add_help=False)
    required = parser.add_argument_group('Required arguments')
    optional = parser.add_argument_group('Optional arguments')

    required.add_argument('-e', '--edges', metavar = '', help = 'all, or comma-separated names of edges in the assembly graph to be mapped', required = True)
    required.add_argument('-g', '--graph', metavar = '', help = 'path to assembly graph in GFA format', required = True)
    required.add_argument('-r', '--reference', metavar = '', help = 'path to reference genome fasta', required = True)

    optional.add_argument('-h', '--help', action = 'help', default = argparse.SUPPRESS, help = 'show this help message and exit')
    optional.add_argument('-p', '--prefix', metavar = '', help = 'prefix for output files (default: out)')
    optional.add_argument('-v', '--verbose', action = 'store_true', help = 'print progress (default: false)')
    return parser

def check_args(args):
    gfa_path = args.graph
    ref_path = args.reference
    if not os.path.isfile(gfa_path):
        print('Invalid assembly graph file path.')
        sys.exit()
    if not os.path.isfile(ref_path):
        print('Invalid reference file path.')
        sys.exit()
    if args.prefix is None:
        args.prefix = 'out'

def edge_parser(edges, verbose):
    if verbose:
        print('Creating edge list...')
    ## Return queries as a list of queries
    if edges != 'all':
        edge_list = edges.split(',')
    else:
        edge_list = ['all']
    return(edge_list)

def gfa_to_fasta(gfa, edges, prefix, verbose):
    ## Converts
    if verbose:
        print('Converting gfa to fasta...')
    fasta_list = []
    fasta_name = prefix + '.fasta'
    file = open(gfa, 'r')
    for entry in file:
        entry = entry.split()
        flag = entry[1] in edges
        if edges == ['all']:
            flag = True
        if entry[0] == 'S' and flag:
            if verbose:
                print('Processing', entry[1], '...')
            seq = entry[2]
            header = '>' + entry[1] + '_len' + str(len(seq))
            fasta_list.append(header + '\n')
            fasta_list.append(seq + '\n')
            continue
        else:
            continue
    fasta = open(fasta_name, 'w')
    fasta.writelines(fasta_list)
    fasta.close()
    return fasta_name

def mapper(reference, fasta, prefix, verbose):
    if verbose:
        print('Generating alignments...')
    sam_name = prefix + '.sam'
    sam = open(sam_name, 'w')
    subprocess.run(["minimap2", "-a", reference, fasta], stdout = sam)

def get_mapping(prefix, verbose):
    if verbose:
        print('Generating mapping...')
    sam_name = prefix + '.sam'
    entries = subprocess.Popen(["grep", "-v", "^@", sam_name], stdout = subprocess.PIPE)
    hits = subprocess.check_output(["cut", "-f", "1,3"], stdin = entries.stdout).decode('utf-8')
    hits = re.sub('_len[0-9]+', '', hits)
    hits = hits.split()
    mapping = dict()
    for index, item in enumerate(hits):
        if index % 2 == 0:
            if item in mapping:
                mapping[item] = mapping[item] + '_' + hits[index + 1]
            else:
                mapping[item] = hits[index + 1]
    return mapping

def annotate_gfa(gfa, mapping, prefix, verbose):
    if verbose:
        print('Annotating assembly graph...')
    annotated_gfa = 'annotated_' + gfa
    shutil.copy2(gfa, annotated_gfa)
    for line in fileinput.input(annotated_gfa, inplace=True):
        line = line.rstrip()
        for edge, annotation in mapping.items():
            match = r"\b" + re.escape(edge) + r"\b"
            if re.search(match, line):
                replacement = annotation + '_' + edge
                line = re.sub(match, replacement, line)
        print(line)

def main():
    parser = create_parser()
    args = parser.parse_args()
    check_args(args)
    edges = args.edges
    gfa = args.graph
    ref = args.reference
    prefix = args.prefix
    verbose = args.verbose

    edge_list = edge_parser(edges, verbose)
    fasta_name = gfa_to_fasta(gfa, edge_list, prefix, verbose)
    mapper(ref, fasta_name, prefix, verbose)
    mapping = get_mapping(prefix, verbose)
    annotate_gfa(gfa, mapping, prefix, verbose)

if __name__ == "__main__":
    main()
