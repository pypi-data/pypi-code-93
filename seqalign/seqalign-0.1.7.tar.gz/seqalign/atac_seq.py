#!/usr/bin/env python3
#===============================================================================
# align_atac_seq.py
#===============================================================================

"""Align some ATAC-seq files"""




# Imports ======================================================================

import argparse
import os
import picardtools
import pyhg19
import seqalign
import subprocess
import tempfile




# Functions ====================================================================

def main():
    args = parse_arguments()
    with tempfile.TemporaryDirectory(dir=args.tmp_dir) as (
        temp_dir_name
    ), open(f'{args.output}.align.log', 'w') as (
        log
    ): 
        sa = seqalign.SequenceAlignment(
            input_file=seqalign.trim_galore(
                args.reads1,
                args.reads2,
                temp_dir_name
            ),
            mapping_quality=0,
            processes=args.processes,
            log=log,
            aligner=(
                seqalign.Bowtie2() if args.bowtie2
                else seqalign.BWA(reference_genome_path=args.reference)
            ),
            temp_dir=args.tmp_dir
        )
        sa.samtools_fixmate()
        sa.samtools_sort(memory_limit=args.memory * args.processes)
        sa.samtools_index()
        sa.write(f'{args.output}.sort.bam')
        sa.remove_duplicates(
            dedupper=picardtools.MarkDuplicates(
                memory_gb=args.memory,
                assume_sorted=True,
                metrics_file=f'{args.output}.picard_rmdup_metrics.txt',
                remove_duplicates=False,
                temp_dir=args.tmp_dir
            )
        )
        sa.write(f'{args.output}.sort.md.bam')
        sa.samtools_view(
            mapping_quality=args.quality,
            remove_unpaired=True if not args.bowtie2 else False,
            remove_improperly_paired=True,
            remove_unmapped=True,
            remove_mate_unmapped=False if not args.bowtie2 else True,
            remove_not_primary=True,
            remove_fails_quality_check=False if not args.bowtie2 else True,
            remove_duplicate=True,
            remove_supplementary=True
        )
        sa.samtools_index()
        with open(f'{args.output}.quality_metrics.txt', 'w') as f:
            f.write(
                '\n'.join(
                    '\t'.join(str(val) for val in row) for row in (
                        ('PERCENT_MITOCHONDRIAL', 'PERCENT_BLACKLISTED'),
                        (
                            sa.percent_mitochondrial(),
                            sa.percent_blacklisted(
                                blacklist_path=args.blacklist_file
                            )
                        )
                    )
                )
                + '\n'
            )
        sa.restrict_chromosomes(*(tuple(range(1, 23)) + ('X',)))
        if args.remove_blacklisted_reads:
            sa.remove_blacklisted_reads(blacklist_path=args.blacklist_file)
        sa.samtools_index()
        sa.write(f'{args.output}.sort.filt.rmdup.bam')


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Align ATAC-seq reads to a reference genome'
    )
    io_group = parser.add_argument_group('I/O arguments')
    io_group.add_argument(
        'reads1',
        metavar='<path/to/reads_1.fastq[.gz]>',
        help='path to fastq files'
    )
    io_group.add_argument(
        'reads2',
        metavar='<path/to/reads_2.fastq[.gz]>',
        help='path to fastq files'
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
        help='number of processes (or threads) to use [4]'
    )
    align_group.add_argument(
        '--memory',
        metavar='<float>',
        type=float,
        default=4,
        help='maximum memory per thread in GB [4]'
    )
    align_group.add_argument(
        '--quality',
        metavar='<int>',
        type=int,
        default=30,
        help='mapping quality cutoff for samtools [30]'
    )
    align_group.add_argument(
        '--reference',
        metavar='<path/to/reference.fasta>',
        default=pyhg19.PATH,
        help=f'path to reference genome prepared for BWA [{pyhg19.PATH}]'
    )
    align_group.add_argument(
        '--bowtie2',
        action='store_true',
        help='use bowtie2 for alignment (instead of the default BWA)'
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
        metavar='<path/to/temp/file/dir>',
        default='/nfs/lab/tmp/',
        help='path to a directory where temporary files will be written'
    )
    args = parser.parse_args()
    if args.memory * args.processes < 5:
        raise RuntimeError(
            'Please provide at least 5 GB of memory in total '
            f'({args.processes} processes * {args.memory} GB memory is only '
            f'{args.memory * args.processes} GB)'
        )
    return args
