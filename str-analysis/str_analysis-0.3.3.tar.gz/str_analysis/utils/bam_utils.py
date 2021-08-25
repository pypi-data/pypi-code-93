import collections
import logging
import math
import os
import pysam
import re

from utils.misc import parse_interval, run, intervals_genomic_sort_order


def parse_picard_metrics(picard_metrics_file_path):
    """Parses the header and 1st data line from a Picard metrics file.
    Returns them as a dictionary of key-value pairs.
    """

    with open(picard_metrics_file_path) as metrics_file:
        header_line = None
        for line in metrics_file:
            if line.strip() == "" or line.startswith("#"):
                continue
            elif header_line is None:
                header_line = line.strip("\n").split("\t")
            else:
                data_line = line.strip("\n").split("\t")
                return dict(zip(header_line, data_line))

    raise ValueError(f"Unable to parse {picard_metrics_file_path}")


def compute_read_coverage(bam_or_cram_path, chrom, start_1based, end_1based, reference_filename=None):
    bam_file = pysam.AlignmentFile(bam_or_cram_path, reference_filename=reference_filename)

    bases_in_interval = 0
    read_length = None
    read_counter = 0
    for r in bam_file.fetch(chrom, start_1based, end_1based):
        if r.is_unmapped or r.is_secondary:
            continue

        read_length = r.infer_query_length()
        if read_length is None:
            continue

        read_start_1based = r.reference_start + 1
        read_end_1based = r.reference_start + read_length

        if read_end_1based < start_1based or read_start_1based > end_1based:
            continue

        read_counter += 1
        bases_in_interval += min(read_end_1based, end_1based) - max(read_start_1based, start_1based) + 1

    mean_coverage = bases_in_interval/float(end_1based - start_1based + 1)

    return mean_coverage, read_counter, read_length


def compute_bam_stats(ref_fasta_path, bam_path, picard_jar_path, chrom, start_1based, end_1based, stop_after_num_reads=10**5, temp_dir="/tmp"):
    """Computes read length, total reads, and fragment size & stddev in the given bam file at the given genomic interval.
    Processes only the first {stop_after_num_reads} to compute fragment size mean & stddev.
    """

    mean_coverage, read_counter, read_length = compute_read_coverage(bam_path, chrom, start_1based, end_1based)
    if mean_coverage == 0 or read_length is None:
        raise ValueError(f"{bam_path} doesn't have any reads in {chrom}:{start_1based}-{end_1based}")

    # compute coverage
    #interval_file_contents = "\t".join(map(str, [chrom, start_1based, end_1based, "+", "repeat_interval"]))
    #run(f"samtools view -H {bam_path} > repeat.interval; echo '{interval_file_contents}' >> repeat.interval")
    #run(f"java -jar {picard_jar_path} CollectWgsMetrics R={ref_fasta_path} I={bam_path} READ_LENGTH={read_length} INTERVALS=repeat.interval O=wgs_metrics.txt")
    #wgs_metrics = parse_picard_metrics("wgs_metrics.txt")
    #mean_coverage = float(wgs_metrics['MEAN_COVERAGE'])

    # compute fragment size mean & stddev
    insert_size_metrics_path = os.path.join(temp_dir, "insert_size_metrics.txt")
    run(f"java -Xmx2G -jar {picard_jar_path} CollectInsertSizeMetrics "
        f"R={ref_fasta_path} "
        f"I={bam_path} "
        f"HISTOGRAM_FILE=/dev/null "
        "VERBOSITY=WARNING "
        f"O={insert_size_metrics_path} "
        f"STOP_AFTER={stop_after_num_reads} ")  # f"  2> /dev/null"

    insert_size_metrics = parse_picard_metrics(insert_size_metrics_path)

    mean_fragment_length = float(insert_size_metrics['MEAN_INSERT_SIZE'])
    fragment_length_stddev = float(insert_size_metrics['STANDARD_DEVIATION'])

    # compute average MAPQ
    output = run(f"samtools view {bam_path} | head -n {stop_after_num_reads*2} | tail -n {stop_after_num_reads} "
                 "| awk '{ sum += $5 } END { if (NR > 0) print sum / NR }'")
    try:
        mean_mapq = float(output)
    except:
        raise ValueError(f"Unable to parse read length from {bam_path}")

    bam_stats = {
        "read_length": read_length,
        "num_read_pairs": read_counter//2,
        "mean_fragment_length": mean_fragment_length,
        "fragment_length_stddev": fragment_length_stddev,
        "mean_coverage": mean_coverage,
        "mean_MAPQ": mean_mapq,
    }

    logging.info(f"bam stats for {bam_path} in {chrom}:{start_1based}-{end_1based}")
    for key, value in bam_stats.items():
        logging.info(f"    {key}: {value}")

    return bam_stats


def simulate_reads(
        ref_fasta_path,
        reference_sequence,
        read_length,
        mean_coverage,
        mean_fragment_length,
        fragment_length_stddev,
        output_filename_prefix,
        generate_bam_index=True,
        wgsim_base_error_rate=0.001,
        wgsim_mutation_rate=0.0001,
        wgsim_fraction_indels=0.0001,
        wgsim_p_indel_extension=0.0001,
        force=False):
    """Generates simulated reads with the given parameters and returns the output bam path."""

    logging.info("-"*100)
    logging.info(f"Simulating reads from a {len(reference_sequence)}bp reference sequence")

    # save synthetic reference to file
    synthetic_reference_file_path = f"simulated_reference__{output_filename_prefix}.fa"
    if not force and os.path.isfile(synthetic_reference_file_path):
        logging.info(f"{synthetic_reference_file_path} already exists. Will not re-generate it.")
    else:
        logging.info(f"{synthetic_reference_file_path} doesn't exist. Generating it...")

        with open(synthetic_reference_file_path, "w") as output_file:
            output_file.write(f">{output_filename_prefix}\n")
            output_file.write(reference_sequence)

    # convert mean_coverage and interval length to num_read_pairs
    interval_length = len(reference_sequence)
    num_read_pairs = mean_coverage * interval_length/float(read_length * 2)

    logging.info(
        f"    interval_length={interval_length}, N_read_pairs={num_read_pairs}, read_length={read_length}bp, "
        f"mean_coverage={mean_coverage}x, u={mean_fragment_length} sigma={fragment_length_stddev}")

    fastq1_path =  f"{output_filename_prefix}1.fq"
    fastq2_path =  f"{output_filename_prefix}2.fq"
    if not force and os.path.isfile(fastq1_path) and os.path.isfile(fastq2_path):
        logging.info(f"{fastq1_path} and {fastq2_path} already exist. Will not re-generate them.")
    else:
        logging.info(f"{fastq1_path} and {fastq2_path} don't exist. Generating them...")

        run(f"wgsim -1 {read_length} -2 {read_length} " +
            (f"-e {wgsim_base_error_rate} " if wgsim_base_error_rate else "") +
            (f"-r {wgsim_mutation_rate} " if wgsim_mutation_rate else "") +
            (f"-R {wgsim_fraction_indels} " if wgsim_fraction_indels else "") +
            (f"-X {wgsim_p_indel_extension} " if wgsim_p_indel_extension else "") +
            f" -Q B -N {int(num_read_pairs)} -d {mean_fragment_length} -s {fragment_length_stddev} "
            f"{synthetic_reference_file_path} "
            f"{fastq1_path} "
            f"{fastq2_path} ")  # "  2> /dev/null"

    if not force and os.path.isfile(f"{output_filename_prefix}.aligned.bam"):
        logging.info(f"{output_filename_prefix}.aligned.bam already exists. Will not re-generate it.")
    else:
        logging.info(f"{output_filename_prefix}.aligned.bam doesn't exist. Generating it...")

        # align fastq to reference sequence
        run(f"bwa mem -M -R $(echo '@RG\\tID:1\\tSM:1_1\\tLB:1_1\\tPL:ILLUMINA') "
            f"{ref_fasta_path} "
            f"{output_filename_prefix}1.fq "
            f"{output_filename_prefix}2.fq "
            f"| samtools sort -o {output_filename_prefix}.aligned.bam - ")  # "  2> /dev/null"

    output_filename_prefix += ".aligned"

    if generate_bam_index:
        run(f"samtools index {output_filename_prefix}.bam")

    return f"{output_filename_prefix}.bam"


def merge_bams(output_bam_path, *input_bam_paths, force=False):
    """Run picard MergeSamFiles to merge the given bams. Assumes input bams are already coordinate-sorted."""
    logging.info("-"*100)
    if not force and os.path.isfile(output_bam_path):
        logging.info(f"{output_bam_path} already exists. Will not re-generate it.")
        return output_bam_path

    run(f"samtools merge {output_bam_path} " + " ".join(input_bam_paths))
    run(f"samtools index {output_bam_path}")

    #run(f"cp {output_bam_path.replace('.bam', '.bai')} {output_bam_path}.bai")  # rename .bai file to .bam.bai

    return output_bam_path
