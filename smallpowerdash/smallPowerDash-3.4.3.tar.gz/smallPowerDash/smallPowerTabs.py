import datetime as dt, pickle, time, os,re,pandas as pd
import dash, dash_core_components as dcc, dash_html_components as html, dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import plotly.express as px, plotly.graph_objects as go
# import matplotlib.pyplot as plt, matplotlib.colors as mtpcl
# from pylab import cm
from dorianUtils.utilsD import Utils
from dorianUtils.dccExtendedD import DccExtended
from dorianUtils.dashTabsD import TabSelectedTags,TabMultiUnits,TabDataTags,RealTimeTagSelectorTab,RealTimeTagMultiUnit
from dorianUtils.dashTabsD import TabSelectedTags,TabUnitSelector,TabMultiUnits,TabDataTags
import smallPowerDash.configFilesSmallPower as cfs

class SmallPowerTab():
    def __init__(self,app,baseId):
        self.baseId=baseId
        self.app = app
        self.utils = Utils()
        self.dccE = DccExtended()

    def addWidgets(self,dicWidgets,baseId):
        widgetLayout,dicLayouts = [],{}
        for wid_key,wid_val in dicWidgets.items():
            if 'dd_computation' in wid_key:
                widgetObj = self.dccE.dropDownFromList(baseId+wid_key,self.computationGraphs,
                                                        'what should be computed ?',value = wid_val)


            elif 'dd_expand' in wid_key:
                widgetObj = self.dccE.dropDownFromList(baseId+wid_key,['groups','tags'],'Select the option : ',value = wid_val)

            elif 'dd_modules' in wid_key:
                widgetObj = self.dccE.dropDownFromList(baseId+wid_key,
                            list(self.cfg.modules.keys()),'Select your module: ',value = wid_val)

            elif 'dd_moduleGroup' in wid_key:
                widgetObj = self.dccE.dropDownFromList(baseId+wid_key,[],
                                'Select the graphs to display: ',value = 0,multi=True)
            elif 'check_unit' in wid_key:
                widgetObj = [dcc.Checklist(id=baseId+wid_key,options=[{'label': 'unit', 'value':'unit'}],value= wid_val)]

            for widObj in widgetObj:widgetLayout.append(widObj)

        return widgetLayout

# ==============================================================================
#                        POST-PROCESSING TABS
# ==============================================================================
class ComputationTab(SmallPowerTab):
    def __init__(self,folderPkl,app,baseId='ct0_'):
        super().__init__(app,baseId)
        self.cfg = cfs.ConfigFilesSmallPower(folderPkl)
        self.computationGraphs=['power repartition']
        self.tabLayout = self._buildComputeLayout()
        self.tabname = 'computation'
        self._define_callbacks()

    def plotGraphComputation(self,timeRange,computation,params):
        start     = time.time()
        if computation == 'power repartition' :
            fig = self.cfg.plotGraphPowerArea(timeRange,rs=params['rs'],applyMethod=params['method'],expand=params['expand'])
            fig.update_layout(yaxis_title='power in W')
        self.utils.printCTime(start,'computation time : ')
        return fig

    def _buildComputeLayout(self,widthG=85):
        dicWidgets = {'pdr_time' : {'tmin':self.cfg.listFilesPkl[0],'tmax':self.cfg.listFilesPkl[-1]},
                    'in_timeRes':str(60*10)+'s','dd_resampleMethod':'mean',
                    'dd_style':'lines+markers','dd_cmap':'jet','btn_export':0}
        basicWidgets = self.dccE.basicComponents(dicWidgets,self.baseId)
        specialWidgets = self.addWidgets({'dd_computation':'power repartition','dd_expand':'groups'},self.baseId)
        # reodrer widgets
        widgetLayout = basicWidgets + specialWidgets
        return self.dccE.buildGraphLayout(widgetLayout,self.baseId,widthG=widthG)

    def _define_callbacks(self):
        listInputsGraph = {
            'dd_computation':'value',
            'pdr_timeBtn':'n_clicks',
            'dd_resampleMethod' : 'value',
            'dd_expand' : 'value',
            'dd_cmap':'value',
            'dd_style':'value'
            }
        listStatesGraph = {
            'graph':'figure',
            'in_timeRes' : 'value',
            'pdr_timeStart' : 'value',
            'pdr_timeEnd':'value',
            'pdr_timePdr':'start_date',
                            }

        @self.app.callback(
        Output(self.baseId + 'graph', 'figure'),
        [Input(self.baseId + k,v) for k,v in listInputsGraph.items()],
        [State(self.baseId + k,v) for k,v in listStatesGraph.items()],
        State(self.baseId+'pdr_timePdr','end_date')
        )
        def updateGraph(computation,timeBtn,rsmethod,expand,colmap,style,fig,rs,date0,date1,t0,t1):
            ctx = dash.callback_context
            trigId = ctx.triggered[0]['prop_id'].split('.')[0]
            # to ensure that action on graphs only without computation do not
            # trigger computing the dataframe again
            triglist=['dd_computation','pdr_timeBtn','dd_typeGraph','dd_expand','dd_resampleMethod']
            if trigId in [self.baseId+k for k in triglist] :
                timeRange = [date0+' '+t0,date1+' '+t1]
                params,params['rs'],params['method'],params['expand']={},rs,rsmethod,expand
                fig   = self.plotGraphComputation(timeRange,computation,params)
            else :fig = go.Figure(fig)
            fig = self.utils.updateStyleGraph(fig,style,colmap)
            return fig

        @self.app.callback(
                Output(self.baseId + 'dl','data'),
                Input(self.baseId + 'btn_export', 'n_clicks'),
                State(self.baseId + 'graph','figure'),
                prevent_initial_call=True
                )
        def exportClick(btn,fig):
            df,filename =  self.utils.exportDataOnClick(fig)
            return dcc.send_data_frame(df.to_csv, filename+'.csv')

class ModuleTab(SmallPowerTab):
    def __init__(self,folderPkl,app,baseId='tmo0_',widthGraph=86):
        super().__init__(app,baseId)
        self.cfg = cfs.AnalysisPerModule(folderPkl)
        self.widthGraph = widthGraph
        self.tabLayout = self._buildModuleLayout()
        self.tabname = 'modules'
        self._define_callbacks()

    def _buildModuleLayout(self):
        dicWidgets = {
                    'pdr_time' : {'tmin':self.cfg.listFilesPkl[0],'tmax':self.cfg.listFilesPkl[-1]},
                    'in_timeRes':'auto','dd_resampleMethod':'mean',
                    'dd_style':'lines','dd_cmap':'prism',
                    'btn_export':0,
                    'block_multiAxisSettings':None
                    }
        basicWidgets = self.dccE.basicComponents(dicWidgets,self.baseId)
        specialWidgets = self.addWidgets({'check_unit':['unit'],'dd_modules':'GV','dd_moduleGroup':None},self.baseId)
        # reodrer widgets
        widgetLayout = basicWidgets + specialWidgets
        return self.dccE.buildGraphLayout(widgetLayout,self.baseId,widthG=self.widthGraph)

    def _define_callbacks(self):
        @self.app.callback(
        Output(self.baseId + 'dd_moduleGroup', 'options'),
        Input(self.baseId + 'dd_modules','value'),
        Input(self.baseId + 'check_unit','value'),
        )
        def updateGraph(module,unitGroup):
            if not unitGroup : l = self.cfg.listTagsAllModules(module)[1]
            else : l= list(self.cfg._categorizeTagsPerUnit(module).keys())
            options = [{'label':t,'value':t} for t in l]
            return options

        listInputsGraph = {
            'pdr_timeBtn':'n_clicks',
            'dd_resampleMethod' : 'value',
            'dd_cmap':'value',
            'dd_style':'value',
            'in_heightGraph':'value',
            'in_axisSp':'value',
            'in_hspace':'value',
            'in_vspace':'value',
            }
        listStatesGraph = {
            'graph':'figure',
            'dd_modules':'value',
            'check_unit':'value',
            'dd_moduleGroup':'value',
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
        def updateGraph(timeBtn,rsmethod,colmap,style,hg,axsp,hs,vs,fig,module,unitGroup,listGroups,rs,date0,date1,t0,t1):
            ctx = dash.callback_context
            trigId = ctx.triggered[0]['prop_id'].split('.')[0]
            # triggerList = ['dd_modules','dd_moduleGroup','pdr_timeBtn','dd_resampleMethod']
            triggerList = ['pdr_timeBtn','dd_resampleMethod']
            if not timeBtn or trigId in [self.baseId+k for k in triggerList] :
                timeRange = [date0+' '+t0,date1+' '+t1]
                if not unitGroup :
                    fig = self.cfg.figureModule(module,timeRange,groupsOfModule=listGroups,rs=rs,applyMethod=rsmethod)
                else :
                    fig = self.cfg.figureModuleUnits(module,timeRange,listUnits=listGroups,rs=rs,applyMethod=rsmethod)
            else :fig = go.Figure(fig)
            if not unitGroup :fig = self.cfg.updateFigureModule(fig,module,listGroups,hg,hs,vs,axsp)
            else : fig = fig.update_layout(height=hg)
            # fig = self.updateLegend(fig,lgd)
            return fig,timeBtn

        @self.app.callback(
        Output(self.baseId + 'btn_export','children'),
        Input(self.baseId + 'btn_export', 'n_clicks'),
        State(self.baseId + 'graph','figure'))
        def exportClick(btn,fig):
            fig = go.Figure(fig)
            if btn>0:self.utils.exportDataOnClick(fig,baseName='proof')
            return 'export Data'

class MultiUnitSmallPowerTab(TabMultiUnits):
    def __init__(self,folderPkl,app,baseId='mut0_'):
        self.cfg = cfs.ConfigFilesSmallPower(folderPkl)
        TabMultiUnits.__init__(self,folderPkl,self.cfg,app,baseId)
        defaultTags = self.cfg.getTagsTU('L03[26]')
        self.tabLayout = self._buildLayout(widthG=85,initialTags=defaultTags)
        self._define_callbacks()

class TagSelectedSmallPowerTab(TabSelectedTags):
    def __init__(self,folderPkl,app,baseId='tst0_'):
        self.cfg = cfs.ConfigFilesSmallPower(folderPkl)
        TabSelectedTags.__init__(self,folderPkl,self.cfg,app,baseId)
        self.tabLayout = self._buildLayout(widthG=84,tagCatDefault='Temperatures du gv1a')
        self._define_callbacks()

class UnitSelectorSmallPowerTab(TabUnitSelector):
    def __init__(self,folderPkl,app,baseId='tust0_'):
        self.cfg = cfs.ConfigFilesSmallPower(folderPkl)
        TabUnitSelector.__init__(self,folderPkl,self.cfg,app,baseId)
        self.tabLayout = self._buildLayout(widthG=87,unitInit='W AC',patTagInit='')
        self._define_callbacks()

# ==============================================================================
#                        REAL TIME TABS
# ==============================================================================
class RealTimeTagSmallPowerSelectorTab(RealTimeTagSelectorTab):
    def __init__(self,app,connParameters=None,baseId='rttsp_'):
        self.cfg = cfs.ConfigFilesSmallPower_RealTime(connParameters=connParameters)
        RealTimeTagSelectorTab.__init__(self,app,connParameters,self.cfg,baseId=baseId)
        self.tabLayout = self._buildLayout(widthG=85,defaultCat='Temperatures du gv1a',
                        val_window=60*2,val_refresh=20,min_refresh=5,min_window=1)

class RealTimeSmallPowerMultiUnit(RealTimeTagMultiUnit):
    def __init__(self,app,connParameters=None,baseId='rtmsp_'):
        self.cfg = cfs.ConfigFilesSmallPower_RealTime(connParameters=connParameters)
        RealTimeTagMultiUnit.__init__(self,app,connParameters,self.cfg,baseId=baseId)
        defaultTags = self.cfg.getTagsTU('L03[26]')
        self.tabLayout = self._buildLayout(widthG=85,defaultTags=defaultTags,
                        val_window=60*2,val_refresh=20,min_refresh=5,min_window=1)

# ==============================================================================
#                               autres
# ==============================================================================
class TempCosphiTab(TabDataTags):
    def __init__(self,folderPkl,app,baseId='ts0_'):
        self.cfg = cfs.ConfigFilesSmallPower(folderPkl)
        TabDataTags.__init__(self,folderPkl,cfg=self.cfg,app=app,baseId=baseId)
        self.tabname = 'cosphi'
        self.tabLayout = self._buildLayout()
        self._define_callbacks()

    def _buildLayout(self,widthG=85):
        dicWidgets = {'pdr_time' : {'tmin':self.cfg.listFilesPkl[0],'tmax':self.cfg.listFilesPkl[-1]},
                        'in_timeRes':'auto','dd_resampleMethod' : 'mean',
                        'btn_export':0}
        basicWidgets = self.dccE.basicComponents(dicWidgets,self.baseId)
        return self.dccE.buildGraphLayout(basicWidgets,self.baseId,widthG=widthG)

    def _define_callbacks(self):

        listInputsGraph = {
                        'pdr_timeBtn':'n_clicks',
                        'dd_resampleMethod':'value',
                        }
        listStatesGraph = {
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
        def updateGraph(timeBtn,rsMethod,fig,rs,date0,date1,t0,t1):
            ctx = dash.callback_context
            trigId = ctx.triggered[0]['prop_id'].split('.')[0]
            if not timeBtn or trigId in [self.baseId+k for k in ['pdr_timeBtn','dd_resampleMethod',]]:
                timeRange = [date0+' '+t0,date1+' '+t1]
                cosphi = self.cfg.computeCosPhi(timeRange)
                # print(cosphi)
                fig = px.scatter(cosphi['cosphi'])
                fig.update_traces(mode='lines+markers')
                fig.update_layout(height=900)
            return fig,timeBtn


        @self.app.callback(
                Output(self.baseId + 'btn_export','children'),
                Input(self.baseId + 'btn_export', 'n_clicks'),
                State(self.baseId + 'graph','figure')
                )
        def exportClick(btn,fig):
            if btn>1:
                self.utils.exportDataOnClick(fig)
            return 'export Data'
