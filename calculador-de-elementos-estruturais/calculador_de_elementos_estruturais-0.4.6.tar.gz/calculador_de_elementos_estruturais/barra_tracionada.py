from .pegador_parafusada import PegadorParafusada
from .calculador_barra_tracionada import CalculadorBarraTracionada
from .informacoes import request_resistencia_chapas

class BarraTracionada:
    
    
    def __init__(self):
        
        self.largura_bruta = PegadorParafusada.pega_medida('Digite a largura da peça(bg) em mm. ')
        self.espessura = PegadorParafusada.pega_espessura('Digite a espessura da peça. ')
        self.area_bruta = CalculadorBarraTracionada.area(self.largura_bruta, self.espessura)
        
        self.diametro_parafusos = PegadorParafusada.pega_diametro_parafuso()
        medida_parafusos = CalculadorBarraTracionada.medida_furos(2, self.diametro_parafusos)
        self.largura_liquida_1 = CalculadorBarraTracionada.largura_liquida(self.largura_bruta, medida_parafusos)
        self.area_liquida_1 = CalculadorBarraTracionada.area(self.largura_liquida_1, self.espessura)
        
        self.s = PegadorParafusada.pega_medida('Digite a medida de s em mm. ')
        self.g = PegadorParafusada.pega_medida('Digite a medida de g em mm. ')
        self.ziguezague_1 = CalculadorBarraTracionada.ziguezague(self.s, self.g, 1)
        self.largura_liquida_2 = CalculadorBarraTracionada.largura_com_ziguezague(self.largura_bruta, medida_parafusos, self.ziguezague_1)
        self.area_liquida_2 = CalculadorBarraTracionada.area(self.largura_liquida_2, self.espessura)
        
        medida_parafusos = CalculadorBarraTracionada.medida_furos(3, self.diametro_parafusos)
        self.ziguezague_2 = CalculadorBarraTracionada.ziguezague(self.s, self.g, 2)
        self.largura_liquida_3 = CalculadorBarraTracionada.largura_com_ziguezague(self.largura_bruta, medida_parafusos, self.ziguezague_2)
        self.area_liquida_3 = CalculadorBarraTracionada.area(self.largura_liquida_3, self.espessura)
        
        self.secao_critica = self.escolhe_menor_valor(self.area_liquida_1, self.area_liquida_2, self.area_liquida_3)
        
        especificacao_peca = PegadorParafusada.pega_especificacao_chapa()
        self.fy, self.fu = request_resistencia_chapas(especificacao_peca) if especificacao_peca != 'Outro' else PegadorParafusada.pega_fy_e_fu('a peça')
        self.resistencia_bruta = CalculadorBarraTracionada.resistencia_secao_bruta(self.area_bruta, self.fy)
        self.resistencia_furos = CalculadorBarraTracionada.resistencia_secao_furos(self.secao_critica, self.fu)
        
        self.resistencia_peca = self.escolhe_menor_valor(self.resistencia_bruta, self.resistencia_furos)
        
        self.nd = self.resistencia_peca
        
        self.esforco_nominal = CalculadorBarraTracionada.esforco_nominal(self.nd)
        
        print(self)
        
        
    @staticmethod
    def escolhe_menor_valor(*valores: float):
        return min(valores)
    
    def __str__(self):
        abre_negrito = '\033[1m'
        fecha_negrito = '\033[0m'
        n = abre_negrito
        _n = fecha_negrito
        
        mensagem = f'''{n}      Barra Tracionada        

{n}1) Cálculo da área bruta (Ag):

{n}Área bruta (Ag):{_n} {round(self.area_bruta, 6)} cm²

{n}2) Cálculo das áreas líquidas nas seções I, II e III

{n}• Seção I (seção reta)

{n}Largura líquida (bn):{_n} {round(self.largura_liquida_1, 6)} cm
{n}Área Líquida (An):{_n} {round(self.area_liquida_1, 6)} cm²

{n}• Seção II (seção ziguezague)

{n}Largura líquida (bn):{_n} {round(self.largura_liquida_2, 6)} cm
{n}Área Líquida (An):{_n} {round(self.area_liquida_2, 6)} cm²

{n}• Seção III (seção ziguezague)

{n}Largura líquida (bn):{_n} {round(self.largura_liquida_3, 6)} cm
{n}Área Líquida (An):{_n} {round(self.area_liquida_3, 6)} cm²

{n}• Seção Crítica:{_n} {round(self.secao_critica, 6)} cm²

{n}3) Resistência da peça à tração

{n}• Na seção bruta

{n}Resistência da peça (ΦNn):{_n} {round(self.resistencia_bruta, 6)} N

{n}• Na seção com furos

{n}Resistência da peça (ΦNn):{_n} {round(self.resistencia_furos, 6)} N

{n}• Resistência da peça:{_n} {round(self.resistencia_peca, 6)} N

{n}4)Maior esforço suportado pela peça (Nd)

{n}Nd:{_n} {round(self.nd, 6)} N

{n}5) Maior esforço nominal suportado pela peça (N)

{n}N:{_n} {round(self.esforco_nominal, 6)} N
'''

        return mensagem
    