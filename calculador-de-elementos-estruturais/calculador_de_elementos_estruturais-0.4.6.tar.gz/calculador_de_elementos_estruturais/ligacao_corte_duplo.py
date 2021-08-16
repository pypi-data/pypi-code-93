from .pegador_ligacao_dupla import PegadorLigacaoDupla
from .calculador_ligacao_dupla import CalculadorLigacaoDupla

class LigacaoCorteDuplo:
    
    
    def __init__(self, enunciado=None):
        self.classe_central = PegadorLigacaoDupla.pega_classe_central(enunciado)
        self.espessura_central = PegadorLigacaoDupla.pega_espessura_central(enunciado)
        self.classe_lateral = PegadorLigacaoDupla.pega_classe_lateral(enunciado)
        self.espessura_lateral = PegadorLigacaoDupla.pega_espessura_lateral(enunciado)
        self.escoamento_aco = PegadorLigacaoDupla.pega_escoamento_aco(enunciado)
        self.duracao = PegadorLigacaoDupla.pega_duracao(enunciado)
        self.classe_umidade = PegadorLigacaoDupla.pega_classe_umidade(enunciado)
        self.categoria = PegadorLigacaoDupla.pega_categoria(enunciado)
        self.quantidade_pinos = PegadorLigacaoDupla.pega_quantidade_pinos(enunciado)
        self.diametro_pinos = PegadorLigacaoDupla.pega_diametro_pinos(enunciado)
        self.fc0k_central = PegadorLigacaoDupla.pega_Fc0k(self.classe_central)
        self.fc0k_lateral = PegadorLigacaoDupla.pega_Fc0k(self.classe_lateral)
        self.kmods = PegadorLigacaoDupla.pega_kmods(self.duracao, self.classe_umidade, self.categoria)
        
        self.fyd = CalculadorLigacaoDupla.calcula_fyd(self.escoamento_aco)
        self.kmod = CalculadorLigacaoDupla.calcula_kmod(self.kmods)
        self.fc0d_central = CalculadorLigacaoDupla.calcula_fc0d(self.fc0k_central, self.kmod)
        self.fc0d_lateral = CalculadorLigacaoDupla.calcula_fc0d(self.fc0k_lateral, self.kmod)
        self.blim_central = CalculadorLigacaoDupla.calcula_blim(self.fyd, self.fc0d_central)
        self.blim_lateral = CalculadorLigacaoDupla.calcula_blim(self.fyd, self.fc0d_lateral)
        self.t_lateral = self.espessura_lateral
        self.t_central = CalculadorLigacaoDupla.calcula_t_central(self.espessura_central)
        self.d = self.diametro_pinos
        self.bef_central = CalculadorLigacaoDupla.calcula_bef(self.t_central, self.d)
        self.bef_lateral = CalculadorLigacaoDupla.calcula_bef(self.t_lateral, self.d)
        self.rvd_1_central = CalculadorLigacaoDupla.calcula_rvd_1(self.bef_lateral, self.blim_central, self.t_lateral, 
                                                             self.d, self.fc0d_central, self.fyd)
        self.rvd_1_lateral = CalculadorLigacaoDupla.calcula_rvd_1(self.bef_central, self.blim_lateral, self.t_central, 
                                                             self.d, self.fc0d_lateral, self.fyd)
        self.r_ligacao_central = CalculadorLigacaoDupla.calcula_r_ligacao(self.quantidade_pinos, self.rvd_1_central)
        self.r_ligacao_lateral = CalculadorLigacaoDupla.calcula_r_ligacao(self.quantidade_pinos, self.rvd_1_lateral)
        self.fd = self.faz_verificacao()
        print(self)
        
    def faz_verificacao(self):
        if self.r_ligacao_central < self.r_ligacao_lateral:
            return self.r_ligacao_central
        return self.r_ligacao_lateral
    
    def __str__(self):
        abre_negrito = '\033[1m'
        fecha_negrito = '\033[0m'
        
        return f'''{abre_negrito}       Material do Pino
    
{abre_negrito}Resistência do aço (fyd){fecha_negrito}: {round(self.fyd, 3)} MPa

{abre_negrito}      Kmods

{abre_negrito}Kmod1{fecha_negrito}: {self.kmods['1']}   |   {abre_negrito}Kmod{fecha_negrito}: {round(self.kmod, 4)}
{abre_negrito}Kmod2{fecha_negrito}: {self.kmods['2']}   |
{abre_negrito}Kmod3{fecha_negrito}: {self.kmods['3']}   |

{abre_negrito}      Resistência de Cálculo

{abre_negrito}fc0k central{fecha_negrito}: {self.fc0k_central} MPa
{abre_negrito}fc0d central{fecha_negrito}: {round(self.fc0d_central, 3)} MPa
{abre_negrito}fc0k lateral{fecha_negrito}: {self.fc0k_lateral} MPa
{abre_negrito}fc0d central{fecha_negrito}: {round(self.fc0d_lateral, 3)} MPa

{abre_negrito}      ßlim

{abre_negrito}ßlim central{fecha_negrito}: {round(self.blim_central, 3)} 
{abre_negrito}ßlim lateral{fecha_negrito}: {round(self.blim_lateral, 3)}

{abre_negrito}      Características Geométricas da madeira e do aço

{abre_negrito}Espessura das peças laterais (t1){fecha_negrito}: {self.t_lateral} mm
{abre_negrito}Espessura da peça central para uma seção de corte (t2){fecha_negrito}: {self.t_central} mm
{abre_negrito}Diâmetro do pino (d){fecha_negrito}: {self.d} mm

{abre_negrito}      ßef

{abre_negrito}ßef lateral{fecha_negrito}: {round(self.bef_lateral, 3)}
{abre_negrito}ßef central{fecha_negrito}: {round(self.bef_central, 3)}

{abre_negrito}      Rvd_1

{abre_negrito}Rvd_1 central{fecha_negrito}: {round(self.rvd_1_central, 3)} kN
{abre_negrito}Rvd_1 lateral{fecha_negrito}: {round(self.rvd_1_lateral, 3)} kN

{abre_negrito}      R ligacao

{abre_negrito}R1ligação{fecha_negrito}: {round(self.r_ligacao_central, 3)} kN
{abre_negrito}R2ligação{fecha_negrito}: {round(self.r_ligacao_lateral, 3)} kN


{abre_negrito}Valor de cálculo para Fd{fecha_negrito}: {round(self.fd, 3)} kN
'''
