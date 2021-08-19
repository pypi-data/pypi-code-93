import pandas as pd, numpy as np
from dorianUtils.configFilesD import ConfigDashTagUnitTimestamp
from dorianUtils.configFilesD import ConfigDashRealTime
from dorianUtils.configFilesD import ConfigDashSpark
import subprocess as sp, os,re,glob, datetime as dt
from dateutil import parser
from scipy import linalg,integrate
pd.options.mode.chained_assignment = None  # default='warn'

class ConfigFilesSmallPower(ConfigDashTagUnitTimestamp):
    # ==========================================================================
    #                       INIT FUNCTIONS
    # ==========================================================================

    def __init__(self,folderPkl,folderFig=None,folderExport=None,encode='utf-8'):
        confFolder = os.path.dirname(os.path.realpath(__file__))+'/confFiles/'
        super().__init__(folderPkl,confFolder,folderFig=folderFig,folderExport=folderExport)
        self.dfPLC      = self.__buildPLC(ds=False)
        self.legendTags = pd.read_csv(confFolder + 'tagLegend.csv')
        self.powerGroups = pd.read_csv(confFolder +'powerGroups.csv',index_col=0)

    def __buildPLC(self,ds=True):
        if ds:return self.dfPLC[self.dfPLC.DATASCIENTISM==True]
        else : return self.dfPLC

    def removeMeteoDF(self,df):
        return df[~df.tag.str.contains('@SIS')]
    # ==============================================================================
    #                   basic functions for computation
    # ==============================================================================
    def get_randomListTags(self,n=5):
        import random
        allTags = self.getTagsTU('',ds=True)
        return [allTags[random.randint(0,len(allTags))] for k in range(n)]

    def integrateDFTag(self,df,tagname,timeWindow=60,formatted=1):
        dfres = df[df.Tag==tagname]
        if not formatted :
            dfres = self.formatRawDF(dfres)
        dfres = dfres.sort_values(by='timestamp')
        dfres.index=dfres.timestamp
        dfres=dfres.resample('100ms').ffill()
        dfres=dfres.resample(str(timeWindow) + 's').mean()
        dfres['Tag'] = tagname
        return dfres

    def integrateDF(self,df,pattern,**kwargs):
        ts = time.time()
        dfs = []
        listTags = self.getTagsTU(pattern[0],pattern[1])[self.tagCol]
        # print(listTags)
        for tag in listTags:
            dfs.append(self.integrateDFTag(df,tagname=tag,**kwargs))
        print('integration of pattern : ',pattern[0],' finished in ')
        self.utils.printCTime(ts)
        return pd.concat(dfs,axis=0)

    def getListTagsPower(self):
        return self.utils.flattenList([self.getTagsTU(self.powerGroups.loc[k].pattern) for k in self.powerGroups.index])

    def _categorizeTagsPerUnit(self,df):
        dfPLC1 = self.dfPLC[self.dfPLC.TAG.isin(df.columns)]
        unitGroups={}
        for u in dfPLC1.UNITE.unique():
            unitGroups[u]=list(dfPLC1[dfPLC1.UNITE==u].TAG)
        return unitGroups

    # ==============================================================================
    #                   computation functions
    # ==============================================================================
    def DF_allPower(self,timeRange,**kwargs):
        dfs=[]
        for group in self.powerGroups.index[:-1]:
            listTags=self.getTagsTU(self.powerGroups.loc[group].pattern)
            df = self.DF_loadTimeRangeTags(timeRange,listTags,**kwargs)
            if 'courant' in group.lower():
                df=df*self.powerGroups.loc[group].voltage
            df=df.abs()# take absolute value of the power
            df['timestamp'] = df.index
            df=df.melt(id_vars='timestamp',ignore_index=True)
            df['Power group'] = group
            dfs.append(df)

        dfPtotal = self.DF_loadTimeRangeTags(timeRange,self.getTagsTU('SEH0\.JT_01\.HE13'),**kwargs)
        dfPtotal = dfPtotal.ffill().bfill()
        df=pd.concat(dfs,axis=0)
        return df,dfPtotal

    def computeCosPhi(self,timeRange,pat='SEH0.JT_01',**kwargs):
        tagsPower = self.getTagsTU(pat)
        df        = self.DF_loadTimeRangeTags(timeRange,tagsPower)
        P=[k for k in tagsPower if 'HE10' in k]
        S=[k for k in tagsPower if 'HE16' in k]
        df['cosphi'] = df[P[0]]/df[S[0]]
        return df

    # ==============================================================================
    #                   plot functions
    # ==============================================================================
    def plotGraphPowerArea(self,timeRange,expand='groups',groupnorm='',**kwargs):
        import plotly.express as px
        import plotly.graph_objects as go
        # df,dfPtotal,dicPowerGroups = self.DF_allPower(timeRange,melt=True,**kwargs)
        df,dfPtotal = self.DF_allPower(timeRange,**kwargs)

        if expand=='tags' :fig=px.area(df,x='timestamp',y='value',color='tag',groupnorm=groupnorm)
        elif expand=='groups' :
            fig=px.area(df,x='timestamp',y='value',color='Power group',groupnorm=groupnorm,line_group='tag')
            fig.update_layout(legend=dict(orientation="h"))

        try:
            traceP=go.Scatter(x=dfPtotal.index,y=dfPtotal.iloc[:,0],name='SEH0.JT_01.HE16(puissance totale apparente)',mode='lines+markers',
                                    marker=dict(color='blue'))
            fig.add_trace(traceP)
        except:
            print('total power SEH0.JT_01.HE16 IS EMPTY' )

        return fig

    def updateLayoutMultiUnitGraph(self,fig,sizeDots=10):
        fig.update_yaxes(showgrid=False)
        fig.update_traces(marker=dict(size=sizeDots))
        fig.update_layout(height=900)
        fig.update_traces(hovertemplate='<b>%{y:.1f}')
        return fig

    def plotMultiUnitGraph(self,timeRange,listTags=[],**kwargs):
        if not listTags : listTags=self.get_randomListTags()
        tagMapping = {t:self.getUnitofTag(t) for t in listTags}
        df  = self.DF_loadTimeRangeTags(timeRange,listTags,**kwargs)
        return self.utils.multiUnitGraph(df,tagMapping)

    # ==============================================================================
    #                   fitting functions
    # ==============================================================================

    def prepareDFforFit(self,filename,ts=None,group='temperatures Stack 1',rs='30s'):
        df = self.loadFile(filename)
        a  = self.usefulTags[group]
        df = self.getDFTagsTU(df,a[0],a[1])
        df = self.pivotDF(df,resampleRate=rs)
        if not not ts :
            df= self.getDFTime(df,ts)
        return df

    def fitDataframe(self,df,func='expDown',plotYes=True,**kwargs):
        res = {}
        period = re.findall('\d',df.index.freqstr)[0]
        print(df.index[0].freqstr)
        for k,tagName in zip(range(len(df)),list(df.columns)):
             tmpRes = self.utils.fitSingle(df.iloc[:,[k]],func=func,**kwargs,plotYes=plotYes)
             res[tagName] = [tmpRes[0],tmpRes[1],tmpRes[2],
                            1/tmpRes[1]/float(period),tmpRes[0]+tmpRes[2]]
        res  = pd.DataFrame(res,index = ['a','b','c','tau(s)','T0'])
        return res

class ConfigFilesSmallPowerSpark(ConfigDashSpark):
    def __init__(self,sparkData,sparkConfFile,confFile=None,folderFig=None,folderExport=None,encode='utf-8'):
        self.appDir = os.path.dirname(os.path.realpath(__file__))
        if not confFile : confFile=glob.glob(self.appDir +'/confFiles/' + '*PLC*')[0]
        super().__init__(sparkData,sparkConfFile,confFile=confFile,folderFig=folderFig,folderExport=folderExport)
        self.usefulTags = pd.read_csv(self.appDir+'/confFiles/predefinedCategories.csv',index_col=0)
        self.dfPLC = self.__buildPLC()

    def __buildPLC(self):
        return self.dfPLC[self.dfPLC.DATASCIENTISM==True]

class AnalysisPerModule(ConfigFilesSmallPower):
    def __init__(self,folderPkl,folderFig=None,folderExport=None,encode='utf-8'):
        super().__init__(folderPkl,folderFig,folderExport,encode)
        self.modules=self._loadModules()
        self.listModules=list(self.modules.keys())

    def _buildEauProcess(self):
        eauProcess={}
        eauProcess['pompes']=['PMP_04','PMP_05']
        eauProcess['TNK01'] = ['L219','L221','L200','L205','GWPBC_TNK_01']
        eauProcess['pompe purge'] = ['GWPBC_PMP_01','L202','L210']
        eauProcess['toStack'] = ['L036','L020','GFD_01']
        return eauProcess

    def _buildGV(self):
        GV = {}
        GV['temperatures GV1a'] = ['STG_01a_TT']
        GV['commande GV1a'] = ['STG_01a_HER']
        GV['commande GV1b'] = ['STG_01b_HER']
        GV['ligne gv1a'] = ['L211','L213_H2OPa']
        GV['ligne gv1b'] = ['L211','L213_H2OPb']
        GV['temperatures GV1b'] = ['STG_01b_TT']
        return GV

    def _buildValo(self):
        Valo = {}
        Valo['amont-retour'] = ['GWPBC_PMP_02','L400','L416','L413']
        Valo['echangeur 1'] = ['HPB_HEX_01','L402','L114','L117']
        Valo['condenseur 1'] = ['HPB_CND_01','L408','L404','L021','L022']
        Valo['echangeur 2'] = ['HPB_HEX_02','L404','L115','L116']
        Valo['condenseur 2'] = ['HPB_CND_02','L406','L046','L045']
        Valo['batiment'] = ['GWPBC-HEX-01','L414','L415']
        return Valo

    def _buildGroupeFroid(self):
        groupFroid = {}
        groupFroid['groupe froid'] = ['HPB_CND_03','L417','L418','L056','L057']
        return groupFroid

    def _buildBalayage(self):
        Balayage = {}
        Balayage['echangeur'] = ['HTBA_HEX_01','L133','L134','L135','HPB_RD_01']
        Balayage['stack'] = ['STB_TT_01','STB_TT_02']
        Balayage['blowers'] = ['GWPBH_BLR','L136']
        Balayage['explosimetre'] = ['SFTB_AT_01']
        return Balayage

    def _buildStackBox(self):
        stackBox = {}
        stackBox['chauffants enceinte'] = ['SEH1.STB_HER']
        stackBox['chauffants stacks'] = ['SEH1.STB_STK_0[1-4]_HER']
        stackBox['stack 1'] = ['STB_STK_01']
        stackBox['stack 2'] = ['STB_STK_02']
        stackBox['stack 3'] = ['STB_STK_03']
        stackBox['stack 4'] = ['STB_STK_04']
        stackBox['debits'] = ['STB_GFD','STB_FUEL','STB_GFC','STB_GDC']
        return stackBox

    def _loadModules(self):
        modules = {}
        modules['eau process']=self._buildEauProcess()
        modules['GV']=self._buildGV()
        modules['groupe froid']=self._buildGroupeFroid()
        modules['valo']=self._buildValo()
        modules['balayage']=self._buildBalayage()
        modules['stackbox']=self._buildStackBox()
        return modules

    def _categorizeTagsPerUnit(self,module):
        '''module : {'eauProcess','groupe froid','GV','valo'...} given by self.listModules'''
        mod=self.modules[module]
        ll = self.utils.flattenList([self.listTagsModule(mod,g)[1] for g in mod])
        dfPLC1 = self.dfPLC[self.dfPLC.TAG.isin(ll)]
        unitGroups={}
        for u in dfPLC1.UNITE.unique():
            unitGroups[u]=list(dfPLC1[dfPLC1.UNITE==u].TAG)
        return unitGroups

    # ==========================================================================
    #                     functions prepare for graph
    # ==========================================================================

    def listTagsModule(self,module,group):
        groupList=module[group]
        lplc=pd.concat([self.getTagsTU(pat,ds=False,cols='tdu') for pat in groupList])
        lds=self.utils.flattenList([self.getTagsTU(pat,ds=True) for pat in groupList])
        return lplc,lds

    def listTagsAllModules(self,module,groups=[]):
        mod=self.modules[module]
        LPLC = {g:self.listTagsModule(mod,g)[0] for g in mod}
        LDS = {g:self.listTagsModule(mod,g)[1] for g in mod}
        return LPLC,LDS

    def getDictGroupUnit(self,module,groupsOfModule):
        dictdictGroups = {}
        allgroupsofModule = self.listTagsAllModules(module)[1]
        if not groupsOfModule:groupsOfModule=list(allgroupsofModule.keys())
        groupsOfModule={g:allgroupsofModule[g] for g in groupsOfModule}
        for group,listTags in groupsOfModule.items():
            dictdictGroups[group] = {t:self.utils.detectUnit(self.getUnitofTag(t)) + ' in ' + self.getUnitofTag(t) for t in listTags}

        listTags=self.utils.flattenList([v for v in groupsOfModule.values()])
        return dictdictGroups,listTags
    # ==========================================================================
    #                           GRAPH FUNCTIONS
    # ==========================================================================
    def figureModule(self,module,timeRange,groupsOfModule=None,axisSpace=0.04,hspace=0.02,vspace=0.1,colmap='jet',**kwargs):
        '''
        module : name of the module
        groupsOfModule : list of names of subgroups from the module
        '''
        dictdictGroups,listTags=self.getDictGroupUnit(module,groupsOfModule)
        df  = self.DF_loadTimeRangeTags(timeRange,listTags,**kwargs)
        fig = self.utils.multiUnitGraphSubPlots(df,dictdictGroups,
                        axisSpace=axisSpace,horizontal_spacing=hspace,vertical_spacing=vspace,colormap='jet',
                        subplot_titles=groupsOfModule)
        return fig

    def figureModuleUnits(self,module,timeRange,listUnits=[],grid=None,**kwargs):
        from plotly.subplots import make_subplots
        unitGroups=self._categorizeTagsPerUnit(module)
        if not listUnits: listUnits = list(unitGroups.keys())
        if not grid:grid=self.utils.optimalGrid(len(listUnits))
        fig = make_subplots(rows=grid[0], cols=grid[1],
                                vertical_spacing=0.01,horizontal_spacing=0.1,shared_xaxes=True)
        rows,cols=self.utils.rowsColsFromGrid(len(listUnits),grid)
        for k,r,c in zip(listUnits,rows,cols):
            print(k)
            listTags = unitGroups[k]
            df = self.DF_loadTimeRangeTags(timeRange,listTags,**kwargs)
            df=df.ffill().bfill()
            for l in df.columns:
                fig.add_scatter(y=df[l],x=df.index, mode="lines",
                                name=l, row=r, col=c)
            fig.update_yaxes(title_text=self.utils.detectUnit(k) + ' ( '+ k + ' ) ', row=r, col=c)
            # fig.update_yaxes(color='#FF0000')

        fig.update_xaxes(matches='x')
        fig.update_traces(hovertemplate='<b>%{y:.1f}',)
        fig.update_layout(title={"text": module})
        return fig

    def updateFigureModule(self,fig,module,groupsOfModule,hg,hs,vs,axSP,lgd=False):
        self.utils.printListArgs(module,groupsOfModule,hg,hs,vs,axSP)
        dictdictGroups = self.getDictGroupUnit(module,groupsOfModule)[0]
        figLayout = self.utils.getLayoutMultiUnitSubPlots(dictdictGroups,axisSpace=axSP,
                                                        horizontal_spacing=hs,vertical_spacing=vs)
        fig.layout = figLayout[0].layout
        fig.update_traces(marker=dict(size=5))
        fig.update_traces(hovertemplate='<b>%{y:.1f}')
        fig.update_yaxes(showgrid=False)
        fig.update_layout(height=hg)
        fig.update_layout(showlegend=lgd)
        fig.update_xaxes(matches='x')

        return fig

    def plotQuick(self,df,duration='short',title='',form='df'):
        df=df.ffill().bfill()
        if form=='step': plt.step(x=df.index,y=df.iloc[:,0],)
        if form=='multi': mpl.multiYmpl(df)
        if form=='df': df.plot(colormap='jet')
        datenums=md.date2num(df.index)
        if duration=='short': xfmt = md.DateFormatter('%H:%M')
        else: xfmt = md.DateFormatter('%b-%d')
        ax=plt.gca()
        plt.xticks( rotation=25 )
        # ax.xaxis.set_major_formatter(xfmt)
        # ax.set_ylabel('timestamp')
        mpl.plt.title(title)

class ConfigFilesSmallPower_RealTime(ConfigDashRealTime):
    # ==========================================================================
    #                       INIT FUNCTIONS
    # ==========================================================================

    def __init__(self,confFolder=None,connParameters=None,
                    folderFig=None,folderExport=None,encode='utf-8'):
        self.appDir  = os.path.dirname(os.path.realpath(__file__))
        if not connParameters : connParameters ={
            'host'     : "192.168.1.44",
            'port'     : "5434",
            'dbname'   : "Jules",
            'user'     : "postgres",
            'password' : "SylfenBDD"
        }
        if not confFolder:confFolder=self.appDir +'/confFiles/'
        ConfigDashRealTime.__init__(self,confFolder,connParameters)
