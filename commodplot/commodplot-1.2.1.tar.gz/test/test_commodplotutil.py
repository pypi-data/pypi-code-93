import unittest
import plotly.express as px
import cufflinks as cf
from commodplot import commodplotutil as cpu
import os


class TestCommodPlotUtil(unittest.TestCase):

    def test_delta_summary_str(self):
        df = cf.datagen.lines(2,1000)
        col = df.columns[0]

        m1 = df.iloc[-1, 0]
        m2 = df.iloc[-2, 0]
        diff = m1 - m2
        res = cpu.delta_summary_str(df)

        self.assertIn(str(m1.round(2)), res)
        self.assertIn(str(diff.round(2)), res)

    def test_convert_dict_plotly_fig_html_div(self):
        df = px.data.gapminder().query("country=='Canada'")
        fig = px.line(df, x="year", y="lifeExp", title='Life expectancy in Canada')

        data = {}
        data['ch1'] = fig
        data['el'] = 1
        data['innerd'] = {}
        data['innerd']['ch2'] = fig

        res = cpu.convert_dict_plotly_fig_html_div(data)
        self.assertTrue(isinstance(res['ch1'], str))
        self.assertTrue(isinstance(res['innerd']['ch2'], str))

    def test_render_html(self):
        dirname, filename = os.path.split(os.path.abspath(__file__))
        test_out_loc = os.path.join(dirname, 'test.html')
        if os.path.exists(test_out_loc):
            os.remove(test_out_loc)

        data = { 'name' : 'test' }
        tfloc = os.path.join(os.path.join(os.path.join(dirname, os.pardir), 'templates'), 'base.html')
        f = cpu.render_html(data, tfloc, 'test.html')

        self.assertTrue(test_out_loc)
        if os.path.exists(test_out_loc):
            os.remove(test_out_loc)


if __name__ == '__main__':
    unittest.main()


