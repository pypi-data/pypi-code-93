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
    def acha_tipo_elemento(enunciado):
        try:
            return '1' if 'CIRCULAR' in enunciado else '2'
        except:
            return None
        

    @staticmethod
    def acha_classe(enunciado):
        try:
            padrao_1 = 'CLASSE C[0-9]{2}'
            padrao_2 = 'CLASSE C [0-9]{2}'

            classe = re.search(padrao_1, enunciado)
            if classe is not None:
                classe = classe.group()[-3:]
                
            else:
                classe = re.search(padrao_2, enunciado).group()[-4:]
                classe = classe[0] + classe[2:]

            return classe
        
        except:
            return None
    

    @staticmethod
    def acha_categoria(enunciado):
        try: 
            padrao_1 = 'MADEIRA SERRADA DE [0-9]'
            padrao_2 = 'MADEIRA DE [0-9]A CATEGORIA'
            
            categoria = re.search(padrao_1, enunciado)
            if categoria is not None:
                categoria = categoria.group()[-1]
            else:
                categoria = re.search(padrao_2, enunciado).group()[11]
                
            return categoria
        
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
    def acha_dimensoes(enunciado):
        
        try:
            if 'CIRCULAR' in enunciado:
                dimensoes = Enunciado.acha_secao_circular(enunciado)
            elif 'TRANSVERSAL' in enunciado:
                dimensoes = Enunciado.acha_secao_transversal(enunciado)
                
            return dimensoes
    
        except:
            return None
        
    @staticmethod
    def acha_secao_circular(enunciado):
        try:
            padrao = 'CIRCULAR DE [0-9]{2}'
            
            return {'d': re.search(padrao, enunciado).group()[-2:]}
        
        except:
            return None
        
    @staticmethod
    def acha_secao_transversal(enunciado):
        try:
            p1 = 'TRANSVERSAL [0-9]{1,2}CMX[0-9]{1,2}CM'
            p2 = 'TRANSVERSAL DE [0-9]{1,2}X[0-9]{1,2} CENT'
            p3 = 'TRANSVERSAL DE [0-9]{1,2},[0-9]X[0-9]{1,2} CENT'
            p4 = 'TRANSVERSAL DE [0-9]{1,2}X[0-9]{1,2},[0-9] CENT'
            p5 = 'TRANSVERSAL DE [0-9]{1,2},[0-9]X[0-9]{1,2},[0-9] CENT'
            p6 = 'TRANSVERSAL DE [0-9]{1,2} X[0-9]{1,2} CENT'
            p7 = 'TRANSVERSAL DE [0-9]{1,2}X [0-9]{1,2} CENT'
            p8 = 'TRANSVERSAL DE [0-9]{1,2},[0-9] X[0-9]{1,2} CENT'
            p9 = 'TRANSVERSAL DE [0-9]{1,2},[0-9] X[0-9]{1,2} CENT'
            p10 = 'TRANSVERSAL DE [0-9]{1,2},[0-9]X [0-9]{1,2} CENT'
            p11 = 'TRANSVERSAL DE [0-9]{1,2},[0-9]X [0-9]{1,2} CENT'
            p12 = 'TRANSVERSAL DE [0-9]{1,2},[0-9] X[0-9]{1,2},[0-9] CENT'
            p13 = 'TRANSVERSAL DE [0-9]{1,2},[0-9]X [0-9]{1,2},[0-9] CENT'
            p14 = 'TRANSVERSAL DE [0-9]{1,2} X [0-9]{1,2} CENT'
            p15 = 'TRANSVERSAL DE [0-9]{1,2},[0-9] X [0-9]{1,2} CENT'
            p16 = 'TRANSVERSAL DE [0-9]{1,2} X [0-9]{1,2},[0-9] CENT'
            p17 = 'TRANSVERSAL DE [0-9]{1,2},[0-9] X [0-9]{1,2},[0-9] CENT'
            
            padroes = [p1,p2,p3,p4,p5,p6,p7,p8,p9,p10,p11,p12,p13,p14,p15,p16,p17]
            
            frase_nao_tratada = None
            for padrao in padroes:
                auxiliar = re.search(padrao, enunciado)
                if auxiliar is not None:
                    frase_nao_tratada = auxiliar.group()
            
            frase_semi_tratada = frase_nao_tratada.replace('CM', ' ').replace('X', ' ').replace(',', '.').split()
            
            numeros = []
            for palavra in frase_semi_tratada:
                if palavra.isnumeric() or not palavra.isalpha():
                    numeros.append(palavra)
                    
            dimensoes = {'b': numeros[0], 'h': numeros[1]}
            
            return dimensoes
        
        except:
            return None
        
    @staticmethod
    def acha_duracao(enunciado):
        try:
            padrao_1 = 'DE PROJETO [A-Z]{9}'
            padrao_2 = '[A-Z]{9} PARA PROJETO'
            
            duracao = re.search(padrao_1, enunciado)
            if duracao is not None:
                duracao = duracao.group()[-9:]
            else:
                duracao = re.search(padrao_2, enunciado).group()[:9]
                
            return duracao
        
        except:
            return None
    
    
class EnunciadoViga(Enunciado):
    
    @staticmethod
    def acha_comprimento(enunciado):
        try:
            padrao = 'RICO DE L = [0-9],[0-9]{1,2}'
            
            comprimento = re.search(padrao, enunciado).group()[12:].replace(',', '.').replace(' ', '')
            
            return comprimento
        
        except:
            return None
    
    @staticmethod
    def acha_peso_proprio(enunciado):
        try:
            padrao = 'ACRESCIDO DE [0-9],[0-9]{2}'
        
            peso_proprio = re.search(padrao, enunciado).group()[-4:].replace(',', '.')
            return peso_proprio
        
        except:
            return None
    
    @staticmethod
    def acha_carga_acidental(enunciado):
        try:
            padrao = 'STICA DE [0-9],[0-9]'
        
            carga_acidental = re.search(padrao, enunciado).group()[-3:].replace(',', '.')
            return carga_acidental
        
        except:
            return None
    
    
class EnunciadoPilar(Enunciado):
    
    @staticmethod
    def acha_comprimento(enunciado):
        try:
            padrao = '[0-9],[0-9]{2} M DE COMPRIMENTO'
        
            comprimento = re.search(padrao, enunciado).group()[:5].replace(' ', '').replace(',', '.')
            return comprimento
        
        except:
            return None
        
    @staticmethod
    def acha_flexao_composta(enunciado):
        try:
            padrao_1 = 'ND =[0-9]{3}'
            padrao_2 = 'ND = [0-9]{3}'
        
            frase = re.search(padrao_1, enunciado)
            if frase is not None:
                flexao_composta = frase.group()[-3:]
            else:
                flexao_composta = re.search(padrao_2, enunciado).group()[-3:]
                
            return flexao_composta
        
        except:
            return None
    
    def acha_momentos(enunciado):
        try:
            padrao = 'MZD = [0-9]{2} KN.M E MYD = [0-9]{2} KN.M'#7:9   -7:-5
        
            frase = re.search(padrao, enunciado).group()
            momentos = {'z': frase[6:8], 'y': frase[-7:-5]}
            return momentos
        
        except:
            return None

