from .enunciado_ligacao_dupla import EnunciadoLigacaoDupla
from .informacoes import tabela_classe, informacoes_kmod1, duracoes, informacoes_kmod2, informacoes_kmod3, categorias

class PegadorLigacaoDupla:
    
    @staticmethod
    def retorna_classe(nome_classe, localizacao):
        if nome_classe is not None:
            if nome_classe == 'C20':
                classe = 1
            elif nome_classe == 'C30':
                classe = 2
            elif nome_classe == 'C40':
                classe = 3
            elif nome_classe == 'C60':
                classe = 4
                
        else:
            mensagem_classe = f'''Informe a classe da madeira {localizacao}. 

                (1) C20
                (2) C30
                (3) C40
                (4) C60

                 '''

            classe = int(input(mensagem_classe))
            
        if classe not in (1, 2, 3, 4):
            raise ValueError('Digite um valor válido para classe. ')

        return classe
    
    @staticmethod
    def retorna_espessura(espessura_str, localizacao):
        if espessura_str is not None:
            espessura = float(espessura_str)
        else:
            espessura = float(input(f'Informe a espessura da madeira {localizacao} em milímetro. '))
        return espessura
    
    @staticmethod
    def pega_classe_central(enunciado):
        nome_classe = EnunciadoLigacaoDupla.acha_classe_central(enunciado)
        classe = PegadorLigacaoDupla.retorna_classe(nome_classe, 'central')
        return classe
    
    @staticmethod
    def pega_espessura_central(enunciado):
        espessura_str = EnunciadoLigacaoDupla.acha_espessura_central(enunciado)
        espessura = PegadorLigacaoDupla.retorna_espessura(espessura_str, 'central')
        return espessura
        
    @staticmethod
    def pega_classe_lateral(enunciado):
        nome_classe = EnunciadoLigacaoDupla.acha_classe_lateral(enunciado)
        classe = PegadorLigacaoDupla.retorna_classe(nome_classe, 'lateral')
        return classe
    
    @staticmethod
    def pega_espessura_lateral(enunciado):
        espessura_str = EnunciadoLigacaoDupla.acha_espessura_lateral(enunciado)
        espessura = PegadorLigacaoDupla.retorna_espessura(espessura_str, 'lateral')
        return espessura
    
    @staticmethod
    def pega_escoamento_aco(enunciado):
        escoamento_str = EnunciadoLigacaoDupla.acha_escoamento_aco(enunciado)
        if escoamento_str is not None:
            escoamento = float(escoamento_str)
        else:
            escoamento = float(input('Informe a resistência ao escoamento do aço (fyk). '))
        return escoamento
    
    @staticmethod
    def pega_duracao(enunciado):
        palavra_duracao = EnunciadoLigacaoDupla.acha_duracao(enunciado)
        
        if palavra_duracao is not None and palavra_duracao in ('DURADOURA', 'LONGA'):
            duracao = 2
            
        elif palavra_duracao and palavra_duracao == 'PERMANENTE':
            duracao = 1
                
        else:
            mensagem_duracao = '''Informe a duração do carregamento.

                (1) Permanente
                (2) Longa Duração
                (3) Média Duração
                (4) Curta Duração
                (5) Instantânea

                 '''

            duracao = int(input(mensagem_duracao))
                
        if duracao not in (1, 2, 3, 4, 5):
            raise ValueError('Digite um valor válido para duração. ')
        return duracao
            
    @staticmethod
    def pega_classe_umidade(enunciado):
        classe_umidade = EnunciadoLigacaoDupla.acha_umidade(enunciado)
        
        if classe_umidade is not None:
            umidade = int(classe_umidade)
        
        else:
            umidade = int(input('Informe a umidade ambiente. '))

        if umidade <= 65:
            classe_umidade = '1'
        elif 65 < umidade <= 75:
            classe_umidade = '2'
        elif 75 < umidade <= 85:
            classe_umidade = '3'
        else:
            classe_umidade = '4'

        return classe_umidade 
    
    @staticmethod
    def pega_categoria(enunciado):
        categoria_str = EnunciadoLigacaoDupla.acha_categoria(enunciado).strip()
        
        if categoria_str is not None:
            if categoria_str == 'PRIMEIRA':
                categoria = 1
            elif categoria_str == 'SEGUNDA':
                categoria = 2
            
        else:
            mensagem_categoria = '''Informe a categoria da madeira.

                (1) 1ª categoria
                (2) 2ª categoria

                 '''

            categoria = int(input(mensagem_categoria))
            
        if categoria not in (1, 2):
            raise ValueError('Digite um valor válido para categoria. ')

        return categoria
    
    @staticmethod
    def pega_quantidade_pinos(enunciado):
        pinos_str = EnunciadoLigacaoDupla.acha_quantidade_pinos(enunciado)
        if pinos_str is not None:
            pinos = int(pinos_str)
        else:
            pinos = int(input('Informe a quantidade de pinos da ligação. '))
            
        return pinos
    
    @staticmethod
    def pega_diametro_pinos(enunciado):
        diametro_str = EnunciadoLigacaoDupla.acha_diametro_pinos(enunciado)
        if diametro_str is not None:
            diametro = float(diametro_str)
        else:
            diametro = float(input('Informe o diâmetro dos pinos da ligação. '))
            
        return diametro
    
    @staticmethod
    def pega_Fc0k(classe):
        fc0k = tabela_classe.loc[classe, 'Fc0k']
        return fc0k

    @staticmethod
    def pega_kmods(_duracao, classe_umidade, _categoria):
        duracao = duracoes[_duracao - 1]
        kmod1 = informacoes_kmod1[duracao]

        kmod2 = informacoes_kmod2[classe_umidade]

        categoria = categorias[_categoria - 1]
        kmod3 = informacoes_kmod3[categoria]

        return {'1': kmod1, '2': kmod2, '3': kmod3}
