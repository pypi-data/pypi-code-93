from .pegadores import PegadorPilar
from .calculadores import CalculadorPilar

class PilarDeMadeira:

    def __init__(self, enunciado=None):
        self.circulo_ou_retangulo = PegadorPilar.escolhe_tipo_elemento(enunciado)#
        self.dimensoes = PegadorPilar.pega_dimensoes(self, enunciado)#
        self.comprimento = PegadorPilar.pega_comprimento(enunciado)#
        self.flexao_composta = PegadorPilar.pega_flexao_composta(enunciado)
        self.momentos = PegadorPilar.pega_momentos(enunciado)
        self.classe = PegadorPilar.pega_classe(enunciado)#
        self.categoria = PegadorPilar.pega_categoria(enunciado)#
        self.duracao = PegadorPilar.pega_duracao(enunciado)#
        self.classe_umidade = PegadorPilar.pega_classe_umidade(enunciado)#
        
        self.Fc0k = PegadorPilar.pega_Fc0k(self)
        self.kmods = PegadorPilar.pega_kmods(self)
        self.Ec0m = PegadorPilar.pega_Ec0m(self)

        self.area = CalculadorPilar.calcula_area(self)
        self.inercia = CalculadorPilar.calcula_inercia(self)
        self.modulo_resistencia = CalculadorPilar.calcula_resistencia(self)
        self.raio_giracao = CalculadorPilar.calcula_raio_giracao(self)
        self.indice_esbeltez = CalculadorPilar.calcula_indice_esbeltez(self)
        self.kmod = CalculadorPilar.calcula_kmod(self)
        self.fc0d = CalculadorPilar.calcula_fc0d(self)
        self.tensao_normal = CalculadorPilar.calcula_tensao_normal(self)
        self.tensao_momento_fletor = CalculadorPilar.calcula_tensao_momento_fletor(self)
        self.modulo_elasticidade = CalculadorPilar.calcula_modulo_elasticidade(self)
        self.excentricidade = CalculadorPilar.retorna_excentricidade(self)

        print(self)

    def verificacao_parte_1(self):
        verificacao = ((self.tensao_normal/self.fc0d)**2 +
                       self.tensao_momento_fletor['y']/self.fc0d +
                       0.5 * (self.tensao_momento_fletor['z']/self.fc0d))
        if verificacao < 1:
            return 'Passou!', round(verificacao, 6)
        else:
            return 'Não passou!', round(verificacao, 6)

    def verificacao_parte_2(self):
        verificacao = ((self.tensao_normal/self.fc0d)**2 +
                       0.5 * (self.tensao_momento_fletor['y']/self.fc0d) +
                       self.tensao_momento_fletor['z']/self.fc0d)
        if verificacao < 1:
            return 'Passou!', round(verificacao, 6)
        else:
            return 'Não passou!', round(verificacao, 6)

    def verificacao_parte_3(self):
        abre_negrito = '\033[1m'
        fecha_negrito = '\033[0m'

        if type(self.excentricidade) == type(None):
            return ''

        elif len(self.excentricidade) > 2:
            calculo_verificacao = round(((self.tensao_normal/self.fc0d) +
                                   (self.excentricidade['σMyd'][0] / self.fc0d)), 6)
            if calculo_verificacao <= 1:
                verificacao = 'Passou!'
            else:
                verificacao = 'Não passou!'

            eixo = self.excentricidade['eixo']
            anti_eixo = self.excentricidade['anti_eixo']
            
            return f'''     {abre_negrito}Parte 4 - Excentricidade
        
    {abre_negrito}Eixo {eixo.upper()}
            
{abre_negrito}Excentricidade acidental (ea){fecha_negrito}: {round(self.excentricidade['ea'], 6)} mm
{abre_negrito}{self.excentricidade['eiz'][1]}{fecha_negrito}: {round(self.excentricidade['eiz'][0], 6)} mm
{abre_negrito}{self.excentricidade['e1z'][1]}{fecha_negrito}: {round(self.excentricidade['e1z'][0], 6)} mm
{abre_negrito}Ec0m{fecha_negrito}: {self.Ec0m} MPa
{abre_negrito}Módulo de Elasticidade (Ec0ef){fecha_negrito}: {self.modulo_elasticidade} kN/m²
{abre_negrito}Fe{fecha_negrito}: {round(self.excentricidade['fe'], 6)} kN
{abre_negrito}{self.excentricidade['ezd'][1]}{fecha_negrito}: {round(self.excentricidade['ezd'][0], 6)} mm
{abre_negrito}Novo Momento Fletor em {eixo.upper()} ({self.excentricidade['Myd'][1]}){fecha_negrito}: {round(self.excentricidade['Myd'][0], 6)} kNm
{abre_negrito}Nova Tensão Momento Fletor em {eixo.upper()} ({self.excentricidade['σMyd'][1]}){fecha_negrito}: {round(self.excentricidade['σMyd'][0], 6)} MPa

{abre_negrito}Verificação Parte 4{fecha_negrito}: {calculo_verificacao} <= 1
        {abre_negrito}{verificacao}{fecha_negrito}
    '''

        elif len(self.excentricidade) == 2:

            calculo_verificacao_z = ((self.tensao_normal/self.fc0d) +
                                   (self.excentricidade['z']['σMyd'][0] / self.fc0d))

            if calculo_verificacao_z <= 1:
                verificacao_z = 'Passou!'
            else:
                verificacao_z = 'Não passou!'

            calculo_verificacao_y = ((self.tensao_normal/self.fc0d) +
                                   (self.excentricidade['y']['σMyd'][0] / self.fc0d))

            if calculo_verificacao_y <= 1:
                verificacao_y = 'Passou!'
            else:
                verificacao_y = 'Não passou!'

            return f'''     {abre_negrito}Parte 4 - Excentricidade
            
{abre_negrito}Excentricidade acidental (ea){fecha_negrito}: {round(self.excentricidade['z']['ea'], 6)} mm
{abre_negrito}Ec0m{fecha_negrito}: {self.Ec0m} MPa
{abre_negrito}Módulo de Elasticidade (Ec0ef){fecha_negrito}: {self.modulo_elasticidade} kN/m²
            
    {abre_negrito}Verificação em Z:{fecha_negrito}
{abre_negrito}eiy{fecha_negrito}: {round(self.excentricidade['z']['eiz'][0], 6)} mm
{abre_negrito}e1y{fecha_negrito}: {round(self.excentricidade['z']['e1z'][0], 6)} mm
{abre_negrito}Fe{fecha_negrito}: {round(self.excentricidade['z']['fe'], 6)} kN
{abre_negrito}eyd{fecha_negrito}: {round(self.excentricidade['z']['ezd'][0], 6)} mm
{abre_negrito}Novo Momento Fletor em Z (Mzd){fecha_negrito}: {round(self.excentricidade['z']['Myd'][0], 6)} kNm
{abre_negrito}Nova Tensão Momento Fletor em Z (σMzd){fecha_negrito}: {round(self.excentricidade['z']['σMyd'][0], 6)} MPa

{abre_negrito}Verificação Parte 4 em Z{fecha_negrito}: {round(calculo_verificacao_z, 6)} <= 1
        {abre_negrito}{verificacao_z}{fecha_negrito}

    {abre_negrito}Verificação em Y:{fecha_negrito}
{abre_negrito}eiz{fecha_negrito}: {round(self.excentricidade['y']['eiz'][0], 6)} mm
{abre_negrito}e1z{fecha_negrito}: {round(self.excentricidade['y']['e1z'][0], 6)} mm
{abre_negrito}Fe{fecha_negrito}: {round(self.excentricidade['y']['fe'], 6)} kN
{abre_negrito}ezd{fecha_negrito}: {round(self.excentricidade['y']['ezd'][0], 6)} mm
{abre_negrito}Novo Momento Fletor em Y (Myd){fecha_negrito}: {round(self.excentricidade['y']['Myd'][0], 6)} kNm
{abre_negrito}Nova Tensão Momento Fletor em Y (σMyd){fecha_negrito}: {round(self.excentricidade['y']['σMyd'][0], 6)} MPa

{abre_negrito}Verificação Parte 4 em Y{fecha_negrito}: {round(calculo_verificacao_y, 6)} <= 1
        {abre_negrito}{verificacao_y}{fecha_negrito}
    '''

    def __str__(self):
        abre_negrito = '\033[1m'
        fecha_negrito = '\033[0m'

        return f'''

        {abre_negrito}Parte 1 - Características Geométricas

{abre_negrito}Área (A){fecha_negrito}: {round(self.area, 6)} cm²
{abre_negrito}Momento de Inércia em z (Iz){fecha_negrito}: {round(self.inercia['z'], 6)} cm⁴
{abre_negrito}Momento de Inércia em y (Iy){fecha_negrito}: {round(self.inercia['y'], 6)} cm⁴
{abre_negrito}Módulo de Resistência em z (Wz){fecha_negrito}: {round(self.modulo_resistencia['z'], 6)} cm³
{abre_negrito}Módulo de Resistência em y (Wy){fecha_negrito}: {round(self.modulo_resistencia['y'], 6)} cm³
{abre_negrito}Raio de Giração em z (iz){fecha_negrito}: {round(self.raio_giracao['z'], 6)} cm
{abre_negrito}Raio de Giração em y (iy){fecha_negrito}: {round(self.raio_giracao['y'], 6)} cm
{abre_negrito}Índice de Esbeltez em z (λz){fecha_negrito}: {round(self.indice_esbeltez['z'], 6)}
{abre_negrito}Índice de Esbeltez em y (λy){fecha_negrito}: {round(self.indice_esbeltez['y'], 6)}

        {abre_negrito}Parte 2 - Resistência de Cálculo

{abre_negrito}Resistência a Compressão (Fc0k){fecha_negrito}: {self.Fc0k} MPa
{abre_negrito}Kmod1, Kmod2, Kmod3{fecha_negrito}: {self.kmods['1']}, {self.kmods['2']}, {self.kmods['3']} 
{abre_negrito}Kmod{fecha_negrito}: {self.kmod}
{abre_negrito}Resistência da Madeira (Fc0d){fecha_negrito}: {self.fc0d} MPa

        {abre_negrito}Parte 3 - Esforços Solicitantes: força normal e momentos fletores

{abre_negrito}Tensão Normal (σNd){fecha_negrito}: {round(self.tensao_normal, 6)} MPa
{abre_negrito}Tensão Momento Fletor em z (σMz){fecha_negrito}: {round(self.tensao_momento_fletor['z'], 6)} MPa
{abre_negrito}Tensão Momento Fletor em y (σMy){fecha_negrito}: {round(self.tensao_momento_fletor['y'], 6)} MPa

{abre_negrito}Verificação Parte 3.1{fecha_negrito}: {round(self.verificacao_parte_1()[1], 6)} < 1
        {abre_negrito}{self.verificacao_parte_1()[0]}{fecha_negrito}

{abre_negrito}Verificação Parte 3.2{fecha_negrito}: {round(self.verificacao_parte_2()[1], 6)} < 1
        {abre_negrito}{self.verificacao_parte_2()[0]}{fecha_negrito}

{self.verificacao_parte_3()}




'''
