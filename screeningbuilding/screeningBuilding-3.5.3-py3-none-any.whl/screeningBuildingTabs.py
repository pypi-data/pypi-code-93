import datetime as dt, pickle, time
import os,re,pandas as pd
import dash, dash_core_components as dcc, dash_html_components as html, dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import plotly.express as px, plotly.graph_objects as go
from dorianUtils.dccExtendedD import DccExtended
from dorianUtils.utilsD import Utils
import screeningBuilding.configFilesBuilding as cfb
from dorianUtils.dashTabsD import TabSelectedTags,TabMultiUnits,TabDataTags,RealTimeTagSelectorTab,RealTimeTagMultiUnit

class ScreenBuildingTab():
    def __init__(self,app,baseId):
        self.baseId = baseId
        self.app    = app
        self.utils  = Utils()
        self.dccE   = DccExtended()
    # ==========================================================================
    #                           SHARED FUNCTIONS CALLBACKS
    # ==========================================================================
    def addWidgets(self,dicWidgets,baseId):
        widgetLayout,dicLayouts = [],{}
        for wid_key,wid_val in dicWidgets.items():
            if 'dd_computation' in wid_key:
                widgetObj = self.dccE.dropDownFromList(baseId+wid_key,self.computationGraphs,
                                                        'what should be computed ?',value = wid_val)

            for widObj in widgetObj:widgetLayout.append(widObj)

        return widgetLayout

class ComputationTab(ScreenBuildingTab,TabDataTags):
    def __init__(self,app,folderPkl,baseId='tc0_'):
        ScreenBuildingTab.__init__(self,app,baseId)
        self.tabname = 'computation'
        self.cfg = cfb.ConfigFilesBuilding(folderPkl)
        self.listCompteurs = [k.split('-')[1] for k in list(self.cfg.listCompteurs.Compteurs) if 'VIRTUAL' not in k]
        self.listCompute = ['power enveloppe','consumed energy','energyPeriodBarPlot']
        self.tabLayout  = self._buildLayout()
        self._define_callbacks()

    def _buildLayout(self,widthG=85):
        dicWidgets = {
            'pdr_time':{'tmax':'2021-06-05','tmin':'2021-06-01'},
            'block_resample':{'val_res':'60s','val_method' : 'mean'},
            'block_graphSettings':{'style':'lines+markers','type':'scatter','colmap':'jet'}
            }
        basicWidgets = self.dccE.basicComponents(dicWidgets,self.baseId)
        computeWid = self.dccE.dropDownFromList(self.baseId + 'dd_computation',
                    self.listCompute,'computation:',value='power enveloppe')
        compteurWid  = self.dccE.dropDownFromList(self.baseId + 'dd_compteur',
                        self.listCompteurs,'variables:',value='B001',multi=True)
        widgetLayout = basicWidgets + computeWid +compteurWid
        return self.dccE.buildGraphLayout(widgetLayout,self.baseId,widthG=widthG)

    def computeGraph(self,timeRange,computation,compteurs,rs):
        if not isinstance(compteurs,list):compteurs=[compteurs]
        if computation == 'power enveloppe' :
            df = self.cfg.computePowerEnveloppe(timeRange,compteur=compteurs[0],rs=rs)
            unit = 'kW'
            fig = px.scatter(df)
            # fig.update_layout(title=compteurs)
        elif computation == 'consumed energy' :
            fig= self.cfg.plot_compare_kwhCompteurvsPower(timeRange,compteurs,rs)
        elif computation == 'energyPeriodBarPlot' :
            if not compteurs:compteurs=self.listCompteurs
            fig = self.cfg.energyPeriodBarPlot(timeRange,compteurs=compteurs)
        return fig

    def _define_callbacks(self):
        @self.app.callback(
        Output(self.baseId + 'dd_compteur', 'multi'),
        Input(self.baseId + 'dd_computation', 'value'))
        def dynamicComputationdd(computation):
            if computation == 'power enveloppe' :
                return False
            else :
                return True


        listInputsGraph = {
                        'dd_compteur':'value',
                        'pdr_timeBtn':'n_clicks',
                        'dd_style':'value',
                        'dd_cmap':'value',
                        }
        listStatesGraph = {
                            'dd_computation':'value',
                            'graph':'figure',
                            'in_timeRes' : 'value',
                            'pdr_timeStart' : 'value',
                            'pdr_timeEnd':'value',
                            'pdr_timePdr':'start_date',
                            }
        @self.app.callback(
        Output(self.baseId + 'graph', 'figure'),
        Output(self.baseId + 'pdr_timeBtn', 'n_clicks'),
        [Input(self.baseId + k,v) for k,v in listInputsGraph.items()],
        [State(self.baseId + k,v) for k,v in listStatesGraph.items()],
        State(self.baseId+'pdr_timePdr','end_date'))
        def updateGraph(compteurs,timeBtn,style,cmap,cmp,fig,rs,date0,date1,t0,t1):
            ctx = dash.callback_context
            trigId = ctx.triggered[0]['prop_id'].split('.')[0]
            listTrig = ['dd_compteurs','pdr_timeBtn']
            if not timeBtn or trigId in [self.baseId+k for k in listTrig] :
                timeRange = [date0+' '+t0,date1+' '+t1]
                fig = self.computeGraph(timeRange,cmp,compteurs,rs)
            else :fig = go.Figure(fig)
            # fig.update_traces(mode=style)
            fig.update_layout(height=800)
            fig = self.utils.updateColorMap(fig,cmap)
            return fig,timeBtn

class TagSelectedScreeningBuilding(TabSelectedTags):
    def __init__(self,folderPkl,app,pklMeteo=None,baseId='tst0_'):
        self.cfg = cfb.ConfigFilesBuilding(folderPkl,pklMeteo=pklMeteo)
        TabSelectedTags.__init__(self,folderPkl,self.cfg,app,baseId)
        self._define_callbacks()

    def _buildLayout(self,widthG=85):
        dicWidgets = {'pdr_time' : {'tmin':self.cfg.listFilesPkl[0],'tmax':self.cfg.listFilesPkl[-1]},
                        'in_timeRes':'auto','dd_resampleMethod' : 'mean',
                        'dd_style':'lines+markers','dd_typeGraph':'scatter',
                        'dd_cmap':'jet','btn_export':0}
        basicWidgets = self.dccE.basicComponents(dicWidgets,self.baseId)
        specialWidgets = self.addWidgets({'dd_typeTags':'Puissances sls','btn_legend':0},self.baseId)
        # reodrer widgets
        widgetLayout = basicWidgets + specialWidgets
        return self.dccE.buildGraphLayout(widgetLayout,self.baseId,widthG=widthG)

class MultiUnitScreeningBuilding(TabMultiUnits):
    def __init__(self,folderPkl,app,baseId='mut0_'):
        self.cfg = cfb.ConfigFilesBuilding(folderPkl)
        TabMultiUnits.__init__(self,folderPkl,self.cfg,app,baseId)
        self.tabLayout = self._buildLayout(widthG=85,initialTags=self.cfg.getTagsTU('PV'))
        self._define_callbacks()

# ==============================================================================
#                                   REAL TIME
# ==============================================================================

class RealTimeTagScreeningBuildingSelectorTab(RealTimeTagSelectorTab):
    def __init__(self,app,connParameters=None,baseId='rttsb_'):
        self.cfg = cfb.ConfigFilesBuildingRealTime(connParameters=connParameters)
        RealTimeTagSelectorTab.__init__(self,app,connParameters,self.cfg,baseId=baseId)
        self.tabLayout = self._buildLayout(widthG=85,defaultCat='Puissances sls',
                        val_window=60*2,val_refresh=20,min_refresh=5,min_window=1)

class RealTimeScreeningBuildingMultiUnit(RealTimeTagMultiUnit):
    def __init__(self,app,connParameters=None,baseId='rtmsb_'):
        self.cfg = cfb.ConfigFilesBuildingRealTime(connParameters=connParameters)
        RealTimeTagMultiUnit.__init__(self,app,connParameters,self.cfg,baseId=baseId)
        defaultTags = self.cfg.getTagsTU('PV')
        self.tabLayout = self._buildLayout(widthG=85,defaultTags=defaultTags,
                        val_window=60*2,val_refresh=20,min_refresh=5,min_window=1)
