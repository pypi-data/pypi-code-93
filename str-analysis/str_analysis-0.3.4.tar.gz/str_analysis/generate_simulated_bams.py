#!/usr/bin/env python3

import argparse
import json
import logging
import os
import pyfaidx
import tempfile
import unittest

from str_analysis.utils.bam_utils import compute_bam_stats, simulate_reads, merge_bams, generate_bam_donut
from str_analysis.utils.fasta_utils import get_reference_sequence
from str_analysis.utils.misc import parse_interval, run

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')


def main():
    p = argparse.ArgumentParser(description="This script lets the user add a tandem repeat expansion of a given length "
                                            "to some locus in the reference genome. It then simulates paired-end reads from this locus, and runs the bwa "
                                            "aligner to generate a synthetic .bam file. This .bam file is useful for checking how well different tandem "
                                            "repeat calling tools do at calling the given expansion. "
                                            "The key inputs are: a reference fasta file, the genomic locus coordinates, the repeat unit motif and number "
                                            "of copies to insert at this locus. "
                                            "This script requires the following programs to be installed and on PATH: bedtools, samtools, bwa, wgsim"
                                )

    p.add_argument("-e", "--wgsim-base-error-rate", type=float, help="wgsim -e arg (base error rate [0.020]). GangSTR paper uses 0.001.")
    p.add_argument("-r", "--wgsim-mutation-rate", type=float, help="wgsim -r arg (rate of mutations [0.0010]). GangSTR paper uses 0.0001")
    p.add_argument("-R", "--wgsim-fraction-indels", type=float, help="wgsim -R arg (fraction of indels [0.15]). GangSTR paper uses 0.0001")
    p.add_argument("-X", "--wgsim-p-indel-extension", type=float, help="wgsim  -X arg (probability an indel is extended [0.30]). GangSTR paper uses 0.0001")

    p.add_argument("-u", "--new-repeat-unit", required=True, help="The repeat unit sequence to insert at 'ref_repeat_coords'")
    p.add_argument("-n", "--num-copies", type=int, required=True, help="How many copies of the repeat unit to insert.")
    p.add_argument("-t", "--num-copies-max", type=int, help="If -t is specified, multiple bams will be "
                                                            "generated - one for each copy number between -n and -t, with step size -i.")
    p.add_argument("-i", "--num-copies-increment", type=int, default=5, help="If -t is specified, multiple bams will be "
                                                                             "generated - one for each copy number between -n and -t, with step size -i.")
    p.add_argument("-l", "--num-copies-list", type=str, help="As an alternative to -n, -t and -i, this sets a "
                                                             "comma-seperated list of copy numbers to simulate.")
    p.add_argument("--num-copies2", type=int, help="If --het, how many copies of the repeat unit to insert for "
                                                   "the 2nd alt allele. Defaults to the number of copies in the reference genome.")

    p.add_argument("-p", "--padding", type=int, default=5000, help="How many bases on either side of the reference "
                                                                   "repeat region to include in the synthetic reference from which reads are simulated.")

    p.add_argument("--het", action="store_true", help="Simulate an individual that is heterozygous for "
                                                      "--num-copies of --new-repeat-unit.")
    p.add_argument("--hom", action="store_true", help="Simulate an individual that is homozygous for "
                                                      "--num-copies of --new-repeat-unit.")

    p.add_argument("-f", "--force", action="store_true", help="Generated simulated .bam even if it already exists.")
    p.add_argument("-v", "--verbose", action="store_true", help="Verbose output.")

    p.add_argument("--insert-simulated-reads-into-template-bam", action="store_true", help="Create the output .bam file"
                                                                                           "by merging simulated reads with reads in the template bam that don't overlap the simulated region. This "
                                                                                           "makes the output .bam file more realistic since it will have data for all regions, including off-target regions.")

    p.add_argument("--output-off-target-regions", action="store_true", help="Computes off-target regions and outputs them to a repeat_regions.bed output file.")
    p.add_argument("--min-off-target-coverage", type=int, default=5, help="Minimum number of reads that has to map to a particular "
                                                                          "off-target region in order for this region to be included in the output. Only relevant when --output-off-target-regions is also used.")
    p.add_argument("--off-target-regions-padding", type=int, help="Pad off-target regions by this many bases "
                                                                  "(including any regions provided via --set-off-target-regions).")

    p.add_argument("--picard-jar-path", help="Path of picard.jar", default="picard.jar")

    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--template-bam-path", help="simulated reads will mimic this bam's read length, paired-end fragment "
                                               "size distribution, and coverage in the repeat region.")
    g.add_argument("--coverage", type=float, help="Explicitly set simulated read coverage.")

    p.add_argument("--read-length", type=int, help="explicitly set read length of simulated reads", default=150)
    p.add_argument("--fragment-length", type=float, default=345)
    p.add_argument("--fragment-length-stddev", type=float, default=100)

    p.add_argument("--temp-dir", default="/tmp")

    p.add_argument("ref_repeat_coords", help="1-based coordinates in the reference genome (eg. chr1:12345-54321). "
                                             "The reference bases in this interval will be replaced with -n copies of the --repeat-unit sequence.")
    p.add_argument("ref_fasta_path", help="reference fasta file path. Should also have a bwa index for running bwa mem.")

    args = p.parse_args()

    het_or_hom_list = []
    if args.het or (not args.het and not args.hom):
        het_or_hom_list.append("het")
    if args.hom or (not args.het and not args.hom):
        het_or_hom_list.append("hom")

    # validate paths
    for path in (args.ref_fasta_path, args.template_bam_path, args.temp_dir):
        if path and not os.path.exists(path):
            p.error(f"Path not found: {path}")

    args.coverage = int(args.coverage)

    generate_simulated_bams(
        args.ref_fasta_path,
        args.ref_repeat_coords,
        args.new_repeat_unit,
        het_or_hom_list=het_or_hom_list,
        coverage=args.coverage,
        read_length=args.read_length,
        fragment_length=args.fragment_length,
        fragment_length_stddev=args.fragment_length_stddev,
        padding=args.padding,
        template_bam_path=args.template_bam_path,
        num_copies=args.num_copies,
        num_copies2=args.num_copies2,
        num_copies_list=args.num_copies_list,
        num_copies_max=args.num_copies_max,
        num_copies_increment=args.num_copies_increment,
        picard_jar_path=args.picard_jar_path,
        output_off_target_regions=args.output_off_target_regions,
        min_off_target_coverage=args.min_off_target_coverage,
        wgsim_base_error_rate=args.wgsim_base_error_rate,
        wgsim_mutation_rate=args.wgsim_mutation_rate,
        wgsim_fraction_indels=args.wgsim_fraction_indels,
        wgsim_p_indel_extension=args.wgsim_p_indel_extension,
        insert_simulated_reads_into_template_bam=args.insert_simulated_reads_into_template_bam,
        force=args.force,
        verbose=args.verbose,
    )


def generate_simulated_bams(
        ref_fasta_path,
        ref_repeat_coords,
        new_repeat_unit,
        het_or_hom_list=("het", "hom"),
        coverage=30,
        read_length=150,
        fragment_length=345,
        fragment_length_stddev=100,
        padding=1500,
        template_bam_path=None,
        num_copies=None,
        num_copies2=None,
        num_copies_list=None,
        num_copies_max=None,
        num_copies_increment=None,
        picard_jar_path=None,
        output_off_target_regions=False,
        min_off_target_coverage=0,
        wgsim_base_error_rate=0.001,
        wgsim_mutation_rate=0.0001,
        wgsim_fraction_indels=0.0001,
        wgsim_p_indel_extension=0.0001,
        insert_simulated_reads_into_template_bam=False,
        write_out_bam_stats=False,
        write_out_repeat_regions_bed=False,
        force=False,
        verbose=False,
):

    # generate synthetic reference sequence
    chrom, start_1based, end_1based = parse_interval(ref_repeat_coords)

    fasta_obj = pyfaidx.Fasta(ref_fasta_path, one_based_attributes=False, as_raw=True)

    # figure out .bam stats
    if template_bam_path:
        bam_stats = compute_bam_stats(
            ref_fasta_path,
            template_bam_path,
            chrom,
            start_1based - padding,
            end_1based + padding)
    else:
        bam_stats = {
            "mean_coverage": coverage,
            "mean_fragment_length": fragment_length,
            "fragment_length_stddev": fragment_length_stddev,
            "read_length": read_length,
        }


    # compute output filename prefix
    output_filename_prefix = f"{chrom}-{start_1based}-{end_1based}__with_{padding}_pad__{read_length}_readlen__{coverage}x_cov__wgsim_e-{wgsim_base_error_rate}"

    # if args.het, generate ALT allele1. This allele is the ref allele, or if num_copies2, then then num_copies2 allele.
    if "het" in het_or_hom_list:
        if num_copies2:
            logging.info(f"Simulating ALT allele1 with {num_copies2} copies of the repeat.")
            synthetic_alt_allele1_reference_sequence = generate_synthetic_reference_sequence(
                fasta_obj,
                chrom,
                start_1based,
                end_1based,
                padding,
                new_repeat_unit,
                num_copies2)
            ref_reads_output_prefix = f"{output_filename_prefix}__{num_copies2:4d}x{new_repeat_unit}__het_ref_allele".replace(" ", "_")
        else:
            logging.info(f"Simulating ALT allele1 with same number of copies as the reference.")
            synthetic_alt_allele1_reference_sequence = get_reference_sequence(
                fasta_obj,
                chrom,
                start_1based - padding,
                end_1based + padding)
            ref_reads_output_prefix = f"{output_filename_prefix}__het_ref_allele"

        synthetic_ref_bam_path = \
            simulate_reads(
                ref_fasta_path,
                synthetic_alt_allele1_reference_sequence,
                bam_stats["read_length"],
                bam_stats["mean_coverage"] / 2,  # divide by 2 to generate ref and alt .bams with 1/2 original coverage, and then merge them.
                bam_stats["mean_fragment_length"],
                bam_stats["fragment_length_stddev"],
                ref_reads_output_prefix,
                wgsim_base_error_rate=wgsim_base_error_rate,
                wgsim_mutation_rate=wgsim_mutation_rate,
                wgsim_fraction_indels=wgsim_fraction_indels,
                wgsim_p_indel_extension=wgsim_p_indel_extension,
                force=force)

    # simulate ALT allele(s) 2, with het and/or hom genotype
    if num_copies_list:
        num_copies_list = [int(num_copies) for num_copies in num_copies_list.split(",")]
    elif num_copies_max:
        num_copies_list = range(num_copies, num_copies_max+1, num_copies_increment)
    else:
        num_copies_list = [num_copies]

    reference_bam_donut = None
    for het_or_hom in het_or_hom_list:
        simulated_bam_paths = []
        for num_copies in num_copies_list:

            synthetic_alt_allele2_reference_sequence = generate_synthetic_reference_sequence(
                fasta_obj,
                chrom,
                start_1based,
                end_1based,
                padding,
                new_repeat_unit,
                num_copies)

            output_bam_prefix = f"{output_filename_prefix}__{num_copies:4d}x{new_repeat_unit}".replace(" ", "_")
            if num_copies2:
                output_bam_prefix += f"__{num_copies2:4d}x{new_repeat_unit}".replace(" ", "_")

            synthetic_alt_bam_path = simulate_reads(
                ref_fasta_path,
                synthetic_alt_allele2_reference_sequence,
                bam_stats["read_length"],
                bam_stats["mean_coverage"] / (2 if het_or_hom == "het" else 1),
                bam_stats["mean_fragment_length"],
                bam_stats["fragment_length_stddev"],
                f"{output_bam_prefix}__{het_or_hom}" + ("__alt_allele" if het_or_hom == "het" else ""),
                force=force)

            if het_or_hom == "het":
                merged_ref_alt_bam_path = merge_bams(
                    f"{output_bam_prefix}__{het_or_hom}.bam",
                    synthetic_ref_bam_path,
                    synthetic_alt_bam_path,
                    force=force)

                #run(f"rm {synthetic_alt_bam_path} {synthetic_alt_bam_path}.bai")
            else:
                merged_ref_alt_bam_path = synthetic_alt_bam_path

            simulated_bam_paths.append(merged_ref_alt_bam_path)

            # for merged_ref_alt_bam, print bam stats and regions in other parts of the genome to which the simulated reads
            # mis-align (eg. off-target regions) - this is just for logging
            if verbose:
                compute_bam_stats(
                    ref_fasta_path,
                    merged_ref_alt_bam_path,
                    picard_jar_path,
                    chrom,
                    start_1based - padding,
                    end_1based + padding)

                compute_off_target_regions(
                    merged_ref_alt_bam_path,
                    ref_fasta_path,
                    interval=f"{chrom}:{start_1based - padding}-{end_1based + padding}",
                    verbose=verbose)

        # compute off-target regions based on all simulated bams together
        off_target_regions = None
        if output_off_target_regions:
            all_simulated_bams_merged_bam_path = f"{output_filename_prefix}__all_{het_or_hom}.bam"
            merge_bams(
                all_simulated_bams_merged_bam_path,
                *simulated_bam_paths,
                force=force)

            off_target_regions, _ = compute_off_target_regions(
                all_simulated_bams_merged_bam_path,
                ref_fasta_path,
                f"{chrom}:{start_1based - padding}-{end_1based + padding}",
                coverage_threshold=min_off_target_coverage, verbose=True)
            off_target_regions = [r for r, read_count in off_target_regions]


            #run(f"rm {all_simulated_bams_merged_bam_path} {all_simulated_bams_merged_bam_path}.bai")

        # if --insert-simulated-reads-into-template-bam, merge the synthetic bam(s) with the reference donut .bam
        if insert_simulated_reads_into_template_bam:
            if reference_bam_donut is None:
                # create copy of the template bam file, but without reads at the locus where reads are being simulated.
                # make the hole smaller by read_length on each side so that simulated bams fit in the hole without a drop in coverage at the seams.
                reference_bam_donut = generate_bam_donut(
                    template_bam_path,
                    chrom,
                    start_1based - padding + bam_stats["read_length"],
                    end_1based + padding - bam_stats["read_length"],
                    off_target_regions,
                    f"{output_filename_prefix}__reference_bam_donut")

            simulated_bam_paths_with_original = []
            for simulated_bam_path in simulated_bam_paths:
                output_bam_path = simulated_bam_path.replace(".bam", "__with_original_data.bam")
                merge_bams(
                    output_bam_path,
                    reference_bam_donut,
                    simulated_bam_path,
                    force=force)

                simulated_bam_paths_with_original.append(output_bam_path)
            simulated_bam_paths = simulated_bam_paths_with_original


    # write bam_stats.json
    if write_out_bam_stats:
        logging.info("Writing out bam_stats.json")
        with open(f"bam_stats.json", "w") as reference_bam_stats_file:
            json.dump(bam_stats, reference_bam_stats_file)

    # write repeat_regions.bed
    if write_out_repeat_regions_bed:
        logging.info("Writing out repeat_regions.bed")
        with open(f"repeat_regions.bed", "w") as repeat_region_bed_file:
            repeat_region_bed_file.write("\t".join(map(str, [
                chrom,
                start_1based - 1,
                end_1based,
                new_repeat_unit,
                num_copies,  # max number of copies that were simulated above
                ",".join(off_target_regions) if off_target_regions is not None else "",
                #",".join(sorted(off_target_regions, key=genomic_order)),
            ])) + "\n")


def generate_synthetic_reference_sequence(fasta_obj, chrom, start_1based, end_1based, padding_length, repeat_unit, num_copies):
    """Generates a nucleotide sequence that consists of {num_copies} of the {repeat_unit} surrounded by {padding_length}
    bases from the reference on either side of the interval given by {chrom}:{start_1based}-{end_1based}.
    """

    if padding_length == 0:
        return repeat_unit * num_copies

    if chrom not in fasta_obj:
        raise ValueError(f"Invalid chromosome name: {chrom}")

    left_padding_start_1based = max(1, start_1based - padding_length)
    left_padding = get_reference_sequence(fasta_obj, chrom, left_padding_start_1based, start_1based - 1)

    chromosome_length = len(fasta_obj[chrom])
    right_padding_end_1based = min(end_1based + padding_length, chromosome_length)
    right_padding = get_reference_sequence(fasta_obj, chrom, end_1based + 1, right_padding_end_1based)

    return left_padding + repeat_unit * num_copies + right_padding


def compute_off_target_regions(merged_bam_path, ref_fasta_path, interval=None, coverage_threshold=5, verbose=False):
    """Returns a list of genomic intervals that are outside the locus given by {chrom}:{start_1based}-{end_1based}
    but contain at least {coverage_threshold} aligned reads. This means that reads from the given locus can mis-align to
    these other regions.
    """

    #on_target_count = int(run(f"samtools view -c {merged_bam_path} {chrom}:{start_1based}-{end_1based}"))

    # compute off-target regions command
    off_target_reads_command = ""
    if interval is not None:
        chrom, start_1based, end_1based = parse_interval(interval)
        logging.info(f"Computing off-target regions for {chrom}:{start_1based}-{end_1based}...")
        off_target_reads_command = f"echo '{chrom}\t{start_1based - 1}\t{end_1based}' "
        off_target_reads_command += f"| bedtools intersect -nonamecheck -v -wa -a {merged_bam_path} -b - "
        off_target_reads_command += f"| samtools view -F 4 -b - "  # exclude unmapped reads because this causes errors
    else:
        off_target_reads_command += f"samtools view -F 4 -b {merged_bam_path} "  # exclude unmapped reads because this causes errors

    logging.info(f"Coverage threshold to output an off-target region: {coverage_threshold}")

    off_target_reads_command += f"| bedtools merge -d 100 "  # merge reads' intervals
    off_target_reads_command += f"| bedtools slop -b 150 -g {ref_fasta_path}.fai "
    off_target_reads_command += f"| bedtools sort "
    off_target_reads_command += f"| bedtools intersect -nonamecheck -wa -a - -b {merged_bam_path} -c "   # add counts of how many reads mapped to each off-target interval
    off_target_reads_command += f"| sort -n -k4 -r "   # sort by these counts, so that the 1st interval is the one with the most reads, etc.
    off_target_regions = [off_target_region for off_target_region in run(off_target_reads_command).strip().split("\n") if off_target_region]

    # print some stats
    total_read_count = int(run(f"samtools view -c {merged_bam_path}"))

    try:
        off_target_read_count = sum([int(off_target_region.split("\t")[-1]) for off_target_region in off_target_regions])
    except ValueError:
        off_target_read_count = 0

    if total_read_count > 0:
        fraction_of_reads_that_map_to_off_target_regions = off_target_read_count/total_read_count
    else:
        fraction_of_reads_that_map_to_off_target_regions = 0

    logging.info(f"Found {len(off_target_regions)} off-target regions. "
                 f"{off_target_read_count} out of {total_read_count} reads "
                 f"({0 if not total_read_count else (100*off_target_read_count/total_read_count):0.1f}%) "
                 f"map to these off-target regions.")

    if verbose or len(off_target_regions) <= 7:
        logging.info("\n" + "\n".join(off_target_regions))

    off_target_region_list = []
    for off_target_region in off_target_regions:
        fields = off_target_region.strip("\n").split("\t")
        if len(fields) <= 3:
            logging.warning(f"Counts column missing for off_target_region: {off_target_region}. Skipping..." )
            continue

        # Skip loci with less than {coverage_threshold} reads in order to reduce noise
        num_reads_mapped_to_region = int(fields[3])
        if num_reads_mapped_to_region < coverage_threshold:
            continue
        off_target_region_list.append((f"{fields[0]}:{max(1, int(fields[1]))}-{int(fields[2])}", num_reads_mapped_to_region))

    return off_target_region_list, fraction_of_reads_that_map_to_off_target_regions


if __name__ == "__main__":
    main()


class Tests(unittest.TestCase):

    def setUp(self):
        self.temp_fasta_file = tempfile.NamedTemporaryFile("w", suffix=".fasta", delete=False)
        self.temp_fasta_file.write(">chrTest1\n")
        self.temp_fasta_file.write("ACGTACGT\n")

        self.temp_fasta_file.write(">chrTest2\n")
        self.temp_fasta_file.write(f"ACGT{'CAG'*2}ACGT\n")
        self.temp_fasta_file.close()

        self.fasta_obj = pyfaidx.Fasta(self.temp_fasta_file.name, one_based_attributes=False, as_raw=True)


    def test_get_reference_sequence(self):
        seq = get_reference_sequence(self.fasta_obj, chrom="chrTest1", start_1based=1, end_1based=5)
        self.assertEqual(seq, "ACGTA")

        seq = get_reference_sequence(self.fasta_obj, chrom="chrTest1", start_1based=8, end_1based=8)
        self.assertEqual(seq, "T")

        seq = get_reference_sequence(self.fasta_obj, chrom="chrTest1", start_1based=8, end_1based=10)
        self.assertEqual(seq, "T")

        seq = get_reference_sequence(self.fasta_obj, chrom="chrTest1", start_1based=9, end_1based=20)
        self.assertEqual(seq, "")

        seq = get_reference_sequence(self.fasta_obj, chrom="chrTest1", start_1based=0, end_1based=1)
        self.assertEqual(seq, "")


    def test_generate_synthetic_reference_sequence(self):
        seq = generate_synthetic_reference_sequence(self.fasta_obj, chrom="chrTest2", start_1based=5, end_1based=10, padding_length=4, repeat_unit="CAG", num_copies=0)
        self.assertEqual(seq, "ACGTACGT")

        seq = generate_synthetic_reference_sequence(self.fasta_obj, chrom="chrTest2", start_1based=5, end_1based=10, padding_length=2, repeat_unit="CAG", num_copies=0)
        self.assertEqual(seq, "GTAC")

        seq = generate_synthetic_reference_sequence(self.fasta_obj, chrom="chrTest2", start_1based=5, end_1based=10, padding_length=2, repeat_unit="CAG", num_copies=3)
        self.assertEqual(seq, "GTCAGCAGCAGAC")

        seq = generate_synthetic_reference_sequence(self.fasta_obj, chrom="chrTest2", start_1based=5, end_1based=10, padding_length=2, repeat_unit="CAG", num_copies=10)
        self.assertEqual(seq, "GTCAGCAGCAGCAGCAGCAGCAGCAGCAGCAGAC")

    def tearDown(self):
        if os.path.isfile(self.temp_fasta_file.name):
            os.remove(self.temp_fasta_file.name)



# wgsim command line options
"""
wgsim [options] <in.ref.fa> <out.read1.fq> <out.read2.fq>

Options: -e FLOAT      base error rate [0.020]
         -d INT        outer distance between the two ends [500]
         -s INT        standard deviation [50]
         -N INT        number of read pairs [1000000]
         -1 INT        length of the first read [70]
         -2 INT        length of the second read [70]
         -r FLOAT      rate of mutations [0.0010]
         -R FLOAT      fraction of indels [0.15]
         -X FLOAT      probability an indel is extended [0.30]
         -S INT        seed for random generator [0, use the current time]
         -A FLOAT      discard if the fraction of ambiguous bases higher than FLOAT [0.05]
         -h            haplotype mode
         
"""

