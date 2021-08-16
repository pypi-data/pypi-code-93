from calculador_de_elementos_estruturais.cantoneira_tracionada import CantoneiraTracionada
from .viga_de_madeira import VigaDeMadeira
from .pilar_de_madeira import PilarDeMadeira
from .enunciado_pv import Enunciado
from .ligacao_corte_duplo import LigacaoCorteDuplo
from .ligacao_parafusada import LigacaoParafusada
from .barra_tracionada import BarraTracionada

class MenuPrincipal:

    def __init__(self):
        mensagem = '''
        
    Bem vindo ao Calculador de Estruturas do 4º TE. A seguir, um pequeno tutorial de uso.
    
    
    Se tudo der certo, você só deve copiar e colar o enunciado. Mas caso não dê:
    
    Quando aparecer um seletor, por exemplo:
    
            (1) Opção 1
            (2) Opção 2
            (3) Opção 3

    Digite apenas o número que está dentro do parênteses. Por exemplo, se sua opção desejada for a 2,
    digite apenas "2" (sem as aspas).
    
    Não é necessário digitar as unidades dos valores. Caso elas sejam digitadas, erros ocorrerão.
    
    '''
    
        print(mensagem)

        while True:
            
            enunciado = Enunciado.pega_enunciado()
            
            if enunciado not in (' ', ''):
                if 'PILAR' in enunciado:
                    PilarDeMadeira(enunciado)
                elif 'VIGA' in enunciado:
                    VigaDeMadeira(enunciado)
                elif 'CORTE DUPLO' in enunciado:
                    LigacaoCorteDuplo(enunciado)
                elif 'NOMINAL' in enunciado:
                    LigacaoParafusada()
                elif 'NORMAL' in enunciado:
                    BarraTracionada()
                elif 'COM OUTRA CANTONEIRA' in enunciado:
                    CantoneiraTracionada()
                else:
                    MenuPrincipal.seletor_manual()
            else:
                MenuPrincipal.seletor_manual()
            
    @staticmethod    
    def seletor_manual() -> None:
        mensagem = '''Qual elemento estrutural irá ser calculado?
        
                (1) Pilar
                (2) Viga
                (3) Ligação Corte Duplo
                (4) Ligação Parafusada
                (5) Barra Tracionada
                (6) Cantoneira Tracionada
            
                 '''
        numero_elemento = input(mensagem)
        todos_os_elementos = {'1': PilarDeMadeira,
                              '2': VigaDeMadeira,
                              '3': LigacaoCorteDuplo,
                              '4': LigacaoParafusada,
                              '5': BarraTracionada,
                              '6': CantoneiraTracionada}
        
        if numero_elemento not in todos_os_elementos.keys():
            print('Digite um valor válido.')
            MenuPrincipal.seletor_manual()
        else:    
            elemento_estrutural = todos_os_elementos[numero_elemento]
            elemento_estrutural()
