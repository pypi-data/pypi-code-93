import importlib
import dash, dash_core_components as dcc, dash_html_components as html, dash_bootstrap_components as dbc
import dorianUtils.dccExtendedD as dcce
import smallPowerDash.smallPowerTabs as sptabs
from dash.dependencies import Input, Output, State

# ==============================================================================
#                       INSTANCIATIONS
# ==============================================================================
connParameters ={
'host'     : "192.168.1.44",
'port'     : "5434",
'dbname'   : "Jules",
'user'     : "postgres",
'password' : "SylfenBDD"
}

dccE=dcce.DccExtended()
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP],title='RealTime SmallPower',
                                                        url_base_pathname = '/smallPowerRealTime/')

tabSelectedTagsRT = sptabs.RealTimeTagSmallPowerSelectorTab(app,connParameters=connParameters)
tabMultiUnitRT = sptabs.RealTimeSmallPowerMultiUnit(app,connParameters=connParameters)
tabsLayout= dccE.createTabs([tabSelectedTagsRT])
mdFile = tabMultiUnits.cfg.confFolder + '/logVersionSmallPowerRT.md'
logModal = dccE.buildModalLog('Real Time Small Power V3.4(development version)',mdFile)

# tabsLayout= dccE.createTabs([tabSelectedTags,tabMultiUnits])
tabsLayout= dccE.createTabs([tabMultiUnitRT])
app.layout = html.Div([html.Div(logModal),html.Div(tabsLayout)])
@app.callback(
    Output("log_modal", "is_open"),
    [Input("btn_log", "n_clicks"), Input("close", "n_clicks")],
    [State("log_modal", "is_open")],
)
def showLog(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

# app.run_server(port=45000,debug=False,host='0.0.0.0')
app.run_server(port=45003,debug=True)
