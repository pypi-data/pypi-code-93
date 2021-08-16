class CalculadorBarraTracionada:
    
    
    @staticmethod
    def area(largura: float, espessura: float) -> float:
        area_bruta = largura * espessura
        return area_bruta
    
    @staticmethod
    def medida_furos(quantidade_furos: int, diametro_parafuso: float) -> float:
        medida = quantidade_furos * (diametro_parafuso + 0.35)
        return medida
    
    @staticmethod
    def largura_liquida(largura_bruta: float, medida_furos: float) -> float:
        largura = largura_bruta - medida_furos
        return largura
    
    @staticmethod
    def ziguezague(s: float, g: float, quantidade: int) -> float:
        acrescimo = (s**2 / (4 * g)) * quantidade
        return acrescimo
    
    @staticmethod
    def largura_com_ziguezague(largura_bruta: float, medida_furos: float, medida_ziguezagues: int) -> float:
        largura = largura_bruta - medida_furos + medida_ziguezagues
        return largura
    
    @staticmethod
    def resistencia_secao_bruta(area_bruta: float, fy: int or float) -> float: 
        coef_resistencia = 0.9
        
        resistencia = coef_resistencia * area_bruta * 10**-4 * fy * 10**6
        return resistencia
    
    @staticmethod
    def resistencia_secao_furos(secao_critica: float, fu: float or int) -> float:
        coef_resistencia = 0.75
        coef_correcao = 1
        
        resistencia = coef_resistencia * secao_critica * 10**-4 * coef_correcao * fu * 10**6
        return resistencia
        
    @staticmethod
    def esforco_nominal(nd: float) -> float:
        esforco_nominal = nd / 1.4
        return esforco_nominal