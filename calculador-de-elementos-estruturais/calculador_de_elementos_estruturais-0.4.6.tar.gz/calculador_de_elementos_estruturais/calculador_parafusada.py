from math import pi

class CalculadorParafusada:
    '''cantoneira'''    
    @staticmethod
    def calcula_area_bruta_cantoneira(medida_aba, espessura):
        area = (2 * (medida_aba) - (espessura)) * (espessura)
        return area
    
    @staticmethod
    def calcula_largura_bruta_cantoneira(medida_aba, espessura):
        largura_bruta = 2 * (medida_aba) - (espessura)
        return largura_bruta
    
    @staticmethod
    def calcula_largura_liquida(largura_bruta, diametro_parafuso, diametro_cabeca_parafuso):
        largura_liquida = largura_bruta - (diametro_parafuso + diametro_cabeca_parafuso)
        return largura_liquida

    @staticmethod
    def calcula_area_liquida(largura_liquida, espessura):
        area_liquida = largura_liquida * espessura
        return area_liquida
    
    @staticmethod
    def calcula_resistencia_tracao_secao_bruta(area_bruta, fy):
        coef_resistencia = 0.9
        resistencia = coef_resistencia * (area_bruta * 10**-4) * (fy * 10**6)
        return resistencia
    
    @staticmethod
    def calcula_resistencia_tracao_secao_liquida(area_liquida, fu, coef_reducao=0.75):
        coef_resistencia = 0.75
        area_reduzida = area_liquida * coef_reducao
        resistencia = coef_resistencia * (area_reduzida * 10**-4) * (fu * 10**6)
        return resistencia
    
    '''gusset'''
    @staticmethod
    def calcula_area_bruta_gusset(medida, espessura):
        area = medida * espessura
        return area
    
    '''pressão de contato na cantoneira'''
    @staticmethod
    def calcula_pressao_centro_furos(dist_furos, diametro_parafuso):
        pressao_centro_furos = (dist_furos / diametro_parafuso) - 0.5
        return pressao_centro_furos if pressao_centro_furos <= 3 else 10
    
    @staticmethod
    def calcula_pressao_centro_furo_bordo(e, diametro_parafuso):
        pressao_centro_furo_bordo = e / diametro_parafuso
        return pressao_centro_furo_bordo
    
    @staticmethod
    def calcula_esmagamento_chapa(rasgamento_chapa, numero_parafusos, diametro_parafuso, espessura_cantoneira, fu):
        coef_resistencia = 0.75
        resistencia = coef_resistencia * rasgamento_chapa * \
                      numero_parafusos * diametro_parafuso * \
                      espessura_cantoneira * 10**-4 * \
                      fu * 10**6
        return resistencia
    
    @staticmethod
    def calcula_resistencia_cisalhamento_parafusos(diametro_parafuso, fu, numero_parafusos):
        area_parafuso = (pi * diametro_parafuso**2) / 4
        coef_resistencia_forca_cortante = 0.6
        area_parafuso_efetiva = 0.7 * area_parafuso
        tu = 0.6 * fu
        
        resistencia_cisalhamento_parafusos = coef_resistencia_forca_cortante * numero_parafusos * \
                                             area_parafuso_efetiva * 10**-4 * \
                                             tu * 10**6
        return resistencia_cisalhamento_parafusos
    
    @staticmethod
    def calcula_maximo_esforco_nominal(esforco):
        coef_seguranca = 1.4
        maximo_esforco_nominal = esforco / coef_seguranca
        return maximo_esforco_nominal
    
    