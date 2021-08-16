from math import sqrt

class CalculadorLigacao:
    
    @staticmethod
    def calcula_fyd(escoamento_aco):
        fyd = escoamento_aco / 1.15
        return fyd
    
    @staticmethod
    def calcula_kmod(kmods):
        kmod = kmods['1'] * kmods['2'] * kmods['3']
        return kmod
    
    @staticmethod
    def calcula_fc0d(fc0k, kmod):
        fc0d = (kmod * fc0k) / 1.4
        return fc0d
    
    @staticmethod
    def calcula_blim(fyd, fc0d):
        blim = 1.25 * sqrt((fyd / fc0d))
        return blim 
    
    @staticmethod
    def calcula_t_central(espessura):
        t2 = espessura / 2
        return t2
    
    @staticmethod
    def calcula_bef(t, d):
        bef = t / d
        return bef
    
    @staticmethod
    def calcula_rvd_1(bef, blim, t, d, fc0d, fyd):
        if bef <= blim:
            rvd_1 = 0.4 * ((t / 1000)**2 / bef) * fc0d * 1000
        else:
            rvd_1 = 0.625 * ((d / 1000)**2 / blim) * fyd
            
        return rvd_1
    
    @staticmethod
    def calcula_r_ligacao(rvd_1):
        r_ligacao = 16 * rvd_1
        return r_ligacao