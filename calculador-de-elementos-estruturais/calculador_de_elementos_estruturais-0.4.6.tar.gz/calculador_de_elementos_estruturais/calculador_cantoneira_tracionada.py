from .calculador_barra_tracionada import CalculadorBarraTracionada

class CalculadorCantoneiraTracionada(CalculadorBarraTracionada):
    
    
    @staticmethod
    def largura_efetiva(largura: float, espessura: float) -> float:
        largura_efetiva = 2 * largura - espessura
        return largura_efetiva
    