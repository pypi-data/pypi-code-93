#!/usr/bin/env python

import argparse

import csv
import dendropy

def getOpts():

    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description="""

            Root groups at ggpy results

	* Example:

	    $ root_groups.py [ggpy results] -r [file with outgroups]

            note: ggpy results are files containing the 
                  following format:

                   alignment	tree_id	 group	rank	au_test
                   ...         ...      ...    ...     ...
""",
                                     epilog="")
    parser.add_argument('filenames',
                        nargs  = "*",
                        help='Filenames')
    parser.add_argument('-r','--root_group',
                        metavar="",
                        type= str,
                        required=True,
                        help='File with list of outgroups')
    parser.add_argument('-s', '--suffix',
                        metavar = "",
                        type    = str,
                        default = "_rooted_groups.tsv",
                        help    = '[Optional] suffix [Default = _rooted_groups.tsv]')                    
    args = parser.parse_args()
    return args

def main():
    args = getOpts()
    outgroups = []
    with open(args.root_group, 'r') as f:
        for i in f.readlines():
            outgroups.append(i.strip())

    file_myrows = {}

    for filename in args.filenames:
        myrows = []
        with open(filename, 'r') as f:
            reader = csv.reader(f, delimiter = "\t")
            for row in reader:
                myrows.append( row )

        file_myrows[filename] = myrows

    
    transformed = {}

    for file,myrows in file_myrows.items():

        new_rows = []
        for row in myrows:

            tree_str = row[2]

            if tree_str == 'group':
                continue

            if transformed.__contains__(tree_str):
                row[2] = transformed[tree_str]
                new_rows.append(row)
                continue
            
            from_tree = dendropy.Tree.get_from_string( 
                                        src     = tree_str, 
                                        schema  = 'newick',
                                        rooting = 'default-rooted',
                                        preserve_underscores = True 
                                    )

            root_mrca = from_tree.mrca(taxon_labels = outgroups)
            from_tree.reroot_at_edge(root_mrca.edge)
            to_tree_str = (from_tree
                                .as_string(schema = 'newick')
                                .strip()
                                .replace("[&R] ", "")
                                .replace("'", "")
                            )
                            
            row[2] = to_tree_str

            new_rows.append(row)
            transformed[tree_str] = to_tree_str

        ggi_rooted = [['alignment', 'tree_id', 'group', 'rank', 'au_test']] + new_rows

        with open(file + args.suffix, 'w') as f:
            writer = csv.writer(f, delimiter = "\t")
            writer.writerows(ggi_rooted)
    
if __name__ == "__main__":
    main()
