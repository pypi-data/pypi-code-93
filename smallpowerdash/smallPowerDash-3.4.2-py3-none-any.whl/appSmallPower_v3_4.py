import importlib
import dash, dash_core_components as dcc, dash_html_components as html, dash_bootstrap_components as dbc
import dorianUtils.dccExtendedD as dcce
import smallPowerDash.smallPowerTabs as sptabs
from dash.dependencies import Input, Output, State

baseFolder   = '/home/dorian/data/sylfenData/'

# ==============================================================================
#                       INSTANCIATIONS
# ==============================================================================
folderPkl  = baseFolder + 'smallPower_pkl/'

dccE=dcce.DccExtended()

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP],
                title='small power explorer',url_base_pathname = '/smallPowerDash/')

# tabSelectedTags = sptabs.TagSelectedSmallPowerTab(folderPkl,app,baseId='ts_')
# tabModule       = sptabs.ModuleTab(folderPkl,app,baseId='mt_')
# tabMultiUnits   = sptabs.MultiUnitSmallPowerTab(folderPkl,app,baseId='mu_')
tabCompute      = sptabs.ComputationTab(folderPkl,app,baseId='ct_')
# tabUnitSelector = sptabs.UnitSelectorSmallPowerTab(folderPkl,app,baseId='ut_')

mdFile = tabCompute.cfg.confFolder + '/logVersionSmallPower.md'
logModal = dccE.buildModalLog('Small Power V3.4(development version)',mdFile)

# tabsLayout= dccE.createTabs([tabSelectedTags,tabMultiUnits,tabCompute,tabModule,tabUnitSelector])
tabsLayout= dccE.createTabs([tabCompute])
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
app.run_server(port=45002,debug=True)
