#!/usr/bin/env python

import argparse


def getOpts():

    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
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

    parser.add_argument('-H','--hypothesis',
                        metavar="",
                        default = None,
                        help='[Optional] Pre-defined hypothesis file, either extended or not')
    parser.add_argument('-e','--extended',
                        action="store_true",
                        help='''[Optional] If selected, file with topologies contains
                        extended trees (i.e., species instead of groups)''')
    parser.add_argument('-w','--write_extended',
                        action="store_true",
                        help='''[Optional] If selected, extended topologies are written and exit''')
    parser.add_argument('-r','--rooted',
                        action="store_true",
                        help='''[Optional] If selected, all posible rooted topologies
                         are generated when pre-defined hypothesis file is not given''')
    parser.add_argument('-n', '--threads',
                        metavar = "",
                        type    = int,
                        default = 1,
                        help    = '[Optional] number of cpus [Default = 1]')
    parser.add_argument('-s','--suffix',
                        metavar="",
                        type= str,
                        default= "ggi.txt",
                        help='[Optional] Suffix for each written file [Default: ggi.txt]')


    bl_raxml = parser.add_argument_group('RAxML constrained tree parameters')
    bl_raxml.add_argument('-E','--evomol',
                    metavar="",
                    type= str,
                    default = 'GTRGAMMA',
                    help='[Optional] RAxML evol. model for constrained tree inference [Default: GTRGAMMA]')
    bl_raxml.add_argument('-c','--codon_aware',
                    action="store_true",
                    help='[Optional] If selected, codon partition file is added')
    bl_raxml.add_argument('-i', '--iterations',
                    metavar = "",
                    type    = int,
                    default = 1,
                    help    = '[Optional] Number of iterations for MLEs [Default: 1]')


    main_args = parser.add_argument_group('required arguments')
    main_args.add_argument('filenames',
                        metavar="alns",
                        nargs="*",
                        help='Alignments')   
    main_args.add_argument('-t','--tax_file',
                        metavar="",
                        default = None,
                        # required= True,
                        help='Taxonomy file. Format in csv: "[sequence name],[group]"')                                    

    parser._action_groups.reverse()
    args = parser.parse_args()
    return args

def main():
    args = getOpts()
    
    from ggpy.ggi import GGI
    # print(args)
    GGI(
        sequences       = args.filenames,
        taxonomyfile    = args.tax_file,
        topologies      = args.hypothesis,
        are_extended    = args.extended,
        rooted          = args.rooted,
        codon_partition = args.codon_aware,
        threads         = args.threads,
        evomodel        = args.evomol,
        iterations      = args.iterations,
        write_extended  = args.write_extended,
        suffix          = args.suffix,
    ).main()


if __name__ == "__main__":
    main()

