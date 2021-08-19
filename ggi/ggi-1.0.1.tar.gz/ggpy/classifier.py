

import shap
import joblib
import xgboost
import collections
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.metrics import roc_curve, auc, accuracy_score, plot_confusion_matrix



features_file = 'features_exons1024'
label_file    = 'joined_out_ggi_1018exons_protein.txt_rooted_groups.tsv_filtered'
model_prefix  = 'no_normalized_4200trees_rank_1_105_hypothesis_aa_h1_VS_h6'
threads = 5

# def plot_roc_curve(all_classes, labels, probas_forest, leg_trans = False):
#     plt.figure(figsize=(8, 6), dpi=80)
#     for i in range(len(all_classes)):
#         # false postive rate & true postive rate
#         fpr, tpr, _ = roc_curve( labels == all_classes[i],  probas_forest[:,i] ) 
#         # area under the curve
#         roc_auc = auc(fpr, tpr) 
#         if leg_trans:
#             leg =  _groups_dict[all_classes[i]]
#         else:
#             leg = all_classes[i]


#         label = "%s (area = %.3f)" % ( leg, roc_auc)
#         plt.plot( fpr, tpr, linewidth = 2, label = label )

#     plt.plot([0,1], [0,1], 'k--', color='black')
#     plt.xlim([0.0, 1.0])
#     plt.ylim([0.0, 1.05])
#     plt.xlabel('False Positive Rate')
#     plt.ylabel('True Positive Rate')
#     plt.legend(loc="lower right")





def main():

    model_filename   = model_prefix + '.sav'
    cnf_mx_filename  = "cnf_mx_%s.png" % model_prefix
    bee_20_filename  = "20best_beeswarm_%s.png" % model_prefix
    bee_all_filename = "all_beeswarm_%s.png" % model_prefix


    features = pd.read_csv(features_file, sep = '\t')
    target   = pd.read_csv(label_file, sep = '\t')


    # merge 
    aln_base,hypothesis = target.columns
    aln_feature = features.columns[0]

    target = target.rename({ aln_base: aln_feature}, axis = 1)
    merged_dataset = features.merge( target, on = aln_feature, how='left')
    new_df = merged_dataset[merged_dataset[hypothesis].notna()].reset_index(drop=True)

    # drop columns
    drop_columns = ['Group', 'aln_base', 
                    'SymPval', 'MarPval', 
                    'IntPval']

    for c in drop_columns:
        try:
            new_df = new_df.drop( c, 1 )
        except KeyError:
            pass


    # hypotheses definition
    groups = target[hypothesis].unique().tolist()
    _groups_dict = { True  : 'H1', False : 'H2'}


    split = StratifiedShuffleSplit(n_splits = 1, test_size = 0.25, random_state = 42)
    for train_index, test_index in split.split(new_df, new_df[hypothesis]):
        strat_train_set = new_df.loc[train_index]
        strat_test_set  = new_df.loc[test_index]


    test_num     = strat_test_set.drop(hypothesis, axis=1)
    test_labels  = strat_test_set[hypothesis] == groups[0]

    train_num    = strat_train_set.drop(hypothesis, axis=1)
    train_labels = strat_train_set[hypothesis] == groups[0]

    all_num      = new_df.drop(hypothesis, axis=1)
    all_labels   = new_df[hypothesis] == groups[0]



    fr_tr = collections.Counter(all_labels)
    scale_pos_weight = fr_tr[False]/fr_tr[True]


    xgb_clf_no_nor = xgboost.XGBClassifier(
                objective='binary:logistic',
                subsample = 0.9,
                use_label_encoder=True,
                scale_pos_weight = scale_pos_weight,
                colsample_bytree = 0.5,
                gamma = 0.14210526315789473,
                learning_rate = 0.03,
                max_depth = 4,
                reg_lambda =0.018,
                n_estimators = 4200,
                n_jobs = threads
            )

    xgb_clf_no_nor.fit(all_num, all_labels.tolist(),
                eval_set=[(train_num, train_labels.tolist())],
                early_stopping_rounds=2000,
                verbose=True,
                eval_metric='aucpr'
                )


    joblib.dump(xgb_clf_no_nor, model_filename)

    mytables = [
        (train_num, train_labels, "Train dataset"),
        (test_num , test_labels , "Test dataset"),
        (all_num  , all_labels  , "Whole dataset")
    ]


    accuracy_score(all_labels, xgb_clf_no_nor.predict(all_num)) # 0.9846153846153847



    f,axes = plt.subplots( nrows=1, ncols= len(mytables), figsize=(18, 5) , dpi=400)
    for i in range(len(mytables)):

        X,y,title = mytables[i]
        plot_confusion_matrix( 
            xgb_clf_no_nor, X, y,
            values_format  = 'd',
            display_labels = [_groups_dict[i] for i in xgb_clf_no_nor.classes_],
            ax=axes[i]
        )
        axes[i].set_title( title, fontsize = 20)

    plt.savefig( cnf_mx_filename, bbox_inches = 'tight' )


    explainer   = shap.Explainer(xgb_clf_no_nor, all_num)
    shap_values = explainer(all_num)


    shap.plots.beeswarm(shap_values,
                        max_display = 20,
                        show = False)
    plt.tight_layout(pad=0.05)
    plt.savefig(bee_20_filename, dpi = 330)



    shap.plots.beeswarm(shap_values,
                        max_display = len(all_num.columns),
                        show = False)
    plt.tight_layout(pad=0.05)
    plt.savefig(bee_all_filename, dpi = 330)



if __name__ == "__main__":
    main()
