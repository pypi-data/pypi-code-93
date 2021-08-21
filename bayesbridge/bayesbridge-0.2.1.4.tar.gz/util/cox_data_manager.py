import numpy as np
import scipy as sp
import scipy.sparse
import pandas as pd
import pickle as pkl
from warnings import warn

class DataManager(object):

    # TODO: Consider including the interaction between treatment and propensity strata.
    def __init__(
            self, path_to_data, outcome_name='cardio_disease',
            stratified=True, include_main_effect=True, include_interaction=True,
            include_gender_age_interaction=False, stratified_by_menopause=False,
            exclude_subgroup_indicator=False, n_strata=5, baseline_strata=None,
            treatment_encoding='thiazide'):

        if outcome_name not in ['cardio_disease', 'angioedema']:
            raise ValueError('Invalid outcome name.')

        if stratified_by_menopause and include_gender_age_interaction:
            warn("Gender-age interaction not included when stratified "
                 "by the menopausal states.")
            include_gender_age_interaction = False

        if not stratified:
            n_strata = 1
        if baseline_strata is None:
            baseline_strata = int(n_strata / 2)
        self.folder = path_to_data
        self.outcome_name = outcome_name
        if outcome_name == 'cardio_disease':
            self._filename_prefix = ''
        else:
            self._filename_prefix = outcome_name + '_study_'
        self.stratified = stratified
        self.include_main_effect = include_main_effect
        self.include_interaction = include_interaction
        self.include_gender_age_interaction = include_gender_age_interaction
        self.stratified_by_menopause = stratified_by_menopause
        self.exclude_subgroup_indicator = exclude_subgroup_indicator
        self.n_strata = n_strata
        self.baseline_strata = baseline_strata
        self.treatment_encoding = treatment_encoding

    @property
    def n_age_groups(self):
        _, _, age_names \
            = self.get_age_and_gender_indicator_among_binary_covariates()
        return len(age_names)

    @property
    def n_age_gender_interaction(self):
        interaction_included = int(
            self.include_gender_age_interaction or self.stratified_by_menopause
        )
        return interaction_included * 2 * self.n_age_groups

    @property
    def n_fixed_effect(self):
        return (
            1 + self.stratified * (self.n_strata - 1)
            + self.n_age_gender_interaction
        )

    def read_legend_outcome(self, type='survival_time'):
        """
        Parameters
        ----------
        type : str, {'treatment', 'survival_time'}
        """

        if type == 'treatment':
            outcome = self.read_treatment_indicator(self.treatment_encoding)

        elif type == 'survival_time':
            event_time = np.genfromtxt(
                self.folder + self._filename_prefix + 'event_time.txt',
                missing_values='NA', filling_values=np.inf
            )
            censoring_time = np.genfromtxt(
                self.folder + self._filename_prefix + 'censoring_time.txt',
                missing_values='NA', filling_values=np.inf
            )
            outcome = (event_time, censoring_time)

        else:
            raise ValueError()

        return outcome

    def read_legend_design_matrix(self, matrix_format='csr'):
        """ Read the (pre-processed) design matrix. """

        X = self.read_legend_predictors()
        treatment = self.read_treatment_indicator(self.treatment_encoding)
        treatment = sp.sparse.csc_matrix(treatment[:, np.newaxis])

        if self.include_interaction:
            X_interaction = self.create_interaction(treatment, X)

        if not self.include_main_effect:
            X = sp.sparse.csc_matrix((X.shape[0], 0))

        if self.include_gender_age_interaction or self.stratified_by_menopause:
            X_age_gender_main = self.read_age_and_gender_interaction()
            X_age_gender_interaction = self.create_interaction(
                treatment, X_age_gender_main
            )
            X = sp.sparse.hstack((
                X_age_gender_main, X_age_gender_interaction, X
            ))

        if self.include_interaction:
            X = sp.sparse.hstack((X, X_interaction))

        if self.stratified:
            strata_id = self.read_propensity_strata()
            X = sp.sparse.hstack((strata_id, X))

        X = sp.sparse.hstack((treatment, X))
        return X.asformat(matrix_format)

    def read_age_and_gender_interaction(self):
        X_bin = self.read_sp_coo(
            self.folder + self._filename_prefix + 'sparse_design_matrix_binary_part.txt')
        X_bin = X_bin.tocsc()
        age_indicator, gender_indicator, age_name \
            = self.get_age_and_gender_indicator_among_binary_covariates()
        X_gender = X_bin[:, gender_indicator]
        if self.stratified_by_menopause:
            X_menopause_status = sp.sparse.hstack([
                sp.sparse.csc_matrix(X_bin[:, indicator].sum(-1) > 0)
                for indicator in age_indicator
            ])
            X_age_gender = self.create_interaction(
                X_gender, X_menopause_status
            )
        else:
            X_age_gender = self.create_interaction(
                X_gender, X_bin[:, age_indicator]
            )
        return X_age_gender

    def get_age_and_gender_indicator_among_binary_covariates(
            self, sorted_by_age=True):
        binary_covariate_names = np.loadtxt(
            self.folder + self._filename_prefix + 'covariate_name_binary_part.txt',
            dtype=np.str_, delimiter='\n'
        )
        gender_indicator = self.search_covariate_indices(
            'gender = FEMALE', exclude_words='Subgroup',
            covariate_name=binary_covariate_names
        )
        age_indicator = self.search_covariate_indices(
            'age group', covariate_name=binary_covariate_names
        )
        age_name = binary_covariate_names[age_indicator]
        if sorted_by_age:
            sort_index = np.argsort([name.split(': ')[-1] for name in age_name])
            age_indicator = age_indicator[sort_index]
            age_name = age_name[sort_index]
        if self.stratified_by_menopause:
            age_ranges = self.get_age_range(age_name)
            menopause_onset = 45
            menopause_end = 55
            pre_menopause_indicator = age_indicator[[
                age_range[-1] < menopause_onset for age_range in age_ranges
            ]]
            peri_menopause_indicator = age_indicator[[
                menopause_onset <= age_range[0] and age_range[1] < menopause_end
                for age_range in age_ranges
            ]]
            post_menopause_indicator = age_indicator[[
                menopause_end <= age_range[0]
                for age_range in age_ranges
            ]]
            age_indicator = [
                pre_menopause_indicator, peri_menopause_indicator, post_menopause_indicator
            ]
            age_name = ['pre_menopause', 'peri_menopause', 'post_menopause']
        return age_indicator, gender_indicator, age_name

    @staticmethod
    def get_age_range(age_name):
        return [np.array(name.split(': ')[-1].split('-'), dtype=np.int)
                for name in age_name]

    @staticmethod
    def create_interaction(covariate, X):
        """ Create interaction between one covariate and columns of a design matrix. """
        X = X.tocsc()
        X_interaction = sp.sparse.hstack(tuple(
            X[:, j].multiply(covariate)
            for j in range(X.shape[1])
        ))
        return X_interaction

    def read_treatment_indicator(self, encoding=None):
        """
        Parameters
        ----------
        encoding : {'ace', 'thiazide', None}
        """
        if encoding is None:
            encoding = self.treatment_encoding

        treatment = np.loadtxt(
            self.folder + self._filename_prefix + 'treatment.txt')
        if encoding == 'thiazide':
            treatment = 1 - treatment
        return treatment

    def read_legend_predictors(self, format='csr'):
        """ Return the design matrix for the clinical covariates (main effects). """
        X_bin = self.read_sp_coo(
            self.folder + self._filename_prefix + 'sparse_design_matrix_binary_part.txt')
        if self.exclude_subgroup_indicator:
            subgroup_col_indicator = self.get_subgroup_column_indicator()
            X_bin = X_bin.tocsc()[:, np.logical_not(subgroup_col_indicator)]
        X_cont = self.read_sp_coo(
            self.folder + self._filename_prefix + 'sparse_design_matrix_cont_part.txt')
        X = sp.sparse.hstack((X_bin, X_cont), format=format)

        return X

    def get_diabetes_subgroup_column_id(self):
        column_id_bin = np.loadtxt(
            self.folder + self._filename_prefix + 'covariate_id_binary_part.txt')
        return np.where(column_id_bin == 7998)[0]

    def get_subgroup_column_indicator(self, return_index=False):
        subgroup_id = [1998, 2998, 3998, 4998, 5998, 6998, 7998, 8998]
        column_id_bin = np.loadtxt(
            self.folder + self._filename_prefix + 'covariate_id_binary_part.txt')
        subgroup_col_indicator = \
            np.array([id in subgroup_id for id in column_id_bin])
        if return_index:
            subgroup_col_indicator = np.where(subgroup_col_indicator)[0]
        return subgroup_col_indicator

    def read_sp_coo(self, filename):
        A = pd.read_table(filename, delim_whitespace=True,
                          dtype={'i': np.int32, 'j': np.int32, 'val': np.float64})
        A = sp.sparse.coo_matrix((A.val, (A.i, A.j)))
        return A

    def read_propensity_strata(self):
        propensity_score = np.loadtxt(
            self.folder + self._filename_prefix + 'propensity_score.txt')
        strata_ind = DataManager.create_strata_indicator(
            propensity_score, self.n_strata, self.baseline_strata
        )
        return strata_ind

    def read_covariate_name(self):

        covariate_name = self.read_legend_predictor_names()

        if self.treatment_encoding == 'ace':
            drug_name = "ACE inhibitor"
        else:
            drug_name = "thiazide diuretics"

        if self.include_interaction:
            interaction_name = np.array([
                drug_name + " interaction with " + name for name in covariate_name
            ])

        if not self.include_main_effect:
            covariate_name = np.array([], dtype=np.unicode_)

        if self.include_gender_age_interaction or self.stratified_by_menopause:
            _, gender_indicator, age_names \
                = self.get_age_and_gender_indicator_among_binary_covariates()
            age_gender_main_name = np.array([
                'gender = FEMALE in ' + age_name
                for age_name in age_names
            ])
            age_gender_interaction_name = np.array([
                drug_name + " interaction with " + age_gender_name
                for age_gender_name in age_gender_main_name
            ])
            covariate_name = np.concatenate((
                age_gender_main_name, age_gender_interaction_name, covariate_name
            ))

        if self.include_interaction:
            covariate_name = np.concatenate((covariate_name, interaction_name))

        if self.stratified:
            strata_id_name = np.array([
                'propensity_strata_' + str(i + 1)
                for i in range(self.n_strata)
            ])
            strata_id_name = np.delete(strata_id_name, self.baseline_strata)
            covariate_name = np.concatenate((strata_id_name, covariate_name))

        covariate_name = np.concatenate((
            ['Treatment by ' + drug_name], covariate_name
        ))
        return covariate_name

    def read_legend_predictor_names(self):
        """ Return the names of the main effects. """
        cont_covariate_name = np.loadtxt(
            self.folder + self._filename_prefix + 'covariate_name_cont_part.txt',
            dtype=np.str_, delimiter='\n'
        )
        bin_convariate_name = np.loadtxt(
            self.folder + self._filename_prefix + 'covariate_name_binary_part.txt',
            dtype=np.str_, delimiter='\n'
        )
        if self.exclude_subgroup_indicator:
            subgroup_col_indicator = self.get_subgroup_column_indicator()
            bin_convariate_name = bin_convariate_name[
                np.logical_not(subgroup_col_indicator)
            ]
        covariate_name = np.concatenate((
            bin_convariate_name, cont_covariate_name
        ))
        return covariate_name

    def shorten_covariate_name(self, names):
        names = np.atleast_1d(names)
        names = np.array([
            self._shorten_singleton_covariate_name(name) for name in names
        ])
        if names.size == 1:
            names = names[0]
        return names

    @staticmethod
    def _shorten_singleton_covariate_name(name):
        emdash = '\u2014'
        return name.replace(
            'during day -365 through 0 days relative to index:', emdash
        ).replace(
            'during day -30 through 0 days relative to index:', emdash
        )

    def search_covariate_indices(
            self, keywords, exclude_words=None, covariate_name=None):
        if covariate_name is None:
            covariate_name = self.read_covariate_name()

        keywords = np.atleast_1d(keywords)
        keywords = np.array([word.lower() for word in keywords])
        if exclude_words is not None:
            exclude_words = np.atleast_1d(exclude_words)
            exclude_words = np.array([word.lower() for word in exclude_words])

        covariate_index = np.where(np.array([
            self.has_keyword(name.lower(), keywords, exclude_words)
            for name in covariate_name
        ]))[0]

        if covariate_index.size == 1:
            covariate_index = covariate_index.item()

        return covariate_index

    def get_gender_index(self):
        gender_index = self.search_covariate_indices(
            'gender = FEMALE', exclude_words='interaction'
        )
        treatment_gender_index = self.search_covariate_indices(
            [self.treatment_encoding, 'gender = FEMALE']
        )
        gender_age_index = self.search_covariate_indices(
            'gender = FEMALE interaction with age group'
        )
        return gender_index, treatment_gender_index, gender_age_index

    def has_keyword(self, string, keywords, exclude_words=None):
        """ Check that all the keywords matche and that none of
        the exclusion words match. """
        keyword_found = np.all([word in string for word in keywords])
        if exclude_words is None:
            exclude_word_found = False
        else:
            exclude_word_found = np.any([
                word in string for word in exclude_words
            ])
        return keyword_found and (not exclude_word_found)

    @staticmethod
    def create_strata_indicator(score, n_strata, baseline_strata):
        """
        Parameters
        ----------
        baseline_strata : int
            zero-based index
        """
        percent = np.linspace(0, 100, n_strata + 1)
        percentile = np.percentile(score, percent)
        percentile[0] -= 1  # Make sure the inequality behaves correctly.
        X = np.logical_and(
            percentile[np.newaxis, :-1] < score[:, np.newaxis],
            score[:, np.newaxis] <= percentile[np.newaxis, 1:]
        ).astype(np.float)
        X = np.delete(X, baseline_strata, axis=1)
        return sp.sparse.csr_matrix(X)
