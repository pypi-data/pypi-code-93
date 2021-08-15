from django.views.generic import View

from sentry.charts import generate_chart
from sentry.charts.types import ChartType
from sentry.web.helpers import render_to_response

discover_total_period = {
    "seriesName": "Discover total period",
    "stats": {
        "data": [
            [1616168400, [{"count": 0}]],
            [1616168700, [{"count": 12}]],
            [1616169000, [{"count": 13}]],
            [1616169300, [{"count": 9}]],
            [1616169600, [{"count": 12}]],
            [1616169900, [{"count": 21}]],
            [1616170200, [{"count": 11}]],
            [1616170500, [{"count": 22}]],
            [1616170800, [{"count": 18}]],
            [1616171100, [{"count": 15}]],
            [1616171400, [{"count": 14}]],
            [1616171700, [{"count": 31}]],
            [1616172000, [{"count": 18}]],
            [1616172300, [{"count": 13}]],
            [1616172600, [{"count": 17}]],
            [1616172900, [{"count": 9}]],
            [1616173200, [{"count": 9}]],
            [1616173500, [{"count": 13}]],
            [1616173800, [{"count": 11}]],
        ],
    },
}

discover_total_daily = {
    "seriesName": "Discover total daily",
    "stats": {
        "data": [
            [1615852800, [{"count": 2426486}]],
            [1615939200, [{"count": 18837228}]],
            [1616025600, [{"count": 14662530}]],
            [1616112000, [{"count": 15102981}]],
            [1616198400, [{"count": 7759228}]],
            [1616284800, [{"count": 7216556}]],
            [1616371200, [{"count": 16976035}]],
            [1616457600, [{"count": 17240832}]],
            [1616544000, [{"count": 16814701}]],
            [1616630400, [{"count": 17480989}]],
            [1616716800, [{"count": 15387478}]],
            [1616803200, [{"count": 8467454}]],
            [1616889600, [{"count": 6382678}]],
            [1616976000, [{"count": 16842851}]],
            [1617062400, [{"count": 12959057}]],
        ],
    },
}

discover_top5 = {
    "stats": {
        "ludic-science,1st event": {
            "data": [
                [1615877940, [{"count": 0}]],
                [1615878000, [{"count": 0}]],
                [1615878060, [{"count": 0}]],
                [1615878120, [{"count": 0}]],
                [1615878180, [{"count": 1}]],
                [1615878240, [{"count": 1}]],
                [1615878300, [{"count": 1}]],
                [1615878360, [{"count": 1}]],
                [1615878420, [{"count": 1}]],
                [1615878480, [{"count": 1}]],
                [1615878540, [{"count": 1}]],
                [1615878600, [{"count": 3}]],
                [1615878660, [{"count": 1}]],
                [1615878720, [{"count": 1}]],
                [1615878780, [{"count": 1}]],
                [1615878840, [{"count": 1}]],
                [1615878900, [{"count": 1}]],
                [1615878960, [{"count": 1}]],
                [1615879020, [{"count": 1}]],
                [1615879080, [{"count": 1}]],
                [1615879140, [{"count": 1}]],
                [1615879200, [{"count": 1}]],
                [1615879260, [{"count": 1}]],
                [1615879320, [{"count": 1}]],
                [1615879380, [{"count": 0}]],
                [1615879440, [{"count": 0}]],
                [1615879500, [{"count": 0}]],
                [1615879560, [{"count": 0}]],
                [1615879620, [{"count": 0}]],
            ],
            "order": 0,
        },
        "ludic-science,2nd event": {
            "data": [
                [1615877940, [{"count": 0}]],
                [1615878000, [{"count": 0}]],
                [1615878060, [{"count": 0}]],
                [1615878120, [{"count": 0}]],
                [1615878180, [{"count": 1}]],
                [1615878240, [{"count": 1}]],
                [1615878300, [{"count": 1}]],
                [1615878360, [{"count": 1}]],
                [1615878420, [{"count": 1}]],
                [1615878480, [{"count": 1}]],
                [1615878540, [{"count": 1}]],
                [1615878600, [{"count": 5}]],
                [1615878660, [{"count": 3}]],
                [1615878720, [{"count": 2}]],
                [1615878780, [{"count": 1}]],
                [1615878840, [{"count": 1}]],
                [1615878900, [{"count": 1}]],
                [1615878960, [{"count": 1}]],
                [1615879020, [{"count": 1}]],
                [1615879080, [{"count": 1}]],
                [1615879140, [{"count": 1}]],
                [1615879200, [{"count": 1}]],
                [1615879260, [{"count": 1}]],
                [1615879320, [{"count": 1}]],
                [1615879380, [{"count": 0}]],
                [1615879440, [{"count": 0}]],
                [1615879500, [{"count": 0}]],
                [1615879560, [{"count": 0}]],
                [1615879620, [{"count": 0}]],
            ],
            "order": 1,
        },
    }
}

discover_empty = {
    "seriesName": "Discover empty",
    "stats": {
        "data": [],
    },
}


class DebugChartRendererView(View):
    def get(self, request):
        charts = []

        charts.append(generate_chart(ChartType.SLACK_DISCOVER_TOTAL_PERIOD, discover_total_period))
        charts.append(generate_chart(ChartType.SLACK_DISCOVER_TOTAL_PERIOD, discover_empty))
        charts.append(generate_chart(ChartType.SLACK_DISCOVER_TOTAL_DAILY, discover_total_daily))
        charts.append(generate_chart(ChartType.SLACK_DISCOVER_TOTAL_DAILY, discover_empty))
        charts.append(generate_chart(ChartType.SLACK_DISCOVER_TOP5_PERIOD, discover_top5))
        charts.append(generate_chart(ChartType.SLACK_DISCOVER_TOP5_PERIOD, discover_empty))
        charts.append(generate_chart(ChartType.SLACK_DISCOVER_TOP5_DAILY, discover_top5))
        charts.append(generate_chart(ChartType.SLACK_DISCOVER_TOP5_DAILY, discover_empty))

        return render_to_response("sentry/debug/chart-renderer.html", context={"charts": charts})
