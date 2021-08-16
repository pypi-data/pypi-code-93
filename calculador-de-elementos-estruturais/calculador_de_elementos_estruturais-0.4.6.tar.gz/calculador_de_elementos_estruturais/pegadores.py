from abc import abstractmethod, ABCMeta
from .enunciado_pv import EnunciadoPilar, EnunciadoViga, Enunciado
from .informacoes import tabela_classe, informacoes_kmod1, duracoes, informacoes_kmod2, informacoes_kmod3, categorias
from .input_normalizado import input_normalizado

class Pegador(ABCMeta):

    @staticmethod
    @abstractmethod
    def pega_dimensoes(elemento, enunciado):
        pass

    @staticmethod
    @abstractmethod
    def pega_comprimento(enunciado):
        pass

    @staticmethod
    @abstractmethod
    def pega_cargas(enunciado):
        pass

    @staticmethod
    def escolhe_tipo_elemento(enunciado):
        
        circulo_ou_retangulo = Enunciado.acha_tipo_elemento(enunciado)
        
        if circulo_ou_retangulo is not None:
            return circulo_ou_retangulo

        else:
            mensagem = f'''O elemento é retangular ou circular?

                (1) Circular
                (2) Retangular

                 '''

            circulo_ou_retangulo = input(mensagem)
            if circulo_ou_retangulo in ('1', '2'):
                return circulo_ou_retangulo
            else:
                raise ValueError('Digite um valor válido.')

    @staticmethod
    def pega_classe(enunciado):
        
        nome_classe = Enunciado.acha_classe(enunciado)
        
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
            mensagem_classe = '''Informe a classe da madeira. 

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
    def pega_categoria(enunciado):
        categoria = Enunciado.acha_categoria(enunciado)
        
        if categoria is not None:
            categoria = int(categoria)
            
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
    def pega_duracao(enunciado):
        palavra_duracao = Enunciado.acha_duracao(enunciado)
        
        if palavra_duracao is not None:
            if palavra_duracao == 'DURADOURA':
                duracao = 2
                
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
        classe_umidade = Enunciado.acha_umidade(enunciado)
        
        if classe_umidade is not None:
            umidade = int(classe_umidade)
        
        else:
            umidade = int(input_normalizado('Informe a umidade ambiente. '))

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
    def pega_Fc0k(elemento):
        fc0k = tabela_classe.loc[elemento.classe, 'Fc0k']
        return fc0k

    @staticmethod
    def pega_kmods(elemento):
        duracao = duracoes[elemento.duracao - 1]
        kmod1 = informacoes_kmod1[duracao]

        kmod2 = informacoes_kmod2[elemento.classe_umidade]

        categoria = categorias[elemento.categoria - 1]
        kmod3 = informacoes_kmod3[categoria]

        return {'1': kmod1, '2': kmod2, '3': kmod3}

    @staticmethod
    def pega_Ec0m(elemento):
        Ec0m = tabela_classe.loc[elemento.classe, 'Ec0m']
        return Ec0m


class PegadorViga(Pegador):

    @staticmethod
    def pega_dimensoes(viga, enunciado):
        if viga.circulo_ou_retangulo == '1':
            dimensoes = EnunciadoViga.acha_secao_circular(enunciado)
            if dimensoes is not None:
                diametro = float(dimensoes)
            else:
                diametro = float(input_normalizado('Informe o diâmetro em centímetro da peça. '))
                
            return {'d': diametro / 100}
        
        else:
            dimensoes = EnunciadoViga.acha_secao_transversal(enunciado)
            if dimensoes is not None:
                base = float(dimensoes['b'])
                altura = float(dimensoes['h'])
            else:
                base = float(input_normalizado('Informe a medida da base em centímetro da peça. '))
                altura = float(input_normalizado('Informe a medida da altura em centímetro da peça. '))
                
            return {'b': base / 100, 'h': altura / 100}

    @staticmethod
    def pega_comprimento(enunciado):
        dimensao = EnunciadoViga.acha_comprimento(enunciado)
        if dimensao is not None:
            comprimento = float(dimensao)
        else:
            comprimento = float(input_normalizado('Informe o comprimento em metro da viga. '))
            
        return comprimento

    @staticmethod
    def pega_peso_proprio(enunciado):
        carga = EnunciadoViga.acha_peso_proprio(enunciado)
        if carga is not None:
            peso_proprio = float(carga)
        else:
            peso_proprio = float(input_normalizado('Informe o peso próprio da viga. '))

        return peso_proprio

    @staticmethod
    def pega_carga_acidental(enunciado):
        carga = EnunciadoViga.acha_carga_acidental(enunciado)
        if carga is not None:
            carga_acidental = float(carga)
        else:
            carga_acidental = float(input_normalizado('Informe a carga acidental da viga. '))
        
        return carga_acidental


class PegadorPilar(Pegador):

    @staticmethod
    def pega_dimensoes(pilar, enunciado):
        if pilar.circulo_ou_retangulo == '1':
            dimensao = EnunciadoPilar.acha_secao_circular(enunciado)
            if dimensao is not None:
                diametro = float(dimensao)
            else:
                diametro = float(input_normalizado('Informe o diâmetro em centímetro da peça. '))
                
            return {'d': diametro}
        else:
            dimensoes = EnunciadoPilar.acha_secao_transversal(enunciado)
            if dimensoes is not None:
                base = float(dimensoes['b'])
                altura = float(dimensoes['h'])
            else:
                base = float(input_normalizado('Informe a medida da base em centímetro da peça. '))
                altura = float(input_normalizado('Informe a medida da altura em centímetro da peça. '))
                
            return {'b': base, 'h': altura}

    @staticmethod
    def pega_comprimento(enunciado):
        dimensao = EnunciadoPilar.acha_comprimento(enunciado)
        if dimensao is not None:
            comprimento = float(dimensao)
        else:
            comprimento = float(input_normalizado('Informe o comprimento em metro do pilar. '))
            
        return comprimento * 100

    @staticmethod
    def pega_flexao_composta(enunciado):
        carga = EnunciadoPilar.acha_flexao_composta(enunciado)
        if carga is not None:
            flexao_composta = float(carga)
        else:
            flexao_composta = float(input_normalizado('Informe o esforço de Flexão Composta (Nd) do pilar. '))

        return flexao_composta

    @staticmethod
    def pega_momentos(enunciado):
        momentos = EnunciadoPilar.acha_momentos(enunciado)
        if momentos is not None:
            momento_z = float(momentos['z'])
            momento_y = float(momentos['y'])
        else:
            momento_z = float(input_normalizado('Informe o Momento Fletor no eixo Z (Mzd) do pilar. '))
            momento_y = float(input_normalizado('Informe o Momento Fletor no eixo Y (Myd) do pilar. '))

        return {'z': momento_z, 'y': momento_y}