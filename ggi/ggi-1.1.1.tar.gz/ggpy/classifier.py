

import csv
import sys
import collections



import shap
import joblib
import xgboost
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.metrics import  accuracy_score, plot_confusion_matrix



# file_comparisons = "/Users/ulises/Desktop/GOL/software/GGpy/demo/tree_id_comparisons.csv"
# features_file = '/Users/ulises/Desktop/BAL/GGI_flatfishes/post_ggi/features_fstats_yongxin.tsv'
# label_file    = '/Users/ulises/Desktop/BAL/GGI_flatfishes/post_ggi/ggi_h1_h3.tsv'
# all_ggi_results = '/Users/ulises/Desktop/BAL/GGI_flatfishes/post_ggi/all_1693_ggi_nt.tsv'
# model_prefix  = 'yongxin_h1_h3'
# threads = 5

# """
# 1,2
# 1,3
# 2,3
# """

class Post_ggi:

    def __init__(self, 
                 feature_file = None,
                 all_ggi_results = None,
                 file_comparisons = None,
                 model_prefix = "post_ggi",
                 cnfx_ncols = 3,
                 threads = 1
                 ) -> None:

        self.feature_file = feature_file
        self.all_ggi_results = all_ggi_results
        self.file_comparisons = file_comparisons

        self.model_prefix = model_prefix
        self.cnf_ncols = cnfx_ncols
        self.threads = threads

        self.drop_columns = [
            'Group', 'aln_base', 
            'SymPval', 'MarPval', 
            'IntPval'
        ]

        # previously tuned hyperparameters
        self.gamma = 0.14210526315789473
        self.learning_rate = 0.03
        self.max_depth = 4
        self.reg_lambda = 0.018
        self.n_estimators = 4200

    @property    
    def ggi_df(self):

        if not self.all_ggi_results:
            return None

        ggi_rows = []
        with open(self.all_ggi_results, 'r') as f:
            reader = csv.reader(f, delimiter = '\t')
            for row in reader:
                ggi_rows.append(row)

        return ggi_rows

    @property
    def tree_id_comp(self):

        if not self.file_comparisons:
            return None

        tree_id_comp = []
        with open(self.file_comparisons, 'r') as f:
            reader = csv.reader(f, delimiter = ',')
            for row in reader:
                tree_id_comp.append(row)

        return tree_id_comp

    @property
    def features(self):
        return pd.read_csv(self.feature_file, sep = '\t')

    def subset_tree_id(self, tree_id_comp1):
        """
        subset tree_id_comp df
        by a tree_id
        """
        if not self.ggi_df:
            return None

        subset_df = []
        for row in self.ggi_df:

            rank = row[3]
            if rank != '1':
                continue

            aln_base = row[0]
            tree_id  = row[1]

            contained = set(tree_id_comp1) & set(tree_id)

            if contained:
                subset_df.append([aln_base, tree_id])

        if not subset_df:
            sys.stderr.write("Tree ids '%s' do not match with\n" % ", ".join(tree_id_comp1))
            sys.stderr.write("'%s' data frame\n" % self.all_ggi_results)
            sys.stderr.flush()
            return None

        return pd.DataFrame(subset_df, columns = ['alignment', 'hypothesis'])
        
    def make_specific_prefix(self, tree_id_comp1):
        return "%s_h%s_h%s" % (self.model_prefix, tree_id_comp1[0], tree_id_comp1[1])

    def shap_plots(self, xgb_clf_no_nor, all_num, new_prefix):

        bee_20_filename = "20best_beeswarm_%s.png" % new_prefix
        bee_all_filename = "all_beeswarm_%s.png" % new_prefix

        explainer   = shap.Explainer(xgb_clf_no_nor, all_num)
        shap_values = explainer(all_num)

        shap.plots.beeswarm(shap_values,
                            max_display = 20,
                            show = False)
        plt.tight_layout(pad=0.05)
        plt.savefig(bee_20_filename, dpi = 330)
        plt.close()

        # explainer   = shap.Explainer(xgb_clf_no_nor, all_num)
        shap_values = explainer(all_num)
        shap.plots.beeswarm(shap_values,
                            max_display = len(all_num.columns),
                            show = False)
        plt.tight_layout(pad=0.05)
        plt.savefig(bee_all_filename, dpi = 330)
        plt.close()

    def create_metdata(self, new_prefix, values):

        metadata_filename = '%s_metadata.tsv' % new_prefix
        columns = [
            'model_filename',
            'accuracy',
            'pos_hypo',
            'neg_hypo'
        ]

        df = list(zip(columns, values))

        with open(metadata_filename, 'w') as f:
            writer = csv.writer(f, delimiter = "\t")
            writer.writerows(df)

        sys.stdout.write('metadata written at: "%s"\n' % metadata_filename)
        sys.stdout.flush()
        
    def xgboost_classifier(self, tree_id_comp1):

        # tree_id_comp1 = self.tree_id_comp[0]

        if not tree_id_comp1:
            return None

        dataset = "H%s-H%s" % tuple(tree_id_comp1)
        new_prefix = self.make_specific_prefix(tree_id_comp1)
        model_filename = '%s.sav' % new_prefix

        sys.stdout.write('Processing: "%s" dataset\n' % dataset)
        sys.stdout.flush()

        features = self.features
        target = self.subset_tree_id(tree_id_comp1)

        # merge 
        aln_base,hypothesis = target.columns
        aln_feature = features.columns[0]

        target = target.rename({aln_base: aln_feature}, axis = 1)
        merged_dataset = features.merge(target, on = aln_feature, how='left')
        new_df = merged_dataset[merged_dataset[hypothesis].notna()].reset_index(drop=True)

        for c in self.drop_columns:
            try:
                new_df = new_df.drop( c, 1 )
            except KeyError:
                pass

        # hypotheses definition
        _groups_dict = { 
            True  : 'H%s' % tree_id_comp1[0],
            False : 'H%s' % tree_id_comp1[1]
        }

        split = StratifiedShuffleSplit(n_splits = 1, test_size = 0.25, random_state = 42)
        for train_index, _ in split.split(new_df, new_df[hypothesis]):
            strat_train_set = new_df.loc[train_index]
            # strat_test_set  = new_df.loc[test_index]
        
        train_num = strat_train_set.drop(hypothesis, axis=1)
        train_labels = strat_train_set[hypothesis] == tree_id_comp1[0]
    
        all_num  = new_df.drop(hypothesis, axis=1)
        all_labels = new_df[hypothesis] == tree_id_comp1[0]

        fr_tr = collections.Counter(all_labels)

        if len(fr_tr) <= 1:
            sys.stdout.write("Less than two labels found in the '%s' dataset\n" % dataset)
            sys.stdout.flush()
            return None
        
        scale_pos_weight = fr_tr[False]/fr_tr[True]

        xgb_clf_no_nor = xgboost.XGBClassifier(
                            objective = 'binary:logistic',
                            colsample_bytree = 0.5,
                            subsample = 0.9,

                            use_label_encoder = not True,
                            scale_pos_weight = scale_pos_weight,
                            
                            gamma = self.gamma,
                            learning_rate = self.learning_rate,
                            max_depth = self.max_depth,
                            reg_lambda = self.reg_lambda,
                            n_estimators = self.n_estimators,

                            n_jobs = self.threads
                        )

        xgb_clf_no_nor.fit(all_num, all_labels.tolist(),
                           eval_set = [ (train_num, train_labels.tolist()) ],
                           early_stopping_rounds = 2000,
                           verbose = False,
                           eval_metric = 'aucpr'
                        )

        accuracy = accuracy_score(all_labels, xgb_clf_no_nor.predict(all_num))
        self.shap_plots(xgb_clf_no_nor, all_num, new_prefix)
        joblib.dump(xgb_clf_no_nor, model_filename)

        self.create_metdata(
            new_prefix = new_prefix,
            values = [
                model_filename,
                accuracy,
                _groups_dict[True],
                _groups_dict[False]
            ]
        )

        return (all_num, all_labels, 
                _groups_dict, xgb_clf_no_nor, 
                dataset)

    def confusion_plots(self, mytables):

        if not mytables:
            return None

        cnf_mx_filename = "cnf_mx_%s.png" % self.model_prefix

        if len(self.tree_id_comp) <= 3:
            nrows = 1
            self.cnf_ncols = len(self.tree_id_comp)
            
        else:
            res = len(mytables) % self.cnf_ncols
            nrows = (len(mytables) // self.cnf_ncols) + bool(res)

        f,axes = plt.subplots(nrows = nrows, ncols = self.cnf_ncols, figsize=(18, 5), dpi = 400)
        for i in range(len(mytables)):
            X, y,_groups_dict,xgb_clf_no_nor,title = mytables[i]

            plot_confusion_matrix(
                xgb_clf_no_nor, X, y,
                values_format  = 'd',
                display_labels = [_groups_dict[i] for i in xgb_clf_no_nor.classes_],
                ax = axes[i]
            )
            axes[i].set_title(title, fontsize = 20)

        plt.savefig(cnf_mx_filename, bbox_inches = 'tight')
        plt.close()

    def xgboost_iterator(self):

        mytables = []
        for tree_id_comp1 in self.tree_id_comp:

            tmp_model = self.xgboost_classifier(tree_id_comp1)
            if tmp_model:
                mytables.append(tmp_model)

        self.confusion_plots(mytables)

# debugging --------------------------------------

# self = Post_ggi(
#     features_file = features_file,
#     all_ggi_results = all_ggi_results,
#     file_comparisons = file_comparisons,
#     threads = 6
# )

# self.xgboost_classifier_iterator()

# debugging --------------------------------------
