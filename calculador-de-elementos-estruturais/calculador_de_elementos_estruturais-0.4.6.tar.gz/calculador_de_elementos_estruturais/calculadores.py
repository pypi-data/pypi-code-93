import math
from abc import abstractmethod, ABCMeta

class Calculador(ABCMeta):

    @staticmethod
    @abstractmethod
    def calcula_inercia(elemento):
        pass

    @staticmethod
    @abstractmethod
    def calcula_resistencia(elemento):
        pass

    @staticmethod
    def calcula_area(elemento):
        if elemento.circulo_ou_retangulo == '1':
            area = (math.pi * elemento.dimensoes['d'] ** 2) / 4
            return area
        else:
            area = elemento.dimensoes['b'] * elemento.dimensoes['h']
            return round(area, 6)

    @staticmethod
    def calcula_fc0d(elemento):
        fc0d = (elemento.kmod * elemento.Fc0k) / 1.4
        return round(fc0d, 2)
    
    @staticmethod
    def calcula_modulo_elasticidade(elemento):
        Eef = (elemento.Ec0m * elemento.kmod) * 1000
        return round(Eef, 2)

    def calcula_kmod(elemento):
        kmod = elemento.kmods['1'] * elemento.kmods['2'] * elemento.kmods['3']

        return round(kmod, 3)


class CalculadorViga(Calculador):

    @staticmethod
    def calcula_inercia(viga):
        if viga.circulo_ou_retangulo == '1':
            inercia = (math.pi * (viga.dimensoes['d'] ** 4)) / 64
        else:
            inercia = (viga.dimensoes['b'] * viga.dimensoes['h'] ** 3) / 12

        return round(inercia, 8)

    @staticmethod
    def calcula_resistencia(viga):
        if viga.circulo_ou_retangulo == '1':
            W = (math.pi * (viga.dimensoes['d'] ** 3)) / 32
        else:
            W = (viga.dimensoes['b'] * (viga.dimensoes['h'] ** 2)) / 6

        return W

    @staticmethod
    def calcula_carga_permanente(viga):
        carga_permanente = viga.area * 10 + viga.peso_proprio
        return carga_permanente

    @staticmethod
    def calcula_momento_fletor(viga):
        momento_fletor = (1.4 * (viga.carga_permanente + viga.carga_acidental) * viga.comprimento ** 2) / 8
        return momento_fletor

    @staticmethod
    def calcula_tensao_normal(viga):
        tensao_normal = (viga.momento_fletor / viga.modulo_resistencia) / 1000
        return round(tensao_normal, 3)

    @staticmethod
    def calcula_flecha_maxima(viga):
        flecha_maxima = (viga.comprimento / 200) * 1000
        return flecha_maxima

    @staticmethod
    def calcula_flecha_efetiva(viga):
        Vef = ((5 * (viga.carga_permanente + 0.2 * viga.carga_acidental) * viga.comprimento ** 4) / (
                384 * viga.modulo_elasticidade * viga.inercia)) * 1000
        return round(Vef, 3)


class CalculadorPilar(Calculador):

    @staticmethod
    def calcula_inercia(pilar):
        if pilar.circulo_ou_retangulo == '1':
            inercia = (math.pi * (pilar.dimensoes['d'] ** 4)) / 64
            return {'z': inercia, 'y': inercia}
        else:
            inercia_z = (pilar.dimensoes['b'] * pilar.dimensoes['h'] ** 3) / 12
            inercia_y = (pilar.dimensoes['h'] * pilar.dimensoes['b'] ** 3) / 12
            return {'z': inercia_z, 'y': inercia_y}

    @staticmethod
    def calcula_resistencia(pilar):
        if pilar.circulo_ou_retangulo == '1':
            W = (math.pi * (pilar.dimensoes['d'] ** 3)) / 32
            return {'z': W, 'y': W}
        else:
            Wz = (pilar.dimensoes['b'] * (pilar.dimensoes['h'] ** 2)) / 6
            Wy = (pilar.dimensoes['h'] * (pilar.dimensoes['b'] ** 2)) / 6
            return {'z': Wz, 'y': Wy}

    @staticmethod
    def calcula_raio_giracao(pilar):
        raio_giracao_z = math.sqrt((pilar.inercia['z']/pilar.area))
        raio_giracao_y = math.sqrt((pilar.inercia['y']/pilar.area))

        return {'z': raio_giracao_z, 'y': raio_giracao_y}

    @staticmethod
    def calcula_indice_esbeltez(pilar):
        esbeltez_z = pilar.comprimento/pilar.raio_giracao['z']
        esbeltez_y = pilar.comprimento/pilar.raio_giracao['y']

        return {'z': esbeltez_z, 'y': esbeltez_y}

    @staticmethod
    def calcula_tensao_normal(pilar):
        tensao_normal = pilar.flexao_composta/pilar.area

        return tensao_normal * 10

    @staticmethod
    def calcula_tensao_momento_fletor(pilar):
        tensao_z = (pilar.momentos['z'] * 100)/pilar.modulo_resistencia['z']
        tensao_y = (pilar.momentos['y'] * 100)/pilar.modulo_resistencia['y']

        return {'z': (tensao_z * 10), 'y': (tensao_y * 10)}

    @staticmethod
    def retorna_excentricidade(pilar):
        if (pilar.indice_esbeltez['z'] > 40) and (pilar.indice_esbeltez['y'] > 40):
            lista_excentricidades = []
            for item in ('z', 'y'):
                lista_excentricidades.append(CalculadorPilar.calcula_excentricidade(pilar, item))

            excentricidade = {'z': lista_excentricidades[0], 'y': lista_excentricidades[1]}

        elif pilar.indice_esbeltez['z'] > 40:
            excentricidade = CalculadorPilar.calcula_excentricidade(pilar, 'z')

        elif pilar.indice_esbeltez['y'] > 40:
            excentricidade = CalculadorPilar.calcula_excentricidade(pilar, 'y')

        else: 
            excentricidade = None

        return excentricidade

    @staticmethod
    def calcula_excentricidade(pilar, eixo):
        
        excentricidade_acidental = (pilar.comprimento * 10) / 300
        eiz = (pilar.momentos[eixo] / pilar.flexao_composta) * 1000
        e1z = excentricidade_acidental + eiz

        fe = ((math.pi**2) * pilar.modulo_elasticidade * pilar.inercia[eixo] * 10**-8) / ((pilar.comprimento / 100) ** 2)
        ezd = e1z * (fe/(fe-pilar.flexao_composta))
        myd = (pilar.flexao_composta * (ezd * 10**-3))
        sigma_myd = myd / (pilar.modulo_resistencia[eixo] * 10**-6) / 1000

        anti_eixo = 'z' if eixo == 'y' else 'y'

        resultados = {'σMyd': (sigma_myd, f'σM{eixo}d'), 'Myd': (myd, f'M{eixo}d'), 'fe': fe, 'eixo': eixo,
                      'anti_eixo': anti_eixo, 'ea': excentricidade_acidental,
                      'eiz': (eiz, f'ei{anti_eixo}'), 'e1z': (e1z, f'e1{anti_eixo}'), 
                      'ezd': (ezd, f'e{anti_eixo}d')}

        return resultados