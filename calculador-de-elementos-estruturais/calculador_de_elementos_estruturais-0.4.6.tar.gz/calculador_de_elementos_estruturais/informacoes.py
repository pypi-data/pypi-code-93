from pandas import DataFrame

informacoes_classe = {'Classe': ('C20', 'C30', 'C40', 'C60'),
                      'Fc0k': (20, 30, 40, 60),
                      'Ec0m': (9500, 14500, 19500, 24500)}
tabela_classe = DataFrame(informacoes_classe, index=(1, 2, 3, 4))

informacoes_kmod1 = {'Permanente': 0.6,
                     'Longa Duração': 0.7,
                     'Média Duração': 0.8,
                     'Curta Duração': 0.9,
                     'Instantânea': 1.1}

duracoes = ('Permanente', 'Longa Duração', 'Média Duração', 'Curta Duração', 'Instantânea')

informacoes_kmod2 = {'1': 1,
                     '2': 1,
                     '3': 0.8,
                     '4': 0.8}

informacoes_kmod3 = {'1ª Categoria': 1, '2ª Categoria': 0.8}

categorias = ('1ª Categoria', '2ª Categoria')

dict_resistencia_dos_parafusos = {'fy': (250,235,635,560,640,895,900),
                             'fu': (415,400,825,725,800,1035,100),}

def request_resistencia_parafuso(especificacao: str, diametro: float) -> tuple:
    resistencia_dos_parafusos = DataFrame(dict_resistencia_dos_parafusos, 
                                      index=('ASTM A307', 'ISO 898-1',
                                             'ASTM A325 <= 24', 'ASTM A325 > 24',
                                             'ISO 4016 8.8', 'ASTM A490',
                                             'ISO 4016 10.9'))
    
    df = resistencia_dos_parafusos
    
    if especificacao == 'ASTM A325':
        if diametro > 2.4:
            fu = df.loc['ASTM A325 > 24'].fu
            fy = df.loc['ASTM A325 > 24'].fy
        else:
            fu = df.loc['ASTM A325 <= 24'].fu
            fy = df.loc['ASTM A325 <= 24'].fy
    else:
        fu = df.loc[especificacao].fu
        fy = df.loc[especificacao].fy
        
    return fy, fu

def request_resistencia_chapas(especificacao: str) -> tuple:
    dict_resistencia_chapas = {'fy': (250,350,350,415,310,340,380,410,450),
                           'fu': (400,50,485,520,410,450,480,520,550)}

    resistencia_chapas = DataFrame(dict_resistencia_chapas, 
                               index=('MR 250', 'AR 350', 
                                      'AR 350 COR', 'AR 415',
                                      'F-32/Q-32', 'F-35/Q-35',
                                      'Q-40', 'Q-42', 'Q-45'))
    
    fu = resistencia_chapas.loc[especificacao].fu
    fy = resistencia_chapas.loc[especificacao].fy
    
    return fy, fu

def request_area_cantoneira(comprimento: float, espessura: float) -> float:
    c_7_62 = {0.476: 7.03, 0.635: 9.29, 0.794: 11.48,
              0.952: 13.61, 1.111: 15.67, 1.27: 17.74}
     
    c_10_16 = {0.635: 12.51, 0.794: 15.48, 0.952: 18.45,
               1.111: 21.35, 1.27: 24.19, 1.429: 26.96,
               1.588: 29.73}
    
    c_12_7 = {0.952: 23.29, 1.27: 30.64, 1.588: 37.8,
              1.905: 44.76}
    
    c_15_24 = {0.952: 28.12, 1.27: 37.09, 1.588: 45.86, 
               1.905: 54.44, 2.222: 62.76}
    
    comprimentos_e_espessuras = {7.62: c_7_62,
                                              10.16: c_10_16,
                                              12.7: c_12_7,
                                              15.24: c_15_24}
    
    espessuras_selecionadas = comprimentos_e_espessuras[comprimento]
    area_bruta = espessuras_selecionadas[espessura]
    
    return area_bruta