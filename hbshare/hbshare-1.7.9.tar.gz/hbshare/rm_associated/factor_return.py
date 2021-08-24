#!/usr/bin/python
#coding:utf-8
import pandas as pd
from sqlalchemy import create_engine
from hbshare.rm_associated.config import engine_params, style_names, industry_names
from datetime import datetime
import pyecharts.options as opts
from pyecharts.charts import Line
from pyecharts.globals import ThemeType


class RiskFactorReturn:
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        self._load_data()

    def _load_data(self):
        sql_script = "SELECT * FROM factor_return where TRADE_DATE >= {} and TRADE_DATE <= {}".format(
            self.start_date, self.end_date)
        engine = create_engine(engine_params)
        factor_return = pd.read_sql(sql_script, engine)
        factor_return['trade_date'] = factor_return['trade_date'].apply(lambda x: datetime.strftime(x, '%Y%m%d'))
        factor_return = pd.pivot_table(
            factor_return, index='trade_date', columns='factor_name', values='factor_ret').sort_index()
        factor_return = factor_return[style_names + list(industry_names.values()) + ['country']]

        self.factor_return = factor_return

    def generate_trendency_line(self, title):
        factor_return = self.factor_return.copy()
        factor_return = factor_return.cumsum()[style_names] * 100
        cum_line = Line(
            init_opts=opts.InitOpts(
                page_title=title,
                width='1200px',
                height='600px',
                theme=ThemeType.WALDEN
            )
        ).set_global_opts(
            title_opts=opts.TitleOpts(title=title),
            legend_opts=opts.LegendOpts(legend_icon='pin', pos_top='5%'),
            xaxis_opts=opts.AxisOpts(
                type_="category",
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
                axisline_opts=opts.AxisLineOpts(on_zero_axis_index=False),
            ),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                min_interval=0.1,
                name='Cumulative Performance(%)',
                name_location='middle',
                name_gap=45,
                name_textstyle_opts=opts.TextStyleOpts(font_size=16),
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
        ).add_xaxis(
            xaxis_data=factor_return.index.tolist()
        )

        for style_factor in style_names:
            cum_line.add_yaxis(
                series_name=style_factor,
                y_axis=factor_return[style_factor].round(4).tolist(),
                label_opts=opts.LabelOpts(is_show=False)
            )

        cum_line.render()


if __name__ == '__main__':
    RiskFactorReturn('20210104', '20210310').generate_trendency_line(
        title="Style Factor Performance From {} To {}".format('20210104', '20210310'))

