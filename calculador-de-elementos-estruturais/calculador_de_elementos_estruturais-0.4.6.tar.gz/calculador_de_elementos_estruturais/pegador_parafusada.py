from .input_normalizado import input_normalizado


class PegadorParafusada:
    
    @staticmethod
    def pega_medida(informacao_desejada):
        medida_aba = float(input_normalizado(informacao_desejada))
        return medida_aba / 10
    
    @staticmethod
    def pega_espessura(informacao_desejada):
        espessura = float(input_normalizado(informacao_desejada))
        return espessura / 10
    
    @staticmethod
    def pega_diametro_parafuso():
        mensagem = '''Informe a unidade de medida do parafuso. 
        
                (1) Milímetro       (2) Polegada
                
                '''
                
        numero_parafuso = input(mensagem)
        numeros_e_unidades = {'1': 'mm', '2': 'pol'}
        
        try:
            unidade_medida = numeros_e_unidades[numero_parafuso]
            
        except KeyError:
            print('Insira um valor válido.')
            return PegadorParafusada.pega_diametro_parafuso()
        
        diametro_parafuso = float(input_normalizado(f'Insira a espessura do parafuso em {unidade_medida}. '))
        
        if unidade_medida == 'mm':
            return diametro_parafuso / 10
        
        elif unidade_medida == 'pol':
            return diametro_parafuso * 2.54
    
    @staticmethod
    def pega_quantidade_parafusos():
        qtd_parafusos = int(input_normalizado('Informe a quantidade de parafusos. '))
        return qtd_parafusos
    
    @staticmethod
    def pega_especificacao_chapa() -> str:
        mensagem = '''Informe a especificação da peça. 

                (1) MR 250          (6) F-35/Q-35
                (2) AR 350          (7) Q-40
                (3) AR 350 COR      (8) Q-42
                (4) AR 415          (9) Q-45
                (5) F-32/Q-32       (10) Outro

                 '''

        numero_especificacao = input(mensagem)
        classes = {'1': 'MR 250', '2': 'AR 350', '3': 'AR 350 COR',
                   '4': 'AR 415', '5': 'F-32/Q-32', '6': 'F-35/Q-35',
                   '7': 'Q-40', '8': 'Q-42', '9': 'Q-45', '10': 'Outro'}
        
        try:
            classe_chapa = classes[numero_especificacao]
            return classe_chapa
        
        except KeyError:
        
            print('Digite um valor válido.')
            return PegadorParafusada.pega_especificacao_chapa()
        
    @staticmethod
    def pega_fy_e_fu(elemento: str) -> tuple:
        fy = float(input(f'Informe o fy d{elemento}. '))
        fu = float(input(f'Informe o fu d{elemento}. '))
        
        return fy, fu
        
    @staticmethod
    def pega_especificacao_parafuso() -> str:
        mensagem = '''Informe a especificação do parafuso. 

                (1) ASTM A307
                (2) ISO 898-1
                (3) ASTM A325
                (4) ISO 4016 Classe 8.8
                (5) ASTM A490
                (6) ISO 4016 Classe 10.9 
                (7) Outro

                 '''

        numero_especificacao = input(mensagem)
        
        classes = {'1': 'ASTM A307', '2': 'ISO 898-1', '3': 'ASTM A325',
                   '4': 'ISO 4016 8.8', '5': 'ASTM A490', '6': 'ISO 4016 10.9',
                   '7': 'Outro'}
        
        try: 
            classe_parafuso = classes[numero_especificacao]
            return classe_parafuso
        
        except KeyError:
            print('Digite um valor válido.')
            return PegadorParafusada.pega_especificacao_parafuso()