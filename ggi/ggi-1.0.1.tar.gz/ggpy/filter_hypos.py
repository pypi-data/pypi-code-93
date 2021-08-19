


import csv
import argparse


def getOpts():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description="""
                            Filter GGI results
    Example:

        * Standar usage:

            $ %(prog)s  [ggi out] -H [selected hypotheses]
""")
    parser.add_argument('ggi_out',
                        help='GGI table')
    parser.add_argument('-H', '--hypos',
                        metavar = "",
                        type    = str,
                        required=True,
                        default = None,
                        help    = 'Selected hypotheses')
    parser.add_argument('-p', '--pval',
                        metavar = "",
                        type    = int,
                        default = 0,
                        help    = '[Optional] minimum allowed p-value for rank 1 hypothesis [Default = 0]')
    parser.add_argument('-s', '--suffix',
                        metavar = "",
                        type    = str,
                        default = '_filtered',
                        help    = '[Optional] Suffix for output')
    args = parser.parse_args()
    return args

# alignment
def main():
    args = getOpts()

    my_f = lambda l: l[2] in to_select and l[3] == '1' and float(l[4]) >= pval

    ggi_result = args.ggi_out    
    pval  = args.pval
    hypos = args.hypos

    
    # ggi_result = '/Users/ulises/Desktop/GOL/software/fishlifeqc/postprocessing/joined_out_ggi_1018exons_protein.txt_rooted_groups.tsv'
    # pval = 0
    # to_select = [
    #     "(Outgroup,(Eso_salmo,(Argentiniformes,(Osme_Stomia,(Neoteleostei,Galaxiiformes)))));",
    #     "(Outgroup,((Eso_salmo,Argentiniformes),(Osme_Stomia,(Neoteleostei,Galaxiiformes))));"
    # ]

    to_select = []
    with open(hypos, 'r') as f:
        for i in f.readlines():
            line = i.strip().strip('"') 
            if line:
                to_select.append( line )

    table = []
    with open(ggi_result, 'r') as f:
        reader = csv.reader(f, delimiter = "\t")
        for row in reader:
            table.append(row)

    table_f = [ [ i[0],i[2] ] for i in table if my_f(i)]

    outfile_ = ggi_result + args.suffix
    # print(table_f)
    
    with open(outfile_, 'w') as f:
        writer = csv.writer(f, delimiter = "\t")
        writer.writerows( [['aln_base', 'hypothesis']]  + table_f)

if __name__ == "__main__":
    main()