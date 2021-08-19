
# import re
import os
import sys
import csv
import glob
import copy
import itertools
import collections
import statistics as stats
from multiprocessing import Pool


import dendropy
import numpy as np
from scipy.stats import chi2


from fishlifetraits.utils import fas_to_dic

class Features:

    def __init__(self,
                reference_tree = None,
                groups_file = None,
                fasta_ext = None,
                tree_ext = None,
                path = ".",
                taxonomyfile = None,
                codon_aware = True,
                suffix = 'stats.tsv',
                threads = 1):
        
        self.gap_chars = ['N', '-', '!', '?']                
        self.fast_ext = fasta_ext
        self.tree_ext  = tree_ext
        self.path = path
        self.codon_aware = codon_aware
        self.taxonomyfile = taxonomyfile


        self.weighted_rf = False

        if reference_tree:
            self._spps_tree = dendropy.Tree.get(
                                    path   = reference_tree, 
                                    schema = 'newick',
                                    preserve_underscores = True 
                                )
        else:
            self._spps_tree = None

        self.groups_file = groups_file
        self.threads = threads
        self.suffix  = suffix

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

    @property
    def _groups(self):

        if not self.groups_file:
            return None

        myrows = []
        with open(self.groups_file, 'r') as f:
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

    def _base_names_glob(self, ext):
        out = []
        glob_files = glob.glob(os.path.join(self.path, "*%s" % ext))
        for i in glob_files:
            out.append( os.path.basename(i).replace(ext, "") )

        return out

    def _readmetadata(self):

        trees = self._base_names_glob(self.tree_ext)
        alns  = self._base_names_glob(self.fast_ext)

        base_count = collections.Counter(  trees + alns )
        pairs      = [k for k,v in base_count.items() if v == 2 ]

        if not pairs:
            sys.stderr.write("\nNo alignment-tree name coupling under given file extensions\n\n")
            sys.stderr.write("  alignment extension : *%s\n" % self.fast_ext)
            sys.stderr.write("  tree extension      : *%s\n" % self.tree_ext)
            sys.stderr.write("\nat '%s' directory\n\n" % self.path)
            sys.stderr.flush()
            exit()

        myrows = []
        for p in pairs:
            aln  = os.path.join(self.path, p + self.fast_ext)
            tree = os.path.join(self.path, p + self.tree_ext)
            myrows.append( [aln, tree] )

        return myrows

    def _identity_perc(self, seq1, seq2, seq_len):

        out = 0
        for i in range(0, seq_len):
            a = seq1[i]
            b = seq2[i]

            if a in self.gap_chars and a != 'N':
                continue

            if b in self.gap_chars and b != 'N':
                continue

            if a == b:
                out += 1

        return out*100/seq_len

    def _PI_perc(self, aln, seq_len):
        """
        # Pairwise Identity percentage

        * returns mean and standar deviation, whole table
        * it doesn't consider gap character
        * it considers N character
        """
        pi_list = []
        headers_list = []

        for h1,h2 in itertools.combinations(aln, 2):
            pi_list.append(
                self._identity_perc( aln[h1], aln[h2], seq_len)
            )

            headers_list.append(
                (
                    h1.replace(">", ""),
                    h2.replace(">", ""),
                )
            )

        return ( round( stats.mean(pi_list) , 6 ),
                 round( stats.stdev(pi_list), 6 ),
                 list(zip(headers_list, pi_list)) )

    def _Stuart_symmetry(self, dissM):
        """
        Stuart (1955)
        for marginal symmetry
        """
        # dissM = np.array([[1,0,0,0],
        #                   [0,2,0,0],
        #                   [0,0,3,0],
        #                   [0,0,0,4]])

        ut = np.zeros((3,))
        for i in range(3):
            ut[i] = np.sum(dissM[i,:]) - np.sum(dissM[:,i])

        u = ut.reshape((-1, 1))

        # variance-covariance matrix of marg res
        V = np.zeros((3,3))
        for i in range(3):
            for j in range(3):
                if i == j:
                    V[i,j] = np.sum(dissM[i,:]) + np.sum(dissM[:,i]) - 2 * dissM[i,i]

                else:
                    V[i,j] = -(dissM[i,j] + dissM[j,i])

        # test matrix singularity
        if np.linalg.cond(V) < 1/np.finfo(V.dtype).eps:

            Vi = np.linalg.inv(V)

            Ss   = (ut.dot(Vi)).dot(u).item()
            pval = 1 - chi2.cdf( Ss, 3 ) # 3 -> m - 1 
            return (Ss, round(pval, 6) )

        else:
            return None

    def _Internal_symmetry(self, Sb, Ss, Dfb):

        if Sb and Ss and Dfb > 3:
            Si =  Sb - Ss
            pval = 1 - chi2.cdf( Si, Dfb - 3 ) # f - m + 1
            return round( pval, 6 )

        else:
            return None

    def dissMat(self, str1, str2, aa = False):
        """
        {A, T, C, G} dissimilarity matrix
        """
        if aa:
            bases = np.array([
                'A', 'C', 'D', 'E', 
                'F', 'G', 'H', 'I', 
                'K', 'L', 'M', 'N', 
                'P', 'Q', 'R', 'S', 
                'T', 'V', 'W', 'Y'
                ]).reshape((1, -1))
            
        else:
            bases = np.array(['A', 'T', 'C', 'G']).reshape((1, -1))

        x = np.array(list(str1)).reshape((-1, 1))
        y = np.array(list(str2)).reshape((-1, 1))

        bases_x = (x == bases).astype(int)
        bases_y = (y == bases).astype(int)

        return np.dot(bases_y.T, bases_x)

    def _Bowker_symmetry(self, all_pairs, aln, aa = False):
        """
        * Bowker (1948) 
        """
        # max divergence pair
        all_diss = []

        for tpair in all_pairs:

            str1 = aln[ ">" + tpair[0]]
            str2 = aln[ ">" + tpair[1]]
            mym  = self.dissMat(str1, str2, aa = aa)
            tmp_sum = np.sum(mym)
            if not tmp_sum:
                continue
            tmp_diss = (tmp_sum - np.sum(np.diagonal(mym)))/tmp_sum

            all_diss.append((tpair, tmp_diss))

        pair,_ = sorted(all_diss, key = lambda l: l[1], reverse=True)[0]

        str1 = aln[ ">" + pair[0]]
        str2 = aln[ ">" + pair[1]]

        dissM = self.dissMat(str1, str2, aa = aa)

        D = dissM + dissM.T
        N = np.power(dissM - dissM.T, 2) # diag allways zero

        lt = np.tril(
            np.true_divide( N, D, where = (N!=0) | (D!=0) )
        )

        Sb = np.sum(lt)
        # degrees of freedom
        dfb = np.count_nonzero(lt)

        return dissM, Sb, dfb

    def _symmetries(self, all_pairs, aln, aa = False):
        """
        Assessing Stationarity, Homogeneity and Reversevility 
        assumptions

        Symmetry tests based on:

        * Bowker (1948) 
        * Stuart (1955) 
        * Ababneh et al. (2006) 
        @ https://doi.org/10.1093/bioinformatics/btl064
        
        Code based on:

        * Naser-Khdour et al. (2019)
        @ https://doi.org/10.1093/gbe/evz193
        """
        # aa = True
        # all_pairs = [i[0] for i in pi_table]

        dissM, Sb, dfb = self._Bowker_symmetry(all_pairs, aln, aa = aa)

        if not dfb:
            return (None, None, None)

        SBpvalue = round( 1 - chi2.cdf( Sb, dfb ), 6 )

        Ss_SSpvalue = self._Stuart_symmetry(dissM)

        if not Ss_SSpvalue:
            return (SBpvalue, None, None)

        Ss,SSpvalue = Ss_SSpvalue

        SIpvalue = self._Internal_symmetry(Sb, Ss, dfb)

        if not SIpvalue:
            return (SBpvalue, SSpvalue, None)

        return (SBpvalue, SSpvalue, SIpvalue)

    def _LB_score(self, patristic):
        """
        * Equation based on Struck (2014) @ https://doi.org/10.4137/EBO.S14239
        """
        all_pairs = itertools.combinations(patristic.keys(), 2)
        all_branches = []
        for h1,h2 in all_pairs:
            all_branches.append(  patristic[h1][h2] )

        cross_tax_mean = stats.mean(all_branches)

        all_LB_scores = []

        for k,v in patristic.items():
            tax_mean = stats.mean( [v2 for k2,v2 in v.items() if k2 != k] )
            tmp_lb_score = ( (tax_mean/cross_tax_mean) - 1 ) * 100
            all_LB_scores.append( tmp_lb_score )

        return round( stats.stdev(all_LB_scores), 6 )

    def _RCV(self, clean_rows, nheaders, seq_len):
        """
        # Relative Composition Variability

        Do not consider {'N', '-', '!', '?'} (i.e., gap characters) and\\
        any character is independently counted, even\\
        ambiguous ones. Better implementations
        migth be needed
        """
        relative_comp = {}
        for row in clean_rows:
            for k,v in row.items():
                if not relative_comp.__contains__(k):
                    relative_comp[k] = [v]
                else:
                    relative_comp[k] += [v]

        base_mean = { k:stats.mean(v) for k,v in relative_comp.items() }
        row_rv    = []

        for row in clean_rows:
            row_sum = 0
            for base,its_mean in base_mean.items():
                if row.__contains__(base):
                    row_sum += abs(  row[base] - its_mean )

            row_rv.append(row_sum)

        return sum(row_rv)/(nheaders * seq_len)

    def _stat_sites_horizontal(self, aln):

        gc_taxa    = []
        gap_taxa   = []
        seq_len    = len(next(iter(aln.values())))
        clean_rows = []

        for row in aln.values():

            data_sum = collections.Counter(row)
            # parallel_sum =  copy.deepcopy(data_sum)
            row_gap  = 0

            for gc in self.gap_chars: 
                if data_sum.__contains__(gc):
                    if gc != "N":
                        row_gap += data_sum[gc]
                        # del parallel_sum[gc]

                    del data_sum[gc]

            gap_taxa.append( row_gap*100/seq_len )

            row_gc = 0
            if data_sum.__contains__('G'):
                row_gc += data_sum['G']

            if data_sum.__contains__('C'):
                row_gc += data_sum['C']

            new_seq_len = sum([i for i in data_sum.values()])
            gc_taxa.append(row_gc*100/new_seq_len)

            clean_rows.append(data_sum)
            # clean_rows.append(parallel_sum)

        return ( round( stats.mean(gc_taxa)     , 6) ,
                 round( stats.variance(gc_taxa) , 6) ,
                 round( stats.mean(gap_taxa)    , 6) ,
                 round( stats.variance(gap_taxa), 6) ,
                 clean_rows )

    def _split_aln(self, aln, seq_len):

        codon1 = {}
        codon2 = {}
        codon3 = {}

        for pos in range(0, seq_len, 3):

            for k,v in aln.items():

                if not codon1.__contains__(k):
                    codon1[k] = v[pos]

                else:
                    codon1[k] += v[pos]


                if not codon2.__contains__(k):
                    codon2[k] = v[pos + 1]
                else:
                    codon2[k] += v[pos + 1]


                if not codon3.__contains__(k):
                    codon3[k] = v[pos + 2]
                else:
                    codon3[k] += v[pos + 2]

        return codon1, codon2, codon3

    def _stat_sites_vertical(self, aln):
        """
        # Stats for alignments

        Returning in order:

            * Phylogenetic informative sites
            * Variable sites
            * Proportion of gaps
            * Proportion of non-gaps characters
            * Length of the alignment
            * Number of sequences
            * sites with no gap

        """
        # file = "/Users/ulises/Desktop/GOL/software/GGpy/demo/24_ENSG00000000005_codon_aln.fasta"
        # aln = fas_to_dic(file)

        nheaders = len(aln)
        seq_len  = len(next(iter(aln.values())))
        
        pis_s  = 0
        n_gaps = 0
        var_s  = 0
        site_w_gaps = []

        for pos in range(seq_len):
            has_gaps = False

            column = []
            for v in aln.values():
                column.append( v[pos])

            data_sum = collections.Counter(column)
            
            for gc in self.gap_chars:
                if data_sum.__contains__(gc):

                    if gc != "N":
                        has_gaps = True
                        n_gaps += data_sum[gc]

                    del data_sum[gc]

            site_w_gaps.append(has_gaps)

            uniq_char = len(data_sum)

            if not uniq_char:
                continue

            if uniq_char > 1:
                var_s += 1
                tmp_pi = [i for i in data_sum.values() if i > 1]

                if len(tmp_pi) > 1:
                    pis_s += 1

        
        AlnLen_nogaps = seq_len - sum(site_w_gaps) 
        AREA = nheaders * seq_len
        gap_prop = round(n_gaps/AREA, 6)

        return ( pis_s, 
                 var_s, 
                 gap_prop, 
                 1 - gap_prop, 
                 seq_len, 
                 nheaders, 
                 AlnLen_nogaps)

    def _DVMC(self, tree):
        """
        Degree of violation of molecular clock (DVMC)
        estimated from a mid-point rooted tree.
        DVMC according to Liu et al. 2017. 
        DOI: https://doi.org/10.1073/pnas.1616744114
        """
        tip_root_dists = []
        for nd in tree.preorder_node_iter():
            if nd.is_leaf():
                tip_root_dists.append( nd.distance_from_root() )

        return stats.stdev(tip_root_dists)

    def _coeffVar_rtl(self, tree):
        """ 
        Rate variation among lineages:
        Coefficient of variation of branch lengths
        after mid-point rooting according 
        Vankan et al. 2021
        DOI: https://doi.org/10.1093/sysbio/syab051
        """
        all_lengths  = [ ed.length for ed in tree.postorder_edge_iter() ]
        rootTip_lengths = list( filter(None, all_lengths) )
        return stats.stdev(rootTip_lengths)/stats.mean(rootTip_lengths)

    def _branch_len_stats(self, tree_file):
        """
        All about lengths
        
        * total tree_len
        * treeness
        * internal len_mean
        * internal len_var
        * terminal len_mean
        * terminal len_var
        * patristic distances

        """

        int_branches = []
        ter_branches = []
        node_labels  = []
        tree = dendropy.Tree.get(
                    path   = tree_file, 
                    schema = 'newick',
                    preserve_underscores = True
                )

        for ed in tree.postorder_edge_iter():
            if ed.is_internal():
                int_branches.append(ed.length)
                node_labels.append(ed._head_node._label)

            else:
                ter_branches.append(ed.length)
        
        int_branches_fil = list( filter(None, int_branches) )
        ter_branches_fil = list( filter(None, ter_branches) )
        node_labels_fil  = list( filter(None, node_labels)  )

        if node_labels_fil:
            avg_node = stats.mean([float(i) for i in node_labels_fil])

        else:
            avg_node = 0

        total_treelen = sum( int_branches_fil + ter_branches_fil )
        treeness      = sum(int_branches_fil)/total_treelen
        patristic_d   = tree.phylogenetic_distance_matrix().as_data_table()._data

        # mid-point rooting
        tree.reroot_at_midpoint(update_bipartitions = True)

        coeffVar_rtl = self._coeffVar_rtl(tree)
        # clockness = self._DVMC(tree)

        return ( round( total_treelen                   , 6 ) ,
                 round( treeness                        , 6 ) ,
                 round( stats.mean(int_branches_fil)    , 6 ) ,
                 round( stats.variance(int_branches_fil), 6 ) ,
                 round( stats.mean(ter_branches_fil)    , 6 ) ,
                 round( stats.variance(ter_branches_fil), 6 ) ,
                 round( avg_node                        , 6 ) ,
                 round( coeffVar_rtl                    , 6 ) ,
                 patristic_d )

    def _coeff_deter(self, values):

        x = [ i[0] for i in values ]
        y = [ i[1] for i in values ]

        x_mean = sum(x)/len(x)
        y_mean = sum(y)/len(y)

        n = len(x)
        num  = 0
        deno = 0
        for i in range(n):
            num += ( x[i] - x_mean ) * (y[i] - y_mean )
            deno += ( x[i] - x_mean ) ** 2
        # slope
        m = num/deno
        # coeff
        b = y_mean - (m*x_mean)

    def _taxonomy_sampling(self, aln):
        
        aln_taxa = set([i.replace(">", "") for i in list(aln)])
        # len_aln_taxa = len(aln_taxa)

        present_groups = 0
        for v in self._taxa.values():

            if aln_taxa & set(v):
                present_groups += 1

        return round(present_groups/len(self._taxa), 6)

    def _slope(self, values):

        x = [ i[0] for i in values ]
        y = [ i[1] for i in values ]

        x_mean = sum(x)/len(x)
        y_mean = sum(y)/len(y)

        n = len(x)
        num  = 0
        deno = 0
        for i in range(n):
            num += ( x[i] - x_mean ) * (y[i] - y_mean )
            deno += ( x[i] - x_mean ) ** 2
        # slope
        m = num/deno
        # # coeff
        # b = y_mean - (m*x_mean)
        return m

    def _saturation(self, pi_table, patristic):
        """
        sensu Herve Philippe & cola.
        at 10.1371/journal.pbio.1000602
        """
        values = [] # x = substitutions, y = branch distance
        for pair, identity in pi_table:
            h1,h2 = pair
            values.append( ( 1 - identity/100, patristic[h1][h2]) )

        return self._slope(values)

    def uRF(self, tree1, tree2):
        """
        # Robison-Foulds distances

        it might be more efficient
        by not converting dendropy classes
        into strings, but it might need to
        share same TaxonNamespace.

        This method let to compare
        any couple of tree with different
        TaxonNamespace
        """
        tns = dendropy.TaxonNamespace()

        a = dendropy.Tree.get_from_string(
                        tree1.as_string(schema = 'newick'), 
                        schema = 'newick',
                        taxon_namespace=tns)

        b = dendropy.Tree.get_from_string(
                        tree2.as_string(schema = 'newick'), 
                        schema = 'newick',
                        taxon_namespace=tns)

        if not self.weighted_rf:
            return (dendropy
                        .calculate
                        .treecompare
                        .symmetric_difference(a,b))

        else:
            return (dendropy
                        .calculate
                        .treecompare
                        .weighted_robinson_foulds_distance(a,b))

    def _estimate_rf(self, _gt_tree_f):

        cp_spps_tree = copy.deepcopy(self._spps_tree)
        _gt_tree = dendropy.Tree.get(
                        path   = _gt_tree_f, 
                        schema = 'newick',
                        preserve_underscores = True
                    )
        gt_taxa = [i.taxon.label for i in  _gt_tree.leaf_node_iter()]
        cp_spps_tree.retain_taxa_with_labels( gt_taxa )

        return self.uRF(cp_spps_tree, _gt_tree) 

    def _allocate_group(self, stdout,  aln_file):
        
        aln_file_b = os.path.basename(aln_file)
        out = []
        matched = 0
        for k,v in self._groups.items():
            if aln_file_b in v:
                
                out.append( stdout + [k] )
                matched += 1

        if not matched:
            # (Extend?, table)
            out = (False, stdout + [None])
        else:
            out = (True, out)
            
        return out

    def _add_label(self, stdout, tree_file, aln_file):
        
        if self._spps_tree:
            stdout += [ self._estimate_rf(tree_file) ]

        else:
            stdout = self._allocate_group(stdout, aln_file) 

        return stdout

    def stat_iterator(self, aln_tree_files):

        aln_file,tree_file = aln_tree_files
        # aln_file,tree_file = seq_tree_files[0]
        # aln_file = "/Users/ulises/Desktop/GOL/data/alldatasets/nt_aln/internally_trimmed/malns_36_mseqs_27/round2/no_lavaretus/protein/round1/E0807.aaseqs.fasta"
        aln_base = os.path.basename(aln_file)
        tree_base = os.path.basename(tree_file)

        sys.stdout.write("Processing stats for: %s\n" % aln_base)
        sys.stdout.write("Processing stats for: %s\n" % tree_base)
        sys.stdout.flush()

        aln  = fas_to_dic(aln_file)
        
        (pis          ,
         var_s        ,
         gap_prop     ,
         nogap_prop   ,
         seq_len      ,
         nheaders     ,
         seq_len_nogap) = self._stat_sites_vertical(aln)

        (gc_mean   ,
         gc_var    ,
         gap_mean  , 
         gap_var   , 
         clean_rows) = self._stat_sites_horizontal(aln)

        (pi_mean , 
         pi_std  , 
         pi_table) = self._PI_perc(aln, seq_len)

        (total_tree_len,
         treeness      ,
         inter_len_mean,
         inter_len_var ,
         ter_len_mean  ,
         ter_len_var   ,
         avg_node      ,
         coeffVar_len  ,
         patristic     ) = self._branch_len_stats(tree_file)
 
        rcv            = round(self._RCV(clean_rows, nheaders, seq_len), 6)
        treeness_o_rcv = round(rcv/treeness, 6)
        saturation     = round(self._saturation(pi_table, patristic), 6)

        all_pairs = [i[0] for i in pi_table]

        (SymPval,
         MarPval,
         IntPval) = self._symmetries(all_pairs, aln)

        LB_std = self._LB_score(patristic)

        stdout = [ 
            aln_base      , 
            nheaders      , pis           , var_s         ,
            seq_len       , seq_len_nogap , gap_prop      , 
            nogap_prop    , gc_mean       , gc_var        ,
            gap_mean      , gap_var       , pi_mean       ,
            pi_std        , total_tree_len, treeness      ,
            inter_len_mean, inter_len_var , ter_len_mean  ,
            ter_len_var   , avg_node      , coeffVar_len  ,
            rcv           , treeness_o_rcv, saturation    , 
            SymPval       , MarPval       , IntPval       , 
            LB_std
        ]

        if self._taxa:
            stdout.append( self._taxonomy_sampling(aln) )

        if self.codon_aware:
            codon1, codon2, codon3 = self._split_aln(aln, seq_len)

            (gc_mean_pos1 ,
             gc_var_pos1  ,
             gap_mean_pos1, 
             gap_var_pos1 , 
             _            ) = self._stat_sites_horizontal(codon1)
            (gc_mean_pos2 ,
             gc_var_pos2  ,
             gap_mean_pos2, 
             gap_var_pos2 , 
             _            ) = self._stat_sites_horizontal(codon2)
            (gc_mean_pos3 ,
             gc_var_pos3  ,
             gap_mean_pos3, 
             gap_var_pos3 , 
             _            ) = self._stat_sites_horizontal(codon3)

            stdout.extend([
                gc_mean_pos1, gc_var_pos1, gap_mean_pos1, gap_var_pos1,
                gc_mean_pos2, gc_var_pos2, gap_mean_pos2, gap_var_pos2,
                gc_mean_pos3, gc_var_pos3, gap_mean_pos3, gap_var_pos3 
            ])

        if self._spps_tree or self._groups:
            stdout = self._add_label(stdout, tree_file, aln_file)

        return stdout

    def write_table(self, table):

        colnames = [
            "aln_base"      ,
            "nheaders"      , "pis"           , "vars"          , 
            "seq_len"       , "seq_len_nogap" , "gap_prop"      , 
            "nogap_prop"    , "gc_mean"       , "gc_var"        ,
            "gap_mean"      , "gap_var"       , "pi_mean"       ,
            "pi_std"        , "total_tree_len", "treeness"      ,
            "inter_len_mean", "inter_len_var" , "ter_len_mean"  ,
            "ter_len_var"   , "supp_mean"     , "coeffVar_len"  ,
            "rcv"           , "treeness_o_rcv", "saturation"    , 
            "SymPval"       , "MarPval"       , "IntPval"       ,
            "LB_std"
        ]

        if self._taxa:
            colnames.append("tax_prop")

        if self.codon_aware:
            colnames.extend([
                "gc_mean_pos1", "gc_var_pos1", "gap_mean_pos1", "gap_var_pos1",
                "gc_mean_pos2", "gc_var_pos2", "gap_mean_pos2", "gap_var_pos2",
                "gc_mean_pos3", "gc_var_pos3", "gap_mean_pos3", "gap_var_pos3" 
            ])

        if self._spps_tree or self._groups:

            if self._spps_tree:
                colnames.append("RF")

            else:
                colnames.append("Group")

        out = [colnames] + table

        out_file = "features_" + self.suffix

        if len(out) > 1:
            with open( out_file , 'w' ) as f:
                writer = csv.writer(f, delimiter = "\t")
                writer.writerows(out)

            sys.stdout.write("\n\nReport of features written at %s\n" % out_file)
            sys.stdout.flush()            

    def write_stats(self):

        self._taxa
        self._groups
        
        seq_tree_files = self._readmetadata()

        with Pool(processes = self.threads) as p:

            preout = []
            for seq_tree in seq_tree_files:
                result = p.map_async(self.stat_iterator, (seq_tree,))
                preout.append(result)

            table  = []
            for pr in preout:
                gotit = pr.get()[0]

                if gotit:
                    if len(gotit) == 2:
                        extend,out = gotit
                        if extend:
                            table.extend(out)
                        else:
                            table.append(out)
                    else:
                        table.append(gotit)
                            
            self.write_table(table)

# taxonomyfile = "/Users/ulises/Desktop/GOL/software/GGpy/demo/ingroup_taxa_file.csv"
# # spps_tree = "/Users/ulises/Desktop/GOL/software/GGpy/demo/after_qc_1024exons.tree"
# groups_file = "/Users/ulises/Desktop/GOL/data/alldatasets/nt_aln/internally_trimmed/malns_36_mseqs_27/round2/no_lavaretus/hypothesis_248exons_p_zero75.csv" # change

# self = Features(
#     taxonomyfile=taxonomyfile,
#     path="/Users/ulises/Desktop/GOL/data/alldatasets/nt_aln/internally_trimmed/malns_36_mseqs_27/round2/no_lavaretus/McL", # change
#     fasta_ext=".r2_para_no_lavaretus_TBL_tlike_aln",
#     tree_ext=".r2_para_no_lavaretus_TBL_tlike_aln.nex.treefile",

#     reference_tree=None,

#     groups_file = groups_file,

#     codon_aware=True,
#     threads= 5,
#     suffix="p_zero75.tsv", # change
#     # write=True
#     )

# self.write_stats()