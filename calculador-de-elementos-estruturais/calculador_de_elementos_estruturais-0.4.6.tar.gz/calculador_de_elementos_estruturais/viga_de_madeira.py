from .pegadores import PegadorViga
from .calculadores import CalculadorViga

class VigaDeMadeira:

    def __init__(self, enunciado=None):
        self.circulo_ou_retangulo = PegadorViga.escolhe_tipo_elemento(enunciado)#
        self.dimensoes = PegadorViga.pega_dimensoes(self, enunciado)#
        self.comprimento = PegadorViga.pega_comprimento(enunciado)#
        self.peso_proprio = PegadorViga.pega_peso_proprio(enunciado)
        self.carga_acidental = PegadorViga.pega_carga_acidental(enunciado)
        self.classe = PegadorViga.pega_classe(enunciado)#
        self.categoria = PegadorViga.pega_categoria(enunciado)#
        self.duracao = PegadorViga.pega_duracao(enunciado)#
        self.classe_umidade = PegadorViga.pega_classe_umidade(enunciado)#
        
        self.Fc0k = PegadorViga.pega_Fc0k(self)
        self.kmods = PegadorViga.pega_kmods(self)
        self.Ec0m = PegadorViga.pega_Ec0m(self)

        self.area = CalculadorViga.calcula_area(self)
        self.inercia = CalculadorViga.calcula_inercia(self)
        self.modulo_resistencia = CalculadorViga.calcula_resistencia(self)
        self.carga_permanente = CalculadorViga.calcula_carga_permanente(self)
        self.momento_fletor = CalculadorViga.calcula_momento_fletor(self)
        self.tensao_normal = CalculadorViga.calcula_tensao_normal(self)
        self.kmod = CalculadorViga.calcula_kmod(self)
        self.fc0d = CalculadorViga.calcula_fc0d(self)
        self.flecha_maxima = CalculadorViga.calcula_flecha_maxima(self)
        self.modulo_elasticidade = CalculadorViga.calcula_modulo_elasticidade(self)
        self.flecha_efetiva = CalculadorViga.calcula_flecha_efetiva(self)

        print(self)

    def compara_estado_limite_ultimo(self):
        if self.tensao_normal <= self.fc0d:
            return 'Passou!'
        else:
            return 'Não passou!'

    def compara_flecha(self):
        if self.flecha_efetiva <= self.flecha_maxima:
            return 'Passou!'
        else:
            return 'Não passou!'

    def __str__(self):
        abre_negrito = '\033[1m'
        fecha_negrito = '\033[0m'

        return f'''

        {abre_negrito}Parte 1 - Características Geométricas

{abre_negrito}Área (A){fecha_negrito}: {round(self.area, 6)} m²
{abre_negrito}Momento de Inércia (Iz){fecha_negrito}: {round(self.inercia, 6):.6f} m⁴
{abre_negrito}Módulo de Resistência (Wz){fecha_negrito}: {round(self.modulo_resistencia, 6)} m³

        {abre_negrito}Parte 2 - Ação/Esforços Solicitantes e Resistência de Cálculo

{abre_negrito}Carga Permanente (gk){fecha_negrito}: {round(self.carga_permanente, 6)} kN/m
{abre_negrito}Momento Fletor Máximo (Mzd){fecha_negrito}: {round(self.momento_fletor, 6)} kNm
{abre_negrito}Tensão Máxima (σMzd){fecha_negrito}: {round(self.tensao_normal, 6)} MPa
{abre_negrito}Resistência a Compressão (Fc0k){fecha_negrito}: {self.Fc0k} MPa
{abre_negrito}Kmod1, Kmod2, Kmod3{fecha_negrito}: {self.kmods['1']}, {self.kmods['2']}, {self.kmods['3']}
{abre_negrito}Kmod{fecha_negrito}: {self.kmod}
{abre_negrito}Resistência da Madeira (Fc0d){fecha_negrito}: {self.fc0d} MPa

        {abre_negrito}Parte 3 - Verificação da segurança em relação ao Estado Limite Último

{abre_negrito}Verificação Parte 3{fecha_negrito}: {round(self.tensao_normal, 6)} <= {self.fc0d}
        {abre_negrito}{self.compara_estado_limite_ultimo()}{fecha_negrito}

        {abre_negrito}Parte 4 - Verificação da segurança em situação do Estado Limite de Utilização

{abre_negrito}Flecha Limite (Vlim){fecha_negrito}: {self.flecha_maxima} mm
{abre_negrito}Ec0m{fecha_negrito}: {self.Ec0m} MPa
{abre_negrito}Modulo de Elasticidade Efetivo (Eef){fecha_negrito}: {self.modulo_elasticidade} kN/m²
{abre_negrito}Flecha Efetiva (Vef){fecha_negrito}: {round(self.flecha_efetiva, 6)} mm

{abre_negrito}Verificação Parte 4{fecha_negrito}: {round(self.flecha_efetiva, 6)} <= {self.flecha_maxima}
        {abre_negrito}{self.compara_flecha()}{fecha_negrito}




'''