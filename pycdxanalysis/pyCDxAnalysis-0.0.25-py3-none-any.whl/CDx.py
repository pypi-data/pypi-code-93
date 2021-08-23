import json
from typing import Tuple, Union
import pandas as pd
import numpy as np
import re
import os
from tableone import TableOne
from collections import defaultdict
from io import StringIO

import pypeta
from pypeta import Peta
from pypeta import filter_description


class SampleIdError(RuntimeError):
    def __init__(self, sample_id: str, message: str):
        self.sample_id = sample_id
        self.message = message


class NotNumericSeriesError(RuntimeError):
    def __init__(self, message: str):
        self.message = message


class UnknowSelectionTypeError(RuntimeError):
    def __init__(self, message: str):
        self.message = message


class NotInColumnError(RuntimeError):
    def __init__(self, message: str):
        self.message = message


class GenesRelationError(RuntimeError):
    def __init__(self, message: str):
        self.message = message


class VariantUndefinedError(RuntimeError):
    def __init__(self, message: str):
        self.message = message


class ListsUnEqualLengthError(RuntimeError):
    def __init__(self, message: str):
        self.message = message


class DatetimeFormatError(RuntimeError):
    def __init__(self, message: str):
        self.message = message


class CDx_Data():
    """[summary]
    """
    def __init__(self,
                 mut_df: pd.DataFrame = None,
                 cli_df: pd.DataFrame = None,
                 cnv_df: pd.DataFrame = None,
                 sv_df: pd.DataFrame = None):
        """Constructor method with DataFrames

        Args:
            mut_df (pd.DataFrame, optional): SNV and InDel info. Defaults to None.
            cli_df (pd.DataFrame, optional): Clinical info. Defaults to None.
            cnv_df (pd.DataFrame, optional): CNV info. Defaults to None.
            sv_df (pd.DataFrame, optional): SV info. Defaults to None.
        """

        self.mut = mut_df
        self.cnv = cnv_df
        self.sv = sv_df

        if not cli_df is None:
            self.cli = cli_df
            self.cli = self._infer_datetime_columns()
        else:
            self._set_cli()

        self.crosstab = self.get_crosstab()

    def __len__(self):
        return 0 if self.cli is None else len(self.cli)

    def __getitem__(self, n):
        return self.select_by_sample_ids([self.cli.sampleId.iloc[n]])

    def __sub__(self, cdx):
        if self.cli is None and cdx.cli is None:
            return CDx_Data()

        cli = None if self.cli is None and cdx.cli is None else pd.concat(
            [self.cli, cdx.cli]).drop_duplicates(keep=False)
        mut = None if self.mut is None and cdx.mut is None else pd.concat(
            [self.mut, cdx.mut]).drop_duplicates(keep=False)
        cnv = None if self.cnv is None and cdx.cnv is None else pd.concat(
            [self.cnv, cdx.cnv]).drop_duplicates(keep=False)
        sv = None if self.sv is None and cdx.sv is None else pd.concat(
            [self.sv, cdx.sv]).drop_duplicates(keep=False)

        return CDx_Data(cli_df=cli, mut_df=mut, cnv_df=cnv, sv_df=sv)

    def __add__(self, cdx):
        if self.cli is None and cdx.cli is None:
            return CDx_Data()

        cli = pd.concat([self.cli, cdx.cli]).drop_duplicates()
        mut = pd.concat([self.mut, cdx.mut]).drop_duplicates()
        cnv = pd.concat([self.cnv, cdx.cnv]).drop_duplicates()
        sv = pd.concat([self.sv, cdx.sv]).drop_duplicates()

        return CDx_Data(cli_df=cli, mut_df=mut, cnv_df=cnv, sv_df=sv)

    def from_PETA(self,
                  token: str,
                  json_str: str,
                  host='https://peta.bgi.com/api'):
        """Retrieve CDx data from BGI-PETA database. 

        Args:
            token (str): Effective token for BGI-PETA database
            json_str (str): The json format restrictions communicating to the database
        """
        peta = Peta(token=token, host=host)
        peta.set_data_restriction_from_json_string(json_str)

        # peta.fetch_clinical_data() does`not process dtype inference correctly, do manully.
        #self.cli = peta.fetch_clinical_data()
        self.cli = pd.read_csv(
            StringIO(peta.fetch_clinical_data().to_csv(None, index=False)))
        self.mut = peta.fetch_mutation_data()
        self.cnv = peta.fetch_cnv_data()
        self.sv = peta.fetch_sv_data()

        # dedup for the same sampleId in different studyIds, discard the duplicated ones from all tables
        cli_original = self.cli
        self.cli = self.cli.drop_duplicates('sampleId')
        if (len(self.cli) < len(cli_original)):
            print('Duplicated sampleId exists, drop duplicates and go on')

        undup_tuple = [(x, y)
                       for x, y in zip(self.cli.sampleId, self.cli.studyId)]

        self.sv = self.sv[self.sv.apply(
            lambda x: (x['Tumor_Sample_Barcode'], x['studyId']) in undup_tuple,
            axis=1)].drop_duplicates()
        self.cnv = self.cnv[self.cnv.apply(
            lambda x: (x['Tumor_Sample_Barcode'], x['studyId']) in undup_tuple,
            axis=1)].drop_duplicates()
        self.mut = self.mut[self.mut.apply(
            lambda x: (x['Tumor_Sample_Barcode'], x['studyId']) in undup_tuple,
            axis=1)].drop_duplicates()

        # time series
        self.cli = self._infer_datetime_columns()
        self.crosstab = self.get_crosstab()

        return filter_description(json_str)

    def from_file(self,
                  mut_f: str = None,
                  cli_f: str = None,
                  cnv_f: str = None,
                  sv_f: str = None):
        """Get CDx data from files.

        Args:
            mut_f (str, optional): File as NCBI MAF format contains SNV and InDel. Defaults to None.
            cli_f (str, optional): File name contains clinical info. Defaults to None.
            cnv_f (str, optional): File name contains CNV info. Defaults to None.
            sv_f (str, optional): File name contains SV info. Defaults to None.
        """
        if not mut_f is None:
            self.mut = pd.read_csv(mut_f, sep='\t')

        if not cnv_f is None:
            self.cnv = pd.read_csv(cnv_f, sep='\t')

        if not sv_f is None:
            self.sv = pd.read_csv(sv_f, sep='\t')

        if not cli_f is None:
            self.cli = pd.read_csv(cli_f, sep='\t')
        else:
            self._set_cli()

        self.cli = self._infer_datetime_columns()
        self.crosstab = self.get_crosstab()

    def write_files(self, path: str = './'):
        """Write CDx_Data properties to 4 seprated files

        Args:
            path (str, optional): Path to write files. Defaults to './'.
        """
        if not self.cli is None:
            self.cli.to_csv(os.path.join(path, 'sample_info.txt'),
                            index=None,
                            sep='\t')
        if not self.mut is None:
            self.mut.to_csv(os.path.join(path, 'mut_info.txt'),
                            index=None,
                            sep='\t')
        if not self.cnv is None:
            self.cnv.to_csv(os.path.join(path, 'cnv_info.txt'),
                            index=None,
                            sep='\t')
        if not self.sv is None:
            self.sv.to_csv(os.path.join(path, 'fusion_info.txt'),
                           index=None,
                           sep='\t')

    def _set_cli(self):
        """Set the cli attribute, generate a void DataFrame when it is not specified. 
        """
        sample_id_series = []
        if not self.mut is None:
            sample_id_series.append(
                self.mut['Tumor_Sample_Barcode'].drop_duplicates())

        if not self.cnv is None:
            sample_id_series.append(
                self.cnv['Tumor_Sample_Barcode'].drop_duplicates())

        if not self.sv is None:
            sample_id_series.append(
                self.sv['Tumor_Sample_Barcode'].drop_duplicates())

        if len(sample_id_series) > 0:
            self.cli = pd.DataFrame({
                'sampleId': pd.concat(sample_id_series)
            }).drop_duplicates()
        else:
            self.cli = None

    def _infer_datetime_columns(self) -> pd.DataFrame:
        """To infer the datetime_columns and astype to datetime64 format

        Returns:
            pd.DataFrame: CDx.cli dataframe
        """
        cli = self.cli
        for column in cli.columns:
            if column.endswith('DATE'):
                try:
                    cli[column] = pd.to_datetime(cli[column])
                except Exception as e:
                    raise DatetimeFormatError(
                        f'{column} column end with "DATE" can not be transformed to datetime format'
                    )

        return cli

    def get_crosstab(self) -> pd.DataFrame:
        """Generate a Gene vs. Sample_id cross table.

        Raises:
            SampleIdError: Sample id from the mut, cnv or sv which not exsits in the cli table.

        Returns:
            pd.DataFrame: CDx_Data.
        """
        # 这里cli表中不允许存在相同的样本编号。会造成crosstab的列中存在重复，引入Series的boolen值无法处理的问题
        if (self.cli is None) or (len(self.cli) == 0):
            return pd.DataFrame([])

        sub_dfs = []
        # cli
        cli_crosstab = self.cli.copy().set_index('sampleId').T
        cli_crosstab['track_type'] = 'CLINICAL'
        sub_dfs.append(cli_crosstab)

        # mut. represent by cHgvs, joined by '|' for mulitple hit
        if (not self.mut is None) and (len(self.mut) != 0):
            mut_undup = self.mut[[
                'Hugo_Symbol', 'Tumor_Sample_Barcode', 'HGVSp_Short'
            ]].groupby([
                'Hugo_Symbol', 'Tumor_Sample_Barcode'
            ])['HGVSp_Short'].apply(lambda x: '|'.join(x)).reset_index()
            mut_crosstab = mut_undup.pivot('Hugo_Symbol',
                                           'Tumor_Sample_Barcode',
                                           'HGVSp_Short')
            mut_crosstab['track_type'] = 'MUTATIONS'

            sub_dfs.append(mut_crosstab)

        # cnv. represent by gain or loss. at first use the virtual column "copy_Num"
        if (not self.cnv is None) and (len(self.cnv) != 0):
            cnv_undup = self.cnv[[
                'Hugo_Symbol', 'Tumor_Sample_Barcode', 'status'
            ]].groupby([
                'Hugo_Symbol', 'Tumor_Sample_Barcode'
            ])['status'].apply(lambda x: '|'.join(x)).reset_index()
            cnv_crosstab = cnv_undup.pivot('Hugo_Symbol',
                                           'Tumor_Sample_Barcode', 'status')
            cnv_crosstab['track_type'] = 'CNV'

            sub_dfs.append(cnv_crosstab)

        # sv. represent by gene1 and gene2 combination. explode one record into 2 lines.
        if (not self.sv is None) and (len(self.sv) != 0):
            sv_undup = pd.concat([
                self.sv,
                self.sv.rename(columns={
                    'gene1': 'gene2',
                    'gene2': 'gene1'
                })
            ])[['gene1', 'Tumor_Sample_Barcode', 'gene2']].groupby([
                'gene1', 'Tumor_Sample_Barcode'
            ])['gene2'].apply(lambda x: '|'.join(x)).reset_index()
            sv_crosstab = sv_undup.pivot('gene1', 'Tumor_Sample_Barcode',
                                         'gene2')
            sv_crosstab['track_type'] = 'FUSION'

            sub_dfs.append(sv_crosstab)

        # pandas does not support reindex with duplicated index, so turn into multiIndex
        crosstab = pd.concat(sub_dfs)
        crosstab = crosstab.set_index('track_type', append=True)
        crosstab = crosstab.swaplevel()

        return crosstab

    #如何构建通用的选择接口，通过变异、基因、癌种等进行选择，并支持“或”和“且”的逻辑运算
    #该接口至关重要，对变异入选条件的选择会影响到crosstab，
    #选择后返回一个新的CDX_Data对象
    def select(self, conditions: dict = {}, update=True):
        """A universe interface to select data via different conditions.

        Args:
            conditions (dict, optional): Each key represent one column`s name of the CDx_Data attributes. Defaults to {}.
            update (bool, optional): [description]. Defaults to True.
        """
        return self

    # 数据选择的辅助函数
    def _numeric_selector(self, ser: pd.Series, range: str) -> pd.Series:
        """Compute a comparition expression on a numeric Series

        Args:
            ser (pd.Series): Numeric Series.
            range (str): comparition expression like 'x>5'. 'x' is mandatory and represent the input. 

        Raises:
            NotNumericSeriesError: Input Series`s dtype is not a numeric type.

        Returns:
            pd.Series: Series with boolean values.
        """
        if ser.dtype == 'object':
            raise NotNumericSeriesError(f'{ser.name} is not numeric')

        #return ser.map(lambda x: eval(re.sub(r'x', str(x), range)))
        return eval(re.sub(r'x', 'ser', range))

    def _catagory_selector(self, ser: pd.Series, range: list) -> pd.Series:
        """Return True if the Series` value in the input range list.

        Args:
            ser (pd.Series): Catagory Series.
            range (list): List of target options.

        Returns:
            pd.Series: Series with boolean values
        """
        return ser.isin(range)

    def _selector(self, df: pd.DataFrame, selections: dict) -> pd.DataFrame:
        """Filter the input DataFrame via the dict of conditions.

        Args:
            df (pd.DataFrame): Input.
            selections (dict): Dict format of conditions like "{'Cancer_type':['lung','CRC'],'Age':'x>5'}".
                The keys represent a column in the input DataFrame.
                The list values represent a catagory target and str values represent a numeric target.

        Raises:
            NotInColumnError: Key in the dict is not in the df`s columns.
            UnknowSelectionTypeError: The type of value in the dict is not str nor list.

        Returns:
            pd.DataFrame: Filterd DataFrame
        """
        columns = df.columns
        for key, value in selections.items():
            if key not in columns:
                raise NotInColumnError(f'{key} is not in the columns')

            if isinstance(value, str):
                df = df[self._numeric_selector(df[key], value)]
            elif isinstance(value, list):
                df = df[self._catagory_selector(df[key], value)]
            else:
                raise UnknowSelectionTypeError(
                    f'{selections} have values not str nor list')

        return df

    def _fuzzy_id(self, regex: re.Pattern, text: str) -> str:
        """transform a sample id into fuzzy mode according the regex pattern

        Args:
            regex (re.Pattern): The info retains are in the capture patterns
            text (str): input sample id

        Returns:
            str: fuzzy mode sample id
        """
        matches = regex.findall(text)
        if matches:
            text = '_'.join(matches[0])

        return text

    def select_by_sample_ids(self,
                             sample_ids: list,
                             fuzzy: bool = False,
                             regex_str: str = r'(\d+)[A-Z](\d+)',
                             study_ids: list = []):
        """Select samples via a list of sample IDs.

        Args:
            sample_ids (list): sample ids list.
            fuzzy (bool): fuzzy mode.
            regex_str (str): The match principle for fuzzy match. The info in the regex capture patterns must be matched for a certifired record. Default for r'(\d+)[A-Z](\d+)'.  
            study_ids: (list): The corresponding study id of each sample ids. Length of sample_ids and study_ids must be the same.

        Raises:
            ListsUnEqualLengthError: Length of sample_ids and study_ids are not equal.

        Returns:
            CDx: CDx object of selected samples.
        """
        if fuzzy:
            regex = re.compile(regex_str)

            # fuzzy the input ids
            target_ids = []
            fuzzy_to_origin = defaultdict(list)
            transform = lambda x: self._fuzzy_id(regex, x)
            for sample_id in sample_ids:
                fuzzy_sample_id = self._fuzzy_id(regex, sample_id)
                fuzzy_to_origin[fuzzy_sample_id].append(sample_id)
                target_ids.append(fuzzy_sample_id)
        else:
            target_ids = sample_ids
            transform = lambda x: x

        # match
        sample_id_bool = self.cli['sampleId'].map(transform).isin(target_ids)

        # no match, return immediately
        if not sample_id_bool.any():
            return CDx_Data()

        # with study ids
        if len(study_ids):
            if len(study_ids) != len(sample_ids):
                raise ListsUnEqualLengthError('Error')

            sub_cli_df = self.cli[sample_id_bool]
            study_id_bool = sub_cli_df.apply(
                lambda x: x['studyId'] == study_ids[target_ids.index(
                    transform(x['sampleId']))],
                axis=1)
            sample_id_bool = sample_id_bool & study_id_bool

        # construct new CDx_Data object
        # CDx_Data always have a cli
        cli_df = self.cli[sample_id_bool].copy()

        # add a column of query ids for fuzzy match
        # multi hit represent as a string
        if fuzzy:
            cli_df['queryId'] = cli_df['sampleId'].map(
                lambda x: ','.join(fuzzy_to_origin[transform(x)]))

        if not self.mut is None and len(self.mut) != 0:
            mut_df = self.mut[self.mut['Tumor_Sample_Barcode'].isin(
                cli_df['sampleId'])]
        else:
            mut_df = None

        if not self.cnv is None and len(self.cnv) != 0:
            cnv_df = self.cnv[self.cnv['Tumor_Sample_Barcode'].isin(
                cli_df['sampleId'])]
        else:
            cnv_df = None

        if not self.sv is None and len(self.sv) != 0:
            sv_df = self.sv[self.sv['Tumor_Sample_Barcode'].isin(
                cli_df['sampleId'])]
        else:
            sv_df = None

        return CDx_Data(cli_df=cli_df,
                        mut_df=mut_df,
                        cnv_df=cnv_df,
                        sv_df=sv_df)

    #
    def set_mut_eligibility(self, **kwargs):
        """Set threshold for SNV/InDels to regrard as a positive sample

        Raises:
            VariantUndefinedError: mut info not provided by user.

        Returns:
            CDx_Data: CDx_Data object
        """
        if self.mut is None:
            raise VariantUndefinedError(f'mut variant undefied')

        mut = self._selector(self.mut, kwargs)
        return CDx_Data(cli_df=self.cli,
                        mut_df=mut,
                        cnv_df=self.cnv,
                        sv_df=self.sv)

    def set_cnv_eligibility(self, **kwargs):
        """Set threshold for CNV to regrard as a positive sample.

        Raises:
            VariantUndefinedError: cnv info not provided by user.

        Returns:
            CDx_Data: CDx_Data object.
        """
        if self.cnv is None:
            raise VariantUndefinedError(f'cnv variant undefied')

        cnv = self._selector(self.cnv, kwargs)
        return CDx_Data(cli_df=self.cli,
                        mut_df=self.mut,
                        cnv_df=cnv,
                        sv_df=self.sv)

    def set_sv_eligibility(self, **kwargs):
        """Set threshold for SV to regrard as a positive sample.

        Raises:
            VariantUndefinedError: SV info not provided by user.

        Returns:
            CDx_Data: CDx_Data object.
        """
        if self.sv is None:
            raise VariantUndefinedError(f'sv variant undefied')

        sv = self._selector(self.sv, kwargs)
        return CDx_Data(cli_df=self.cli,
                        mut_df=self.mut,
                        cnv_df=self.cnv,
                        sv_df=sv)

    # 指定一个列名，再指定范围。离散型用数组，数值型
    # attrdict={'Cancer_type':['lung','CRC'],'Age':'x>5'}
    def select_samples_by_clinical_attributes2(self, attr_dict: dict):
        """Select samples via a set of conditions corresponding to the columns in the cli DataFrame.

        Args:
            attr_dict (dict): Dict format of conditions like "{'Cancer_type':['lung','CRC'],'Age':'x>5'}".
                The keys represent a column in the input DataFrame.
                The list values represent a catagory target and str values represent a numeric target.

        Returns:
            CDx: CDx object of selected samples.
        """
        cli_df = self._selector(self.cli, attr_dict)
        return self.select_by_sample_ids(cli_df['sampleId'])

    def select_samples_by_clinical_attributes(self, **kwargs):
        """Select samples via a set of conditions corresponding to the columns in the cli DataFrame.

        Args:
            Keywords arguments with each key represent a column in the input DataFrame.
                like "Cancer_type=['lung','CRC'], Age='x>5'"
                The list values represent a catagory target and str values represent a numeric target.

        Returns:
            CDx: CDx object of selected samples.
        """
        cli_df = self._selector(self.cli, kwargs)
        return self.select_by_sample_ids(cli_df['sampleId'])

    def select_samples_by_date_attributes(
        self,
        column_name: str = 'SAMPLE_RECEIVED_DATE',
        start='',
        end: str = '',
        days: int = 0,
        period: str = '',
    ):
        """Select samples using a datetime attribute in the cli dataframe

        Args:
            column_name (str, optional): Column used in the cli dataframe. Defaults to 'SAMPLE_RECEIVED_DATE'.
            from (str, optional): Time start point. Defaults to ''.
            to (str, optional): Time end point. Defaults to ''.
            days (int, optional): Days lasts. Defaults to ''.
            exact (str, optional): Exact range,eg '202005' for May in 2020 or '2021' for the whole year. Defaults to ''.
        """
        date_ser = self.cli.set_index(column_name)['sampleId']
        if period:
            cdx = self.select_by_sample_ids(date_ser[period])
        elif start and end:
            cdx = self.select_by_sample_ids(date_ser[start:end])
        elif start and days:
            cdx = self.select_by_sample_ids(date_ser[start:(
                pd.to_datetime(start) +
                pd.to_timedelta(days, 'D')).strftime("%Y-%m-%d")])
        elif end and days:
            cdx = self.select_by_sample_ids(date_ser[(
                pd.to_datetime(end) -
                pd.to_timedelta(days, 'D')).strftime("%Y-%m-%d"):end])

        return cdx

    # 对阳性样本进行选取。基因组合，且或关系，chgvs和ghgvs，基因系列如MMR、HR等
    # 基因组合可以做为入参数组来传入
    def select_samples_by_mutate_genes(
            self,
            genes: list = [],
            variant_type: list = ['MUTATIONS', 'CNV', 'FUSION'],
            how='or'):
        """Select sample via positve variant genes.

        Args:
            genes (list): Gene Hugo names. Defaults to [] for all mutated genes
            variant_type (list, optional): Combination of MUTATIONS, CNV and SV. Defaults to ['MUTATIONS', 'CNV', 'SV'].
            how (str, optional): 'and' for variant in all genes, 'or' for variant in either genes. Defaults to 'or'.

        Raises:
            GenesRelationError: Value of how is not 'and' nor 'or'.

        Returns:
            CDx: CDx object of selected samples.
        """
        variant_crosstab = self.crosstab.reindex(index=variant_type, level=0)
        if len(genes) != 0:
            variant_crosstab = variant_crosstab.reindex(index=genes, level=1)

        # Certain variant_types or genes get a empty table. all.() bug
        if len(variant_crosstab) == 0:
            return CDx_Data()

        gene_num = len(
            pd.DataFrame(list(
                variant_crosstab.index)).iloc[:, 1].drop_duplicates())

        if how == 'or':
            is_posi_sample = variant_crosstab.apply(
                lambda x: any(pd.notnull(x)))
        elif how == 'and':
            # reindex multiindex bug
            if len(genes) != 0 and len(genes) != gene_num:
                return CDx_Data()

            is_posi_sample = variant_crosstab.apply(
                lambda x: all(pd.notnull(x)))
        else:
            raise GenesRelationError(
                f'value of "how" must be "or" or "and", here comes "{how}"')

        # the last column is "track_type"
        sample_ids = is_posi_sample[is_posi_sample].index

        return self.select_by_sample_ids(sample_ids)

    # Analysis
    def tableone(self, **kwargs) -> TableOne:
        """Generate summary table1 using tableone library. Please refer to https://github.com/tompollard/tableone

        Args:
            columns : list, optional
                List of columns in the dataset to be included in the final table.
            categorical : list, optional
                List of columns that contain categorical variables.
            groupby : str, optional
                Optional column for stratifying the final table (default: None).
            nonnormal : list, optional
                List of columns that contain non-normal variables (default: None).
            min_max: list, optional
                List of variables that should report minimum and maximum, instead of
                standard deviation (for normal) or Q1-Q3 (for non-normal).
            pval : bool, optional
                Display computed P-Values (default: False).
            pval_adjust : str, optional
                Method used to adjust P-Values for multiple testing.
                The P-values from the unadjusted table (default when pval=True)
                are adjusted to account for the number of total tests that were performed.
                These adjustments would be useful when many variables are being screened
                to assess if their distribution varies by the variable in the groupby argument.
                For a complete list of methods, see documentation for statsmodels multipletests.
                Available methods include ::

                `None` : no correction applied.
                `bonferroni` : one-step correction
                `sidak` : one-step correction
                `holm-sidak` : step down method using Sidak adjustments
                `simes-hochberg` : step-up method (independent)
                `hommel` : closed method based on Simes tests (non-negative)

            htest_name : bool, optional
                Display a column with the names of hypothesis tests (default: False).
            htest : dict, optional
                Dictionary of custom hypothesis tests. Keys are variable names and
                values are functions. Functions must take a list of Numpy Arrays as
                the input argument and must return a test result.
                e.g. htest = {'age': myfunc}
            missing : bool, optional
                Display a count of null values (default: True).
            ddof : int, optional
                Degrees of freedom for standard deviation calculations (default: 1).
            rename : dict, optional
                Dictionary of alternative names for variables.
                e.g. `rename = {'sex':'gender', 'trt':'treatment'}`
            sort : bool or str, optional
                If `True`, sort the variables alphabetically. If a string
                (e.g. `'P-Value'`), sort by the specified column in ascending order.
                Default (`False`) retains the sequence specified in the `columns`
                argument. Currently the only columns supported are: `'Missing'`,
                `'P-Value'`, `'P-Value (adjusted)'`, and `'Test'`.
            limit : int or dict, optional
                Limit to the top N most frequent categories. If int, apply to all
                categorical variables. If dict, apply to the key (e.g. {'sex': 1}).
            order : dict, optional
                Specify an order for categorical variables. Key is the variable, value
                is a list of values in order.  {e.g. 'sex': ['f', 'm', 'other']}
            label_suffix : bool, optional
                Append summary type (e.g. "mean (SD); median [Q1,Q3], n (%); ") to the
                row label (default: True).
            decimals : int or dict, optional
                Number of decimal places to display. An integer applies the rule to all
                variables (default: 1). A dictionary (e.g. `decimals = {'age': 0)`)
                applies the rule per variable, defaulting to 1 place for unspecified
                variables. For continuous variables, applies to all summary statistics
                (e.g. mean and standard deviation). For categorical variables, applies
                to percentage only.
            overall : bool, optional
                If True, add an "overall" column to the table. Smd and p-value
                calculations are performed only using stratified columns.
            display_all : bool, optional
                If True, set pd. display_options to display all columns and rows.
                (default: False)
            dip_test : bool, optional
                Run Hartigan's Dip Test for multimodality. If variables are found to
                have multimodal distributions, a remark will be added below the Table 1.
                (default: False)
            normal_test : bool, optional
                Test the null hypothesis that a sample come from a normal distribution.
                Uses scipy.stats.normaltest. If variables are found to have non-normal
                distributions, a remark will be added below the Table 1.
                (default: False)
            tukey_test : bool, optional
                Run Tukey's test for far outliers. If variables are found to
                have far outliers, a remark will be added below the Table 1.
                (default: False)

        Returns:
            pd.DataFrame: Summary of the Data
        """
        table1 = TableOne(self.cli, **kwargs)
        return table1

    def pathway(self):
        pass

    def pinpoint(self):
        pass

    def oncoprint(self):
        pass

    def survival(self):
        pass

    # 画图的程序是否内置？
    def test_positive_rate(
            self,
            groupby='',
            groupby_genes=False,
            groupby_variant_type=False,
            genes_to_observe=[],
            variant_type_to_observe=['MUTATIONS', 'CNV', 'FUSION']):
        """Calculate the positvie rate for CDx object in user defined way

        Args:
            groupby (str, optional): Column name in the CDx_Data.cli DataFrame. Defaults to ''.
            groupby_genes (bool, optional): Groupby mutate genes. Defaults to False.
            groupby_variant_type (bool, optional): Groupby variant type, including MUTATIONS, CNV and SV. Defaults to False.
            genes_to_observe (list, optional): Genes list that should be considered. Defaults to [].
            variant_type_to_observe (list, optional): Variant type that shoud be considered. Defaults to ['MUTATIONS','CNV','SV'].

        Returns:
            Union[float,pd.Series]: A pd.Series when groupby options passed, a float value when not.
        """
        # empty CDx
        if len(self) == 0:
            return pd.Series([], dtype='float64')

        crosstab = self.crosstab.reindex(index=variant_type_to_observe,
                                         level=0)

        if genes_to_observe:
            crosstab = crosstab.reindex(index=genes_to_observe, level=1)

        test_posi_rate = None
        # skip the last track_type column
        if groupby:
            test_posi_rate = crosstab.groupby(
                self.crosstab.loc['CLINICAL', groupby],
                axis=1).apply(self._crosstab_to_positive_rate)
        elif groupby_genes:
            test_posi_rate = crosstab.groupby(level=1, sort=False).apply(
                self._crosstab_to_positive_rate)
        elif groupby_variant_type:
            test_posi_rate = crosstab.groupby(level=0, sort=False).apply(
                self._crosstab_to_positive_rate)
        else:
            test_posi_rate = self._crosstab_to_positive_rate(crosstab)

        # default to retrun a empty DataFrame which can cause problems
        if (not isinstance(test_posi_rate,
                           float)) and len(test_posi_rate) == 0:
            test_posi_rate = pd.Series([], dtype='float64')

        return test_posi_rate

    def _crosstab_to_positive_rate(self, df: pd.DataFrame):
        """Calculate a crosstab to generate a positive rate value for notnull cell

        Args:
            df (pd.DataFrame): CDx`s crosstab property

        Returns:
            float: positive rate
        """
        posi_rate = self._positive_rate(df.apply(lambda x: any(pd.notnull(x))),
                                        [True])[-1]
        return posi_rate

    def _positive_rate(self, values: list,
                       positive_tags: list) -> Tuple[int, int, float]:
        """Calculate positive tags marked values percentage in the total ones

        Args:
            values (list): the total values
            positive_tags (list): values that are regarded as positive values

        Returns:
            tuple: tuple for total values number, effective values number and percentage of positive values in the input values
        """
        values = list(values)

        total_value_num = len(values)
        missing_value_num = values.count(np.nan)
        effective_value_num = total_value_num - missing_value_num
        positvie_event_num = sum([values.count(tag) for tag in positive_tags])

        positive_rate = 0 if effective_value_num == 0 else positvie_event_num / effective_value_num

        return (total_value_num, effective_value_num, positive_rate)

    def sample_size_by_time(self):
        pass

    def sample_size(self, groupby=''):
        """Return the sample size by the way user defined

        Args:
            groupby (str, optional): Column name in the CDx_Data DataFrame. Defaults to ''.

        Returns:
            Union[int, pd.Series]: Sample size. a pd.Series when groupby options passed.
        """
        if groupby:
            if len(self) == 0:
                return pd.Series([],dtype=float)
            else:
                return self.crosstab.groupby(self.crosstab.loc['CLINICAL',
                                                               groupby],
                                             axis=1).size()
        else:
            return len(self)

    def gene_rearrangement_partner_distribute(self, genes=[]) -> pd.DataFrame:
        """Calculate the rearrangement partner distribution for input/all genes based on fusion table

        Args:
            genes (list, optional): Queried genes. Defaults to [].

        Returns:
            pd.DataFrame: Rearrangement partner distribution.
        """
        sv_df = pd.concat([
            self.sv,
            self.sv.rename(columns={
                'gene1': 'gene2',
                'gene2': 'gene1'
            })
        ])

        if genes:
            sv_df = sv_df[sv_df['gene1'].isin(genes)]

        return sv_df.groupby('gene1').apply(lambda x: pd.DataFrame(
            {
                'Frequency': x['gene2'].value_counts() / len(x),
                'Number': x['gene2'].value_counts(),
                'Total': len(x)
            }))
