import re
from os import environ

class Enunciado:

    @staticmethod
    def pega_enunciado():
        print('Cole aqui o enunciado da questão.\n')
        if 'COLAB_GPU' in environ:
            enunciado = input().upper()
        else:
            enunciado = []
            entrada = None
            while entrada != '':
                entrada = input()
                enunciado.append(entrada)
            enunciado = Enunciado.trata_enunciado(enunciado)
            
        return enunciado
    
    @staticmethod
    def trata_enunciado(lista_enunciado):
        enunciado_tratado = ''
        for periodo in lista_enunciado:
            periodo = periodo.replace('\n', '')
            enunciado_tratado += periodo + ' '

        enunciado_tratado = enunciado_tratado.replace('  ', ' ')

        return enunciado_tratado.upper()
    
    @staticmethod
    def acha_classe_central(enunciado):
        try:
            padrao_1 = 'CENTRAL É DE MADEIRA C[0-9]{2}'
            
            classe_central = re.search(padrao_1, enunciado).group()[-3:]
            return classe_central
        
        except:
            return None
        
    @staticmethod
    def acha_espessura_central(enunciado):
        try:
            padrao_1 = 'COM ESPESSURA T=[0-9]{2} MM'
            
            espessura_central = re.search(padrao_1, enunciado).group()[-5:-3]
            return espessura_central
        except:
            return None
        
    @staticmethod
    def acha_classe_lateral(enunciado):
        try:
            padrao_1 = 'LATERAIS DE MADEIRA C[0-9]{2}'
            
            classe_lateral = re.search(padrao_1, enunciado).group()[-3:]
            return classe_lateral
        
        except:
            return None
        
    @staticmethod
    def acha_espessura_lateral(enunciado):
        try:
            padrao_1 = 'COM ESPESSURA DE [0-9]{2} MM'
            
            espessura_lateral = re.search(padrao_1, enunciado).group()[-5:-3]
            return espessura_lateral
        except:
            return None
        
    @staticmethod
    def acha_escoamento_aco(enunciado):
        try:
            padrao_1 = 'FYK = 700'
        
            escoamento_aco = re.search(padrao_1, enunciado).group()[-3:]
            return escoamento_aco
        except:
            return None
        
    @staticmethod
    def acha_duracao(enunciado):
        try:
            padrao_1 = 'EMPREGAR CARGA DE [A-Z]{5}'
            
            duracao = re.search(padrao_1, enunciado).group()[-5:]
            return duracao
        except:
            return None
        
    @staticmethod
    def acha_umidade(enunciado):
        try:
            padrao = 'UMIDADE AMBIENTE DE [0-9]{2}'
        
            return re.search(padrao, enunciado).group()[-2:]
        
        except:
            return None
        
    @staticmethod
    def acha_categoria(enunciado):
        try:
            padrao_1 = 'MADEIRA DE [A-Z]{7,8} CATEGORIA'
            
            categoria = re.search(padrao_1, enunciado).group()[11:20].replace(' ', '').replace('C', '')
            return categoria
        except:
            return None
        
    @staticmethod
    def acha_quantidade_pinos(enunciado):
        try:
            padrao_1 = 'LIGAÇÃO COM [0-9]'

            qtd_pinos = re.search(padrao_1, enunciado).group()[-1]
            return qtd_pinos
        except:
            return None
        
    @staticmethod
    def acha_diametro_pinos(enunciado):
        try:
            padrao_1 = 'PINOS DE [0-9]'
            
            diam_pinos = re.search(padrao_1, enunciado).group()[-1]
            return diam_pinos
        except:
            return None
        
        