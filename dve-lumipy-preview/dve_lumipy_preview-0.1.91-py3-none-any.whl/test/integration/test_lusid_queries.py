import unittest
import lumipy as lm
import datetime as dt
import pandas as pd
from functools import reduce

from test.test_utils import load_secrets_into_env_if_local_run


class TestLusidQueries(unittest.TestCase):

    """Integration tests for client use cases.

    """

    def setUp(self) -> None:
        load_secrets_into_env_if_local_run()
        self.atlas = lm.get_atlas()

    def test_lusid_holdings_tutorial_queries(self):

        # Following tutorial 3 in example notebooks
        holdings = self.atlas.lusid_portfolio_holding(
            effective_at=dt.datetime(2021, 3, 1),
            as_at=dt.datetime(2021, 3, 8)
        )

        # Query 1: basic select with aliases
        selected = holdings.select(
            holdings.lusid_instrument_id,
            holdings.cost_amount,
            holdings.cost_currency,
            holdings.settled_units,
            Millions=holdings.cost_amount * 1e-6,  # Function of provider column input
            SomeExchangeRate=1.5  # Literal input
        )

        df1 = selected.limit(5).go()

        self.assertIsInstance(df1, pd.DataFrame)
        self.assertEqual(df1.shape[0], 5)
        self.assertEqual(df1.shape[1], 6)
        self.assertIn('Millions', df1.columns)
        self.assertIn('SomeExchangeRate', df1.columns)

        # Query 2: where condition
        condition = (holdings.portfolio_scope == 'Finbourne-Examples') & (holdings.cost_currency == 'USD')
        qry = selected.where(condition)
        df2 = qry.go()

        self.assertIsInstance(df2, pd.DataFrame)
        self.assertEqual(df2.shape[0], 27)
        self.assertEqual(df2.shape[1], 6)

        # Query 3: group by and ordering
        total_cost = holdings.cost_amount_portfolio_currency.sum()
        ordering = total_cost.descending()
        top5_cost = holdings.select(
            holdings.cost_currency,
            holdings.lusid_instrument_id,
        ).where(
            condition
        ).group_by(
            holdings.lusid_instrument_id
        ).aggregate(
            TotalCostAmount=total_cost
        ).order_by(
            ordering
        ).limit(5)

        df3 = top5_cost.go()
        self.assertIsInstance(df3, pd.DataFrame)
        self.assertEqual(df3.shape[0], 5)
        self.assertEqual(df3.shape[1], 3)

        diffs = df3['TotalCostAmount'].diff().values[1:]
        self.assertTrue(all(d <= 0 for d in diffs))

        # Query4: Having expression query
        over_1billion = holdings.select(
            holdings.cost_currency,
            holdings.lusid_instrument_id,
        ).where(
            condition
        ).group_by(
            holdings.lusid_instrument_id
        ).aggregate(
            TotalCostAmount=total_cost
        ).having(
            total_cost > 1e9
        )
        df4 = over_1billion.go()
        self.assertIsInstance(df4, pd.DataFrame)
        self.assertEqual(df4.shape[0], 3)
        self.assertEqual(df4.shape[1], 3)

    def test_lusid_quotes_tutorial_queries(self):

        Quotes = self.atlas.lusid_instrument_quote
        quotes = Quotes(
            as_at=dt.datetime(2021, 4, 9)
        )

        # Query 1: table variable
        table_var = quotes.select(
            quotes.instrument_id,
            quotes.value
        ).limit(25).to_table_var('test')

        qry1 = table_var.select(table_var.instrument_id).group_by(
            table_var.instrument_id
        ).aggregate(
            MinVal=table_var.value.min(),
            MedianVal=table_var.value.median(),
            MeanVal=table_var.value.mean(),
            MaxVal=table_var.value.max()
        )

        df1 = qry1.go()
        self.assertIsInstance(df1, pd.DataFrame)
        self.assertEqual(df1.shape[0], 1)
        self.assertEqual(df1.shape[1], 5)

        # Query 2: scalar variable
        Holdings = self.atlas.lusid_portfolio_holding
        holding = Holdings(
            effective_at=dt.datetime(2021, 3, 1),
            as_at=dt.datetime(2021, 3, 8)
        )

        total_cost = holding.select(
            TotalCost=holding.cost_amount_portfolio_currency.sum()
        ).where(
            holding.portfolio_scope == 'Finbourne-Examples'
        ).to_scalar_var('cost_total')

        qry2 = holding.select(
            holding.portfolio_code,
            holding.lusid_instrument_id,
            holding.cost_amount_portfolio_currency,
            CostFractionPc=100 * holding.cost_amount_portfolio_currency / total_cost
        ).where(
            holding.portfolio_scope == 'Finbourne-Examples'
        ).order_by(
            (holding.cost_amount_portfolio_currency / total_cost).descending()
        ).limit(5)

        df2 = qry2.go()
        self.assertIsInstance(df2, pd.DataFrame)
        self.assertEqual(df2.shape[0], 5)
        self.assertEqual(df2.shape[1], 4)
        self.assertTrue(all(df2.CostFractionPc.values <= 100.0))

    def test_lusid_joins_tutorial_queries(self):

        all_portfolios = self.atlas.lusid_portfolio_holding(
            effective_at=dt.datetime(2021, 4, 9),
            as_at=dt.datetime(2021, 4, 9)
        )
        example_pfs = all_portfolios.select('*').where(
            all_portfolios.portfolio_scope == 'Finbourne-Examples'
        ).to_table_var('example_portfolios')

        portfolios = example_pfs.with_alias('ptf')
        holdings = self.atlas.lusid_portfolio_holding(
            effective_at=dt.datetime(2021, 4, 9),
            as_at=dt.datetime(2021, 4, 9)
        ).with_alias('hld')
        instruments = self.atlas.lusid_instrument(
            effective_at=dt.datetime(2021, 4, 9),
            as_at=dt.datetime(2021, 4, 9)
        ).with_alias('ins')
        properties = self.atlas.lusid_property(
            effective_at=dt.datetime(2021, 4, 9),
            as_at=dt.datetime(2021, 4, 9)
        ).with_alias('prp')
        quotes = self.atlas.lusid_instrument_quote.get_class(
        )(
            as_at=dt.datetime(2021, 4, 9)
        ).with_alias('qte')

        # Query 1: simple join
        join = example_pfs.left_join(
            holdings,
            on=(holdings.portfolio_code == example_pfs.portfolio_code) &
               (holdings.portfolio_scope == 'Finbourne-Examples')
        )

        qry1 = join.select('^')
        df1 = qry1.go()
        self.assertIsInstance(df1, pd.DataFrame)
        self.assertEqual(df1.shape[0], 592)
        self.assertEqual(df1.shape[1], 18)

        # Query 2: chained join
        join = example_pfs.left_join(
            holdings,
            on=(example_pfs.portfolio_code == holdings.portfolio_code) &
               (holdings.portfolio_scope == 'Finbourne-Examples')
        ).left_join(
            properties,
            on=(properties.domain == 'Instrument') &
               (properties.entity_id_type == 'LusidInstrumentId') &
               (properties.entity_id == holdings.lusid_instrument_id)
        ).left_join(
            quotes,
            on=holdings.lusid_instrument_id == quotes.instrument_id
        )
        qry2 = join.select(
            join.portfolio_code_lhs,
            join.lusid_instrument_id_lhs
        ).group_by(
            join.lusid_instrument_id_lhs
        ).aggregate(
            MeanQuoteValue=join.value_qte.mean(),
            StddQuoteValue=join.value_qte.stdev()
        )

        df2 = qry2.go()
        self.assertIsInstance(df2, pd.DataFrame)
        self.assertEqual(df2.shape[0], 49)
        self.assertEqual(df2.shape[1], 4)

    def test_lusid_unions(self):
        portfolios = self.atlas.lusid_portfolio(
            effective_at=dt.datetime(2021, 4, 9),
            as_at=dt.datetime(2021, 4, 9)
        )
        pf_codes = portfolios.select(portfolios.portfolio_code).where(
            (portfolios.portfolio_scope == 'Finbourne-Examples') &
            (portfolios.portfolio_code.like('%equ%')) &
            (portfolios.portfolio_code.not_like('%swap%'))
        ).go().PortfolioCode.tolist()

        holding = self.atlas.lusid_portfolio_holding(
            effective_at=dt.datetime(2021, 4, 9),
            as_at=dt.datetime(2021, 4, 9)
        )

        def subquery(pf_code):
            total_cost = holding.select(
                TotalCost=holding.cost_amount_portfolio_currency.sum()
            ).where(
                (holding.portfolio_code == pf_code) &
                (holding.portfolio_scope == 'Finbourne-Examples')
            ).to_scalar_var(f'cost_total_{abs(hash(pf_code))}')

            return holding.select(
                holding.portfolio_code,
                holding.lusid_instrument_id,
                holding.cost_amount_portfolio_currency,
                CostFractionPc=100 * holding.cost_amount_portfolio_currency / total_cost
            ).where(
                (holding.portfolio_code == pf_code) &
                (holding.portfolio_scope == 'Finbourne-Examples')
            ).order_by(
                (holding.cost_amount_portfolio_currency / total_cost).descending()
            ).limit(5).to_table_var(f"sq_{abs(hash(pf_code))}")

        subqueries = [subquery(c).select('*') for c in pf_codes]
        qry = reduce(lambda x, y: x.union(y), subqueries)
        df = qry.go()

        self.assertEqual(df.shape[0], 10)
        self.assertEqual(df.shape[1], 4)

    def test_lusid_view(self):
        portfolio = self.atlas.lusid_portfolio(
            effective_at=dt.datetime(2021, 4, 9),
            as_at=dt.datetime(2021, 4, 9)
        )
        qry = portfolio.select(
            portfolio.portfolio_code
        ).where(
            portfolio.portfolio_scope == 'Finbourne-Examples'
        )

        make_view = qry.setup_view(
            'Lusid.Portfolio.FbnExamplesPfCodes'
        )

        df1 = make_view.go()
        self.assertEqual(df1.shape[0], 7)
        self.assertEqual(df1.shape[1], 1)

        new_atlas = lm.get_atlas()
        self.assertTrue(hasattr(new_atlas, 'lusid_portfolio_fbnexamplespfcodes'),
                        msg='view is missing in regenerated atlas')
        view_def = new_atlas.lusid_portfolio_fbnexamplespfcodes()

        df2 = view_def.select('*').go()
        self.assertEqual(df2.shape[0], 7)
        self.assertEqual(df2.shape[1], 1)
