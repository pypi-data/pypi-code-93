#!/usr/bin/env python3
#===============================================================================
# chip_seq.py
#===============================================================================

"""Align some ChIP-seq files. Use the beginnng of Josh's pipeline."""




# Imports ======================================================================

import argparse
import os
import picardtools
import pyhg19
import subprocess
import seqalign




# Functions ====================================================================

def main():
    """align reads with bwa aln / bwa samse
    then filter out reads that are unmapped, < quality score
    then remove blacklisted reads (if necessary)
    then sort reads
    then remove chrM reads
    use picard MarkDuplicates to filter out duplicate reads
    then index the bam file
    """

    args = parse_arguments()
    if len(args.fastq) == 1:
        args.fastq = args.fastq[0]
    elif len(args.fastq) > 2:
        raise RuntimeError('too many input files')
    with open('{}.align.log'.format(args.output), 'w') as log:
        sa = seqalign.SequenceAlignment(
            input_file=args.fastq,
            mapping_quality=args.quality,
            processes=args.processes,
            log=log,
            aligner=seqalign.BWA(
                reference_genome_path=args.reference, 
                trim_qual=15
            ),
            dedupper=picardtools.MarkDuplicates(
                metrics_file='{}.MarkDuplicates.metrics'.format(args.output),
                memory_gb=args.memory,
                temp_dir=args.tmp_dir
            ),
            temp_dir=args.tmp_dir
        )
        sa.apply_quality_filter()
        if args.remove_blacklisted_reads:
            sa.remove_blacklisted_reads(blacklist_path=args.blacklist_file)
        sa.samtools_sort(memory_limit=args.memory * args.processes)
        sa.samtools_index()
        sa.restrict_chromosomes(*(tuple(range(1, 23)) + ('X', 'Y')))
        sa.samtools_index()
        sa.samtools_sort(memory_limit=args.memory * args.processes)
        sa.samtools_index()
        sa.write('{}.sort.filt.bam'.format(args.output))
        sa.remove_duplicates()
        sa.samtools_index()
        sa.write('{}.sort.filt.rmdup.bam'.format(args.output))


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Align ChIP-seq reads to a reference genome'
    )
    io_group = parser.add_argument_group('I/O arguments')
    io_group.add_argument(
        'fastq',
        metavar='<path/to/reads.fastq[.gz]>',
        nargs='+',
        help='path to fastq file'
    )
    io_group.add_argument(
        'output',
        metavar='<prefix/for/output/files>',
        help='prefix for output files'
    )
    align_group = parser.add_argument_group('alignment arguments')
    align_group.add_argument(
        '--processes',
        metavar='<int>',
        type=int,
        default=4,
        help='number of processes to use [4]'
    )
    align_group.add_argument(
        '--memory',
        metavar='<float>',
        type=float,
        default=8,
        help='maximum memory per thread in GB [8]'
    )
    align_group.add_argument(
        '--quality',
        metavar='<int>',
        type=int,
        default=10,
        help='mapping quality cutoff for samtools [10]'
    )
    align_group.add_argument(
        '--reference',
        metavar='<path/to/reference.fasta>',
        default=pyhg19.PATH,
        help=(
            'path to reference genome prepared for BWA '
            f'[{pyhg19.PATH}]'
        )
    )
    blacklist_group = parser.add_argument_group('blacklist arguments')
    blacklist_group.add_argument(
        '--remove-blacklisted-reads',
        action='store_true',
        help='remove blacklisted reads after alignment'
    )
    blacklist_group.add_argument(
        '--blacklist-file',
        metavar='<path/to/blacklist.bed>',
        default=pyhg19.BLACKLIST,
        help=f'path to ENCODE blacklist file [{pyhg19.BLACKLIST}]'
    )
    config_group = parser.add_argument_group('configuration arguments')
    config_group.add_argument(
        '--tmp-dir',
        metavar='<temp/file/dir/>',
        help='directory to use for temporary files'
    )
    return parser.parse_args()

