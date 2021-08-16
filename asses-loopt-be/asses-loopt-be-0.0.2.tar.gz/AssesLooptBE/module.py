import pandas as pd
from pandas.core.frame import DataFrame
from sklearn.metrics import confusion_matrix


class assesLooptBE:

    def __init__(self, dataframe_assessment):
        self.results_assessment = {}
        self.dataframe_assessment = dataframe_assessment.copy()
        self.organizacao_dataframe()
        self.acertos_medios_porcentagem(self, False)
        self.acertos_medios_pol(self, False)
        self.acertos_medios_porcentagem_embarques(self, False)
        self.acerto_variacao_porcentagem_fe_bookado(self, False)
        self.acerto_variacao_porcentagem_predict_bookado(self, False)
        self.acertos_medios_porcentagem_day(self, False)
        self.acertos_medios_porcentagem_embarque_day(self, False)
        self.matriz_confusao(self, False)
        self.distribuicoes(self, False)
    
    def organizacao_dataframe(self):
        # ===== criando colunas de erro_predict, erro_predict%, erro_book, erro_book% ======== #
        
        # erro_predict = valor absoluto da diferença entre previsto e embarcado
        self.dataframe_assessment['erro_predict'] = abs(self.dataframe_assessment['embarcado'] - self.dataframe_assessment['predict'])
        
        # erro_predict% = erro absoluto dividido pelo valor embarcado
        # Como convenção essa divisão pode gerar valores infinitos e NAN; Os valores NAN´s são gerados pela divisão 0/0 e deverão ser substituidos por um erro de 0% (Fillna(0)); /n
        # ; Já os valores infinitos são gerados pela divisão x/0 e deverão ser substituidos por um erro de 100%.
        self.dataframe_assessment['erro_predict%'] = ((self.dataframe_assessment['erro_predict']/self.dataframe_assessment['embarcado']).fillna(0))*100
        self.dataframe_assessment.loc[self.dataframe_assessment['erro_predict%'] >=1000, 'erro_predict%'] = 100   
        
        # erro_bookado = valor absoluto da diferença entre bookado e embarcado
        self.dataframe_assessment['erro_bookado'] = abs(self.dataframe_assessment['embarcado'] - self.dataframe_assessment['reference_day0'])
        
        # erro_bookado% = erro absoluto dividido pelo valor embarcado
        self.dataframe_assessment['erro_bookado%'] = (((self.dataframe_assessment['erro_bookado']/self.dataframe_assessment['embarcado'])).fillna(0))*100 
        self.dataframe_assessment.loc[self.dataframe_assessment['erro_bookado%'] >=1000, 'erro_bookado%'] = 100
    
        # Valores de variação entre embarcado e bookado
        self.dataframe_assessment['variacao_embarcado_book'] = self.dataframe_assessment['embarcado']  - self.dataframe_assessment['reference_day0']
    
        # Valores de variação entre predict e bookado
        self.dataframe_assessment['variacao_predict_book'] = self.dataframe_assessment['predict']  - self.dataframe_assessment['reference_day0']
    
    def acertos_medios_porcentagem(self, _return = True):
        # acerto_medio = acerto em relação a previsão
        self.results_assessment['acerto_medio_predict%'] = round(
            100 - self.dataframe_assessment['erro_predict%'].mean(), 1
        ) # Acerto = 100 - erro

        self.results_assessment['acerto_medio_predict_ponderado%'] = round(
            100 - ((self.dataframe_assessment['erro_predict%'] * self.dataframe_assessment['embarcado']).sum()/self.dataframe_assessment['embarcado'].sum()),1
        ) # Acerto ponderado segue a fórmula da média ponderada (Containers = pesos da formula)

        # acerto_medio_bookado = parametro_medio = acerto em relação ao bookado
        self.results_assessment['acerto_medio_bookado%'] = round(
            (100 - self.dataframe_assessment['erro_bookado%'].mean()), 1
        )
        self.results_assessment['acerto_medio_bookado_ponderado%'] = round(
            100- ((self.dataframe_assessment['erro_bookado%'] * self.dataframe_assessment['embarcado']).sum()/self.dataframe_assessment['embarcado'].sum()), 1
        )
        if _return:
            return self.results_assessment

    def acertos_medios_pol(self, _return = True):
        self.results_assessment['acerto_medio_pol'] = self.dataframe_assessment.groupby(['pol'])['reference_day0', 'embarcado', 'predict', 'erro_predict%', 'erro_bookado%'].mean()
        self.results_assessment['acerto_medio_pol']['erro_predict%'] = 100 - self.self.results_assessment['acerto_medio_pol']['erro_predict%']
        self.results_assessment['acerto_medio_pol']['erro_bookado%'] = 100 - self.self.results_assessment['acerto_medio_pol']['erro_bookado%']
        self.results_assessment['acerto_medio_pol'] = self.results_assessment['acerto_medio_pol'].rename(columns={'erro_predict%': 'acerto_medio_predict_pol%',
                                                                                                     'erro_bookado%':'acerto_medio_bookado_pol%'
                                                                                                   })
    
        if _return:
            return self.results_assessment['acerto_medio_pol']

    def acertos_medios_porcentagem_embarques(self, _return = True):
        dataframe_assessment_agrupado = pd.DataFrame()

        dataframe_assessment_agrupado_embarcado = self.dataframe_assessment.groupby(['voyage_cod', 'pol'])['reference_day0', 'embarcado', 'predict'].sum()
        dataframe_assessment_agrupado_embarcado['erro_predict'] = abs(dataframe_assessment_agrupado_embarcado['embarcado'] - dataframe_assessment_agrupado['predict'])
        dataframe_assessment_agrupado_embarcado['erro_predict%'] = (dataframe_assessment_agrupado_embarcado['erro_predict']/dataframe_assessment_agrupado['embarcado'])*100
        dataframe_assessment_agrupado_embarcado['erro_bookado'] = abs(dataframe_assessment_agrupado_embarcado['embarcado'] - dataframe_assessment_agrupado['reference_day0'])
        dataframe_assessment_agrupado_embarcado['erro_bookado%'] = (dataframe_assessment_agrupado_embarcado['erro_bookado']/dataframe_assessment_agrupado['embarcado'])*100

        self.results_assessment['acerto_medio_embarque_predict%'] = round((100 - dataframe_assessment_agrupado_embarcado['erro_predict%'].mean()), 1)
        self.results_assessment['acerto_medio_embarque_predict_ponderado%'] = round(100- ((dataframe_assessment_agrupado_embarcado['erro_predict%']*dataframe_assessment_agrupado_embarcado['embarcado']).sum()/dataframe_assessment_agrupado['embarcado'].sum()), 1)
        self.results_assessment['acerto_medio_embarque_bookado%'] = round((100 - dataframe_assessment_agrupado_embarcado['erro_bookado%'].mean()), 1)
        self.results_assessment['acerto_medio_embarque_bookado_ponderado%'] = round(100- ((dataframe_assessment_agrupado_embarcado['erro_bookado%']*dataframe_assessment_agrupado_embarcado['embarcado']).sum()/dataframe_assessment_agrupado['embarcado'].sum()), 1)

        if _return:
            return self.results_assessment

    def acerto_variacao_porcentagem_fe_bookado(self, _return = True):
        # Embarcado e Bookado 
        # Constante
        constante_embarcado_book = self.dataframe_assessment[self.dataframe_assessment['variacao_embarcado_book'] == 0]
        self.results_assessment['acerto_embarcado_bookado_constante'] = round((100 - constante_embarcado_book['erro_predict%'].mean()), 1)
        self.results_assessment['acerto_embarcado_bookado_constante_pond'] = round((100 -((constante_embarcado_book['erro_predict%']*constante_embarcado_book['embarcado']).sum()/constante_embarcado_book['embarcado'].sum())), 1)
        # Queda
        queda_embarcado_book = self.dataframe_assessment[self.dataframe_assessment['variacao_embarcado_book'] < 0]
        self.results_assessment['acerto_embarcado_bookado_queda'] = round((100 - queda_embarcado_book['erro_predict%'].mean()), 1)
        self.results_assessment['acerto_embarcado_bookado_queda_pond'] = round((100 -((queda_embarcado_book['erro_predict%']*queda_embarcado_book['embarcado']).sum()/queda_embarcado_book['embarcado'].sum())), 1)
        # Aumento
        aumento_embarcado_book = self.dataframe_assessment[self.dataframe_assessment['variacao_embarcado_book'] > 0]
        self.results_assessment['acerto_embarcado_bookado_aumento'] = round((100 - aumento_embarcado_book['erro_predict%'].mean()), 1)
        self.results_assessment['acerto_embarcado_bookado_aumento_pond'] = round((100 -((aumento_embarcado_book['erro_predict%']*aumento_embarcado_book['embarcado']).sum()/aumento_embarcado_book['embarcado'].sum())), 1)

        if _return:
            return self.results_assessment

    def acerto_variacao_porcentagem_predict_bookado(self, _return = True): 
        # Previsto e Bookado
        # Constante
        constante_predict_book = self.dataframe_assessment[self.dataframe_assessment['variacao_predict_book'] == 0]
        self.results_assessment['acerto_predict_bookado_constante'] = round((100 - constante_predict_book['erro_predict%'].mean()), 1)
        self.results_assessment['acerto_predict_bookado_constante_pond'] = round((100 -((constante_predict_book['erro_predict%']*constante_predict_book['embarcado']).sum()/constante_predict_book['embarcado'].sum())), 1)
        # Queda
        queda_predict_book = self.dataframe_assessment[self.dataframe_assessment['variacao_predict_book'] < 0]
        self.results_assessment['acerto_predict_bookado_queda'] = round((100 - queda_predict_book['erro_predict%'].mean()), 1)
        self.results_assessment['acerto_predict_bookado_queda_pond'] = round((100 -((queda_predict_book['erro_predict%']*queda_predict_book['embarcado']).sum()/queda_predict_book['embarcado'].sum())), 1)
        # Aumento
        aumento_predict_book = self.dataframe_assessment[self.dataframe_assessment['variacao_predict_book'] > 0]
        self.results_assessment['acerto_predict_bookado_aumento'] = round((100 - aumento_predict_book['erro_predict%'].mean()), 1)
        self.results_assessment['acerto_predict_bookado_aumento_pond'] = round((100 -((aumento_predict_book['erro_predict%']*aumento_predict_book['embarcado']).sum()/aumento_predict_book['embarcado'].sum())), 1)

        if _return:
            return self.results_assessment

    
    def acertos_medios_porcentagem_day(self, _return = True):
        self.results_assessment['acerto_medio_day'] = self.dataframe_assessment.groupby(['day_atual'])['erro_predict','erro_bookado','erro_predict%','erro_bookado%'].mean()
        self.results_assessment['acerto_medio_day']['erro_predict%'] = 100 - self.results_assessment['acerto_medio_day']['erro_predict%']
        self.results_assessment['acerto_medio_day']['erro_bookado%'] = 100 - self.results_assessment['acerto_medio_day']['erro_bookado%']
        self.results_assessment['acerto_medio_day'] = self.results_assessment['acerto_medio_day'].rename(columns={'erro_predict%': 'acerto_medio_predict_day%',
                                                                                                         'erro_bookado%':'acerto_medio_bookado_day%'
                                                                                                       })

        if _return:
            return self.results_assessment['acerto_medio_day']
    
    def acertos_medios_porcentagem_embarque_day(self, _return = True):
        dataframe_assessment_agrupado_embarcado_day = pd.DataFrame()

        dataframe_assessment_agrupado_embarcado_day = self.dataframe_assessment.groupby(['day_atual', 'voyage_cod'])['reference_day0', 'embarcado', 'predict'].sum()
        dataframe_assessment_agrupado_embarcado_day['erro_predict'] = abs(dataframe_assessment_agrupado_embarcado_day['embarcado'] - dataframe_assessment_agrupado_embarcado_day['predict'])
        dataframe_assessment_agrupado_embarcado_day['erro_predict%'] = (dataframe_assessment_agrupado_embarcado_day['erro_predict']/dataframe_assessment_agrupado_embarcado_day['embarcado'])*100
        dataframe_assessment_agrupado_embarcado_day['erro_bookado'] = abs(dataframe_assessment_agrupado_embarcado_day['embarcado'] - dataframe_assessment_agrupado_embarcado_day['reference_day0'])
        dataframe_assessment_agrupado_embarcado_day['erro_bookado%'] = (dataframe_assessment_agrupado_embarcado_day['erro_bookado']/dataframe_assessment_agrupado_embarcado_day['embarcado'])*100

        self.results_assessment['acerto_medio_embarque_day_predict%'] = round((100 - dataframe_assessment_agrupado_embarcado_day['erro_predict%'].mean()), 1)
        self.results_assessment['acerto_medio_embarque_day_predict_ponderado%'] = round(100- ((dataframe_assessment_agrupado_embarcado_day['erro_predict%']*dataframe_assessment_agrupado_embarcado_day['embarcado']).sum()/dataframe_assessment_agrupado_embarcado_day['embarcado'].sum()), 1)
        self.results_assessment['acerto_medio_embarque_day_bookado%'] = round((100 - dataframe_assessment_agrupado_embarcado_day['erro_bookado%'].mean()), 1)
        self.results_assessment['acerto_medio_embarque_day_bookado_ponderado%'] = round(100- ((dataframe_assessment_agrupado_embarcado_day['erro_bookado%']*dataframe_assessment_agrupado_embarcado_day['embarcado']).sum()/dataframe_assessment_agrupado_embarcado_day['embarcado'].sum()), 1)
        
        if _return:
            return self.results_assessment

    def matriz_confusao(self, _return = True):
        self.results_assessment['matriz_confusao'] = confusion_matrix(self.dataframe_assessment['embarcado'], self.dataframe_assessment['predict'])
        self.results_assessment['matriz_confusao'] = pd.DataFrame(self.results_assessment['matriz_confusao'])
        
        if _return:
            return self.results_assessment['matriz_confusao']

    def distribuicoes(self, _return = True):
        self.results_assessment['distribuicao_valores_embarcados_porcentagem'] = ((self.dataframe_assessment['embarcado'].value_counts()/self.dataframe_assessment['embarcado'].value_counts().sum())*100)
        self.results_assessment['distribuicao_valores_previstos_porcentagem'] = ((self.dataframe_assessment['predict'].value_counts()/self.dataframe_assessment['predict'].value_counts().sum())*100)
        self.results_assessment['distribuicao_erros_porcentagem'] = (((self.dataframe_assessment['erro_predict'].value_counts())/self.dataframe_assessment['erro_predict'].value_counts().sum())*100)
        self.results_assessment['distribuicao_erros_absolutos'] = self.dataframe_assessment['erro_predict'].value_counts()
        
        if _return:
            return self.results_assessment

    def help(self):
        print('''
            Input: Dataframe\n
            \n
            ==>Columns<==\n
            \n
            predict (Valor previsto; Ex: 2)\n
            embarcado (Valor embarcado; Ex: 2)\n
            reference_day0 (Valor bookado; Ex: 2)\n
            day_atual (Dia referencia da linha; Ex: DAY2)\n
            pol (porto de origem; Ex: BRMAO)\n
            voyage_cod (viagem do navio; Ex: )\n
        ''')
        
    def get_results(self):
        return self.results_assessment
