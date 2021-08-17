from stataLogObject.Configs import *

from dataclasses import dataclass
from abc import ABC


@dataclass
class Table(ABC):
    mf: MF
    table_ext: ExtractTable
    body_iso: ExtractBody


@dataclass()
class TableConfigs:
    ols: Table = Table(
        LinearMF(MFVar('Number of obs =', var_type=int), MFVar("F("), MFVar('Prob > F =', key_extract=3),
                 MFVar('R-squared =', key_extract=3), MFVar('Root MSE =', key_extract=3), MFVar('Adj R-squared =')),
        ExtractTable(['Source', '|', 'SS', 'df', 'MS', 'Number', 'of', 'obs', '='], 1, [9]),
        ExtractBody(PValue(), skip_indexes=[0, 1, 2, 3, 4, 5])
    )

    ols_clu: Table = Table(
        LinearMF(MFVar('Number of obs =', var_type=int), MFVar("F("), MFVar('Prob > F ='), MFVar('R-squared ='),
                 MFVar('Root MSE =')),
        ExtractTable(['Linear', 'regression', 'Number', 'of', 'obs', '='], 1, [6]),
        ExtractBody(PValue())
    )

    hdfe: Table = Table(
        LinearMF(MFVar('Number of obs =', var_type=int), MFVar("F(", key_extract=2), MFVar('Prob > F ='),
                 MFVar('R-squared ='), MFVar('Root MSE ='), MFVar('Adj R-squared ='), MFVar("Within R-sq. =")),
        ExtractTable(['HDFE', 'Linear', 'regression', 'Number', 'of', 'obs', '='], 1, [7]),
        ExtractBody(PValue())

    )

    fe_within: Table = Table(
        PanelMF(MFVar('Number of obs =', var_type=int), MFVar('Number of groups =', var_type=int),
                MFVar('min =', int, 1), MFVar('avg =', float, 1), MFVar('max =', int, 1), MFVar("F("),
                MFVar('Prob > F =', key_extract=1), MFVar('within ='), MFVar('between ='), MFVar('overall ='),
                MFVar('sigma_u |'), MFVar('sigma_e |'), MFVar('rho |')),
        ExtractTable(['Fixed-effects', '(within)', 'regression', 'Number', 'of', 'obs', '='], 3, [7]),
        ExtractBody(PValue())

    )

    # TODO: Need to create an optional bool within VarField and create a new method type called GroupVar to handle the
    #   multiple (and potentially absent) group variable definitions
    mixed: Table = Table(
        MixedMF(MFVar('Number of obs =', var_type=int), MFVar('Wald chi2'), MFVar('Prob > chi2 =', key_extract=1),
                MFVar('Log likelihood ='), REVar('Random-effects Parameters')),
        ExtractTable(['Mixed-effects', 'ML', 'regression', 'Number', 'of', 'obs', '='], 4, [7]),
        ExtractBody(PValue())

    )

    summary: Table = Table(
        MF(),
        ExtractTable(['Variable', '|', 'Obs', 'Mean', 'Std.', 'Dev.', 'Min', 'Max'], 0),
        ExtractBody(Summary())
    )

    tabulate: Table = Table(
        TabMF(MFVar('Total |', int)),
        ExtractTable(['|', 'Freq.', 'Percent', 'Cum.'], 0, [0]),
        ExtractBody(Tabulate(), 0, [-1])
    )
