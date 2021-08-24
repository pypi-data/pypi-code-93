#!/usr/bin/env python

import argparse


# ITT_OUTFILENAME = "support_tt.tsv"
# RF_OUTFILENAME = "RF_distance.tsv"

parser = argparse.ArgumentParser( formatter_class = argparse.RawDescriptionHelpFormatter, 
                                      description = '''
                                 GGI and Post-GGI
                                      ''')
subparsers = parser.add_subparsers(help='', dest='subcommand')

# ggi -------------------------------------------------------------------------
ggi = subparsers.add_parser('ggi',
                             help = "Gene-Genealogy Interrogation (GGI)",
                             formatter_class = argparse.RawDescriptionHelpFormatter, 
                             description="""

                    Gene-Genealogy Interrogation

* Standard usage:

    $ %(prog)s [exon files] -t [taxonomy file]

        note 1: The taxnomy file is CSV-formated and must 
                contain the following:

                names               group              
                [sequence header 1],[group of header 1]
                [sequence header 2],[group of header 2]
                [sequence header 3],[group of header 3]
                    ...                 ...      

        note 2: For n groups in the taxonomy file all possible
                topologies are generated if a topology file is 
                not given (see below). Here is a table 
                for reference

                n | Unrooted trees | Rooted tree 
                --+----------------+------------ 
                3 |              - |           3 
                4 |              3 |          15 
                5 |             15 |         105 
                6 |            105 |         945 
                7 |            945 |      10 395 
                8 |         10 395 |     135 135 
                9 |        135 135 |           - 

* Specify pre-defined hypothesis:

    $ %(prog)s [exon files] -t [taxonomy file] -H [file with topologies]
        
        note: `-H` accepts a group-based topologies

* Specify pre-defined extended hypothesis:

    $ %(prog)s [exon files] -H [file with topologies] -e

        note: `-e` specifies that topologies at `-H` files are 
                extended (i.e., with actual species and not groups)

""")

ggi.add_argument('-H','--hypothesis',
                    metavar="",
                    default = None,
                    help='[Optional] Pre-defined hypothesis file, either extended or not')
ggi.add_argument('-e','--extended',
                    action="store_true",
                    help='''[Optional] If selected, file with topologies contains
                    extended trees (i.e., species instead of groups)''')
ggi.add_argument('-w','--write_extended',
                    action="store_true",
                    help='''[Optional] If selected, extended topologies are written and exit''')
ggi.add_argument('-r','--rooted',
                    action="store_true",
                    help='''[Optional] If selected, all posible rooted topologies
                        are generated when pre-defined hypothesis file is not given''')
ggi.add_argument('-n', '--threads',
                    metavar = "",
                    type    = int,
                    default = 1,
                    help    = '[Optional] number of cpus [Default = 1]')
ggi.add_argument('-s','--suffix',
                    metavar="",
                    type= str,
                    default= "ggi.txt",
                    help='[Optional] Suffix for each written file [Default: ggi.txt]')


ggi_bl_raxml = ggi.add_argument_group('RAxML constrained tree parameters')
ggi_bl_raxml.add_argument('-E','--evomol',
                metavar="",
                type= str,
                default = 'GTRGAMMA',
                help='[Optional] RAxML evol. model for constrained tree inference [Default: GTRGAMMA]')
ggi_bl_raxml.add_argument('-c','--codon_aware',
                action="store_true",
                help='[Optional] If selected, codon partition file is added')
ggi_bl_raxml.add_argument('-i', '--iterations',
                metavar = "",
                type    = int,
                default = 1,
                help    = '[Optional] Number of iterations for MLEs [Default: 1]')


ggi_main_args = ggi.add_argument_group('required arguments')
ggi_main_args.add_argument('filenames',
                    metavar="alns",
                    nargs="*",
                    help='Alignments')   
ggi_main_args.add_argument('-t','--tax_file',
                    metavar="",
                    default = None,
                    # required= True,
                    help='Taxonomy file. Format in csv: "[sequence name],[group]"')    
ggi._action_groups.reverse()                     
# ggi -------------------------------------------------------------------------

# fstats -------------------------------------------------------------------------
fstats = subparsers.add_parser('features', help = "Features from both alignment and tree information",
                              formatter_class = argparse.RawDescriptionHelpFormatter, 
                              epilog = """
* codon_aware: currently only GC and Gap content
               can be obtained by codons

""",
                              description="""
                              
                    Summarize both alignment and tree information

Examples:

    * Standard usage:

        $ %(prog)s -A [alignment file extension] -T [tree file extension]

            Where '-A' and '-T' indicate file extensions for alignments and 
            trees, correspondingly.

""")
fstats.add_argument('-A','--aln',
                    metavar="ext",
                    type= str,
                    # required=True,
                    default=".fasta",
                    help="Alignment file extension [Default = '.fasta']") 
fstats.add_argument('-T','--tree',
                    metavar="ext",
                    type= str,
                    # required=True,
                    default=".tree",
                    help="Tree file extension [Default = '.tree']")  
fstats.add_argument('-p','--path',
                    metavar="",
                    type= str,
                    default=".",
                    help="[Optional] Path to above files [Default: '.']")   
fstats.add_argument('-t','--taxonomy',
                    metavar="",
                    type= str,
                    required=False,
                    help='[Optional] Taxonomy file [Default: None]')                      
# fstats.add_argument('-r','--reference',
#                      metavar="",
#                      type= str,
#                      default=None,
#                      help='[Optional] Reference tree [Default: None]')
# fstats.add_argument('-g','--group',
#                 metavar='',
#                 type= str,
#                 default=None,
#                 help='''[Optional] CSV-formated file containing alignmnet
#                         name and a label. This label is added as new column [Default: None]''')
fstats.add_argument('-c','--codon_aware',
                    action="store_true",
                    help='[Optional] If selected, metrics are obtained by codons*')
fstats.add_argument('-s','--suffix', 
                    metavar="",
                    type = str,
                    default='stats.tsv',
                    help='[Optional] suffix output names [Default = stats.tsv ]' )
fstats.add_argument('-n', '--threads',
                    metavar = "",
                    type    = int,
                    default = 1,
                    help    = '[Optional] number of cpus [Default = 1]')          
# fstats -----------------------------------------------------------------------

# post_ggi --------------------------------------------------------------------------
post_ggi_sub = subparsers.add_parser('post', help = "Classification of GGI hypothesis",
                              formatter_class = argparse.RawDescriptionHelpFormatter, 
                              description="""
                              
                    Post-GGI
Examples:

    * Standard usage:

        $ %(prog)s [ggi result] -f [features result] -c [comparison file]

        note 1: feature file is obtained from the 'features' subcomand
        note 2: comparison file is a CSV-formated file and it containts
                pairs of tree ids from the ggi result file:

                1,2
                1,3
                ...

                In above example, hypothesis 1 and hypothesis 2 are compared,
                then hypothesis 1 and hypothesis 3 are compared, and so on.

""")

post_ggi_sub.add_argument('all_ggi_results',
                      metavar = 'file',
                      help='file from the "ggi" subcomand')
post_ggi_sub.add_argument('-f','--features',
                    metavar="",
                    type= str,
                    required=True,
                    help='File with features of alignments and trees [Default: None]')
post_ggi_sub.add_argument('-c','--comparisons',
                    metavar="",
                    type= str,
                    required=True,
                    help='File with hypothesis id to compare [Default: None]')

post_ggi_sub.add_argument('-s','--suffix', 
                        metavar="",
                        type = str,
                        default='post_ggi',
                        help='[Optional] prefix name for outputs [Default = post_ggi]' )
post_ggi_sub.add_argument('-l', '--ncols',
                    metavar = "",
                    type    = int,
                    default = 3,
                    help    = '[Optional] number of columns for plotting confusion matrices [Default = 3]') 
post_ggi_sub.add_argument('-n', '--threads',
                    metavar = "",
                    type    = int,
                    default = 1,
                    help    = '[Optional] number of cpus [Default = 1]') 
# post_ggi --------------------------------------------------------------------------


def main():

    wholeargs = parser.parse_args()

    if wholeargs.subcommand == "ggi":

        from ggpy.ggi import GGI

        GGI(
            sequences       = wholeargs.filenames,
            taxonomyfile    = wholeargs.tax_file,
            topologies      = wholeargs.hypothesis,
            are_extended    = wholeargs.extended,
            rooted          = wholeargs.rooted,
            codon_partition = wholeargs.codon_aware,
            threads         = wholeargs.threads,
            evomodel        = wholeargs.evomol,
            iterations      = wholeargs.iterations,
            write_extended  = wholeargs.write_extended,
            suffix          = wholeargs.suffix,
        ).main()

    elif wholeargs.subcommand == "features":

        from fishlifetraits.stats import Features # expensive import

        Features(
            taxonomyfile   = wholeargs.taxonomy,
            path           = wholeargs.path,
            fasta_ext      = wholeargs.aln,
            tree_ext       = wholeargs.tree,
            reference_tree = None,
            groups_file    = None,
            codon_aware    = wholeargs.codon_aware,
            threads        = wholeargs.threads,
            suffix         = wholeargs.suffix,
        ).write_stats()

    elif wholeargs.subcommand == "post":

        from ggpy.classifier import Post_ggi

        Post_ggi(
            feature_file    = wholeargs.features,
            all_ggi_results  = wholeargs.all_ggi_results,
            file_comparisons = wholeargs.comparisons,
            model_prefix     = wholeargs.suffix,
            cnfx_ncols       = wholeargs.ncols,
            threads          = wholeargs.threads

        ).xgboost_iterator()

if __name__ == "__main__":
    main()
