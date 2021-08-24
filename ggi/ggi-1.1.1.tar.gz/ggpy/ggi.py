
import os
import re
import sys
import csv
import ggpy
import pickle
import dendropy


from multiprocessing import Pool
from ggpy.utils import fas_to_dic, remove_files
from ggpy.wrappers import Raxml, RAXML, Consel


class GGI(Raxml, Consel):

    def __init__(self, 
                sequences = None, 
                taxonomyfile = None,
                topologies = None,
                are_extended = False,
                rooted = False,
                codon_partition = True, 
                threads = 1,

                evomodel = 'GTRGAMMA',
                iterations = 10,

                write_extended = False,
                suffix = 'ggi.tsv',

                raxml_exe = RAXML, #unmutable vars

                ) -> None:


        self.sequences = sequences
        self.taxonomyfile = taxonomyfile

        self.rooted = rooted

        self.topologies = topologies
        self.are_extended = are_extended
        self.write_extended = write_extended


        self.suffix = suffix
        self.threads = threads


        ## --- shared variables --- #
        self.codon_partition = codon_partition
        self.evomodel = evomodel
        self.raxml_exe = raxml_exe
        self.iterations = iterations

        self.seqmt_exe   = "seqmt"
        self.makermt_exe = "makermt"
        self.consel_exe  = "consel"
        self.catpv_exe   = "catpv"
        ## --- shared variables --- #

        self.translation = {}
        self.allheaders = set()
        self.final_out = "out_" + self.suffix
        self.trans_out = "translation_" + self.suffix

        self.unable_to_prune_f = "unable_to_prune_" + self.suffix
        self.unable_to_run_f = "unable_to_run_" + self.suffix

        self.hiddenfile = ".treebase_" + self.suffix

    
    @property
    def _taxa(self):

        if not self.taxonomyfile:
            return None

        myrows = []
        with open(self.taxonomyfile, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                myrows.append(row)
                
        df = {}
        for i in myrows:
            spps  = i[0]
            group = i[1]
            if not df.__contains__(group):
                df[group] = [spps]
            else:
                df[group] += [spps]

        return df

    def _internal_hypothesis(self, df, ext_str):

        ngroups = len(df)

        file_basename = "g_%s_%s" % ( ngroups, ext_str         )
        file_path     = os.path.join( ggpy.__path__[0], 'data' )
        filename      = os.path.join( file_path, file_basename )

        fmt_args_exte = {}
        fmt_args_cons = {}

        g_count  = 1
        for k,v in df.items():

            quoted_spps = ",".join(v)
            if len(v) > 1:
                quoted_spps = "(%s)" % quoted_spps

            fmt_args_exte[ "g_%s" % g_count ] = quoted_spps
            fmt_args_cons[ "g_%s" % g_count ] = k
            g_count += 1

        with open(filename, 'r') as f:
            tmp_str = f.read()

        filled_spps_str  = tmp_str.format(**fmt_args_exte).split()
        filled_group_str = tmp_str.format(**fmt_args_cons).split()

        self.translation = dict(zip(filled_spps_str, filled_group_str))

        hypothesis = {}
        count = 1
        for spps,group in zip(filled_spps_str, filled_group_str):
            hypothesis[count] = {'group': group, 'extended': spps}
            count += 1

        self.translation = hypothesis

    def _taxa_from_str(self, tmp_tree):

        tmp_tree = dendropy.Tree.get_from_string(  
                                    src = tmp_tree, 
                                    schema = 'newick',
                                    preserve_underscores = True
                                )

        return [ i.taxon.label for i in tmp_tree.leaf_node_iter() ]

    def _external_hypothesis(self, df):

        groups = set(df)
        hypothesis = {}

        with open(self.topologies, 'r') as f:

            count = 1
            for i in f.readlines():

                tmp_hypothesis = i.strip()

                if not tmp_hypothesis:
                    continue

                str_taxa = self._taxa_from_str(tmp_hypothesis)

                new_groups = set(str_taxa) - groups

                if new_groups:
                    sys.stderr.write( "\n %s groups do not match with the taxonomy file at: '%s'\n" % (new_groups, tmp_hypothesis) )
                    sys.stderr.flush()
                    continue
      
                extended_str = tmp_hypothesis
                for k,v in df.items():

                    quoted_spps = ",".join(v)
                    if len(v) > 1:
                        quoted_spps = "(%s)" % quoted_spps

                    extended_str = extended_str.replace(k, quoted_spps)

                hypothesis[count] = {'group':tmp_hypothesis, 'extended': extended_str}
                count += 1

        if not hypothesis:
            # no hypothesis
            # to test
            self.close_files()
            sys.exit(1)

        self.translation = hypothesis

    def __save_trees__(self, obj = None):

        with open( self.hiddenfile , 'wb') as f:
            pickle.dump(obj, f, pickle.DEFAULT_PROTOCOL)

    def __load_trees__(self):

        with open( self.hiddenfile, 'rb') as f:
            return pickle.load(f)

    def _set_extended_hypothesis(self):

        if self.topologies and self.are_extended:

            to_trs = {}
            with open(self.topologies, 'r') as f:

                count = 1 
                for i in f.readlines():
                    tmp_hypothesis = i.strip()
                    to_trs[count] = {'group': None, 'extended': tmp_hypothesis}
                    count += 1

            self.translation = to_trs

        else:

            ngroups = len(self._taxa)

            if not self.topologies:

                ext_str = ""

                if ngroups == 3:
                    self.rooted = True

                if self.rooted:
                    if ngroups > 8:
                        sys.stderr.write("\nTest all possible rooted trees for more \n")
                        sys.stderr.write("than 8 groups is not currently available\n")
                        sys.stderr.flush()
                        self.close_files()
                        sys.exit(1)

                    ext_str += "rooted.tree"
                else:

                    if ngroups > 9:
                        sys.stderr.write("\nTest all possible unrooted trees for more \n")
                        sys.stderr.write("than 9 groups is not currently available\n")
                        sys.stderr.flush()
                        self.close_files()
                        sys.exit(1)

                    ext_str += "unrooted.tree"

                self._internal_hypothesis(self._taxa, ext_str)
            else:

                self._external_hypothesis(self._taxa)

        if self.write_extended:

            outname = "extended_hypothesis_" + self.suffix
            with open(outname, "w") as f:
                for v in self.translation.values():
                    f.write("%s\t%s\n" % (v['group'], v['extended']))

            sys.stderr.write("\nExtended hypothesis written at '%s'\n" % outname)
            sys.stderr.flush()
            self.close_files()
            sys.exit(0)

        # attempt to reduce mem usage
        self.__save_trees__(self.translation)
        self.translation = {}
        
    def _aln_in_hypothesis(self, aln_taxa, tmp_tree):
        """
        # hypothesis taxa includes all aln taxa?
        """
        # str_hypothesis = list(self.translation)[0]
        # hypo_taxa = set(self._taxa_from_str(str_hypothesis))

        hypo_taxa = set( [i.taxon.label for i in tmp_tree.leaf_node_iter()] )
        aln_taxa  = set( aln_taxa )

        new_for_hypo = aln_taxa - hypo_taxa

        return (False, new_for_hypo) if new_for_hypo else (True, None)

    def prunning(self, file):
        # file = self.sequences[0]
        aln_base = os.path.basename(file)
        aln      = fas_to_dic(file)

        translation  = self.__load_trees__()
        aln_metadata = {}

        for k,v in translation.items():
            # k,v = tuple(self.translation.items())[0]

            tmp_tree = (dendropy
                            .Tree
                            .get_from_string( 
                                src = v['extended'], 
                                schema = 'newick',
                                preserve_underscores = True) )

            aln_taxa  = [i.replace(">", "") for i in list(aln)]
            is_subset,which_taxa = self._aln_in_hypothesis(aln_taxa, tmp_tree)

            if not is_subset:
                tmp_rows = [ [aln_base, wt, v['id']] for wt in which_taxa ]
                with open(self.unable_to_prune_f, 'a') as f:
                    writer = csv.writer(f, delimiter = "\t")
                    writer.writerows(tmp_rows)

                continue

            tmp_tree.retain_taxa_with_labels( aln_taxa )
            pruned = tmp_tree.as_string(schema='newick')

            aln_metadata[k] = {
                    'group' : v['group'], 
                    'pruned': pruned , 
                    'aln'   : file
                }

        del translation
        return aln_metadata

    def constraints(self, pr_message):
        """
        What it bassically runs:

        raxmlHPC-SSE3_{OS}_64bit                             \\
            -p 12345                                         \\
            -g {fasta}_{id}_{suffix}_constr.tree             \\
            -q {fasta}_{id}_{suffix}.partitions #if selected \\
            -m {model}                                       \\
            -s {fasta}_{id}_{suffix}                         \\
            -n base({fasta}_{id}_{suffix}) + ".tree"         \\
            -T 1                                             \\
            --silent                                         \\
            -N {iterations}
        """
        if not pr_message:
            return None

        return self.__iter_raxml__(pr_message, 
                                   self.unable_to_run_f, 
                                   self.suffix)
        
    def site_likelihoods(self, cons_message, aln_f):
        """
        constraints are sent 
        ordered in functions of keys\\

        keys are ordered in functions
        of row lines in the
        translation file
        """
        # cons_message, aln_f = cons_message, file 
        if not cons_message:
            return None

        # aln_f = next(iter(cons_message.values()))['aln']
        whole_constrs_f = aln_f + "_AllCons_" + self.suffix
        
        # join constrains
        cons_trees = []
        # order matters
        for i in range(len(cons_message)):
            v = cons_message[ i + 1 ]
            with open( v['constrained'], 'r' ) as c:
                cons_trees.append( c.read() )

        with open( whole_constrs_f, "w") as f:
            f.writelines(cons_trees)

        sll_f = self._site_likehood(
                        (aln_f, whole_constrs_f),
                        self.suffix,
                        self.unable_to_run_f
                )

        if sll_f:
            return (sll_f, cons_message)
            # return (sll_f, sll_meta)
        else:
            return None

    def keep_rank1_tree(self, au_table, sll_meta):
        to_rm = []
        s_item = 0

        for rank, item, _ in au_table:
            item_int = int(item)

            if rank != '1':
                to_rm.append(

                    sll_meta[item_int]['constrained']
                )

            else:
                s_item += item_int
                # rank1 += sll_meta[item_int]['constrained']

        rank1 = sll_meta[s_item]['constrained']
        # seq = sll_meta[s_item]['aln']
        # self.add_bootstrap(
        #     seq = seq, 
        #     selected_tree = rank1,
        #     suffix = self.suffix
        # )
        new_name = re.sub(self.suffix, self.suffix + "_rank1", rank1)

        os.rename(rank1, new_name)
        remove_files(to_rm)

    def au_tests(self, sll_message, seq_basename):

        if not sll_message:
            return None

        sll_f,sll_meta = sll_message

        au_table = self._consel_pipe(seq_basename, sll_f, self.unable_to_run_f)

        if not au_table:
            return None

        self.keep_rank1_tree(au_table, sll_meta)

        out_cols = []
        for row in au_table:
            item    = int(row[1])

            rank    = row[0]
            au_test = row[2]
            tree_id = item
            group   = sll_meta[item]['group']

            out_cols.append([
                    seq_basename, tree_id,
                    group, rank, au_test
                ])

        return out_cols

    def ggi_iterator(self, file):
        # file = self.sequences[0]
        seq_basename = os.path.basename(file)

        sys.stdout.write("Processing: '%s' \n" % seq_basename)
        sys.stdout.flush()

        pr_message   = self.prunning(file)
        cons_message = self.constraints(pr_message)
        sll_message  = self.site_likelihoods(cons_message, file)
        
        return self.au_tests(sll_message, seq_basename)

    def init_files(self):

        utp_cols = [["alignment", "species", "tree_id"]]
        with open(self.unable_to_prune_f, "w") as f:
            writer = csv.writer(f, delimiter = "\t")
            writer.writerows(utp_cols)

        utr_cols = [["alignment", "where", "tree_id"]]
        with open(self.unable_to_run_f, "w") as f:
            writer = csv.writer(f, delimiter = "\t")
            writer.writerows(utr_cols)

    def close_files(self):
        files_check = [
            self.unable_to_prune_f,
            self.unable_to_run_f
        ]

        to_rm = [self.hiddenfile]

        sys.stdout.write("\n\n")
        sys.stdout.flush()

        for to_c in files_check:
            num_lines = sum( 1 for _ in open(to_c) )
            if num_lines == 1:
                to_rm.append(to_c)
            else:
                sys.stdout.write("'%s' file was written\n" % to_c)
                sys.stdout.flush()
                
        remove_files(to_rm)

    def export_translation(self):
                
        trans_cols = [[ "tree_id", "group", "extended"]]
        translation = self.__load_info__(self.hiddenfile)

        trans_sorted = sorted(translation.items(), key = lambda kv: kv[0])

        for k,v in trans_sorted:
            trans_cols.append([ k, v['group'], v['extended'] ])

        with open(self.trans_out, "w") as f:
            writer = csv.writer(f, delimiter = "\t")
            writer.writerows(trans_cols)

        sys.stdout.write("=> '%s' file was written\n" % self.trans_out)
        sys.stdout.flush()
    
    def main(self):

        self.init_files()

        with Pool(processes= self.threads) as p:

            self._set_extended_hypothesis()

            preout = []
            for fa in self.sequences:
                result  = p.map_async(self.ggi_iterator, (fa,))
                preout.append(result)

            out_cols = [["alignment", "tree_id", "group", "rank", "au_test"]]
            for pr in preout:
                gotit = pr.get()[0]
                if gotit:
                    out_cols.extend(gotit)

            if len(out_cols ) > 1:    
                sys.stdout.write("\n\n")
                sys.stdout.flush()

                with open(self.final_out, "w") as f:
                    writer = csv.writer(f, delimiter = "\t")
                    writer.writerows(out_cols)

                sys.stdout.write("=> '%s' file was written\n" % self.final_out)
                sys.stdout.flush()

                self.export_translation()
                self.close_files()
            else:

                self.close_files()
                sys.exit(1)
                

# tests ----------------------#
# import glob
# sequences = glob.glob("/Users/ulises/Desktop/GOL/software/GGpy/demo/LOC*.fas")
# # sequences = glob.glob("/Users/ulises/Desktop/GOL/software/GGpy/demo/E*.fasta")


# self = GGI(
#     sequences=sequences,
#     # taxonomyfile=None,
#     taxonomyfile="/Users/ulises/Desktop/GOL/software/GGpy/demo/ggi_tax_file.csv",
#     topologies= "/Users/ulises/Desktop/BAL/GGI_flatfishes/tests/all_constraints_hypos.trees",
#     # topologies= "/Users/ulises/Desktop/GOL/software/GGpy/demo/myhypothesis.trees",
#     write_extended= False,
#     # are_extended = False,
#     are_extended = True,
#     codon_partition=False,
#     iterations=1
#     )

# self._set_extended_hypothesis()
# tests ----------------------#

class deepGGI:
    def __init__(self) -> None:
        pass
