# -*- coding: utf-8 -*-
"""
Created on Fri Jul 16 09:28:54 2021

@author: mnauge
"""

class NklTarget:
    """
    Une classe permetant de définir le Nakala cible.
    En effet,  il existe :
        Nakala_production (https://nakala.fr)
        Nakala_test (https://test.nakala.fr)
        
    Pour cette cible Nkala, il est possible d'indiquer sa ApiKey pour faire
    des actions qui necessitent des droits.
    
    """
    
    # les urls de Nakala_test
    BASE_URL = "https://test.nakala.fr"
    API_URL = "https://apitest.nakala.fr"
    #la ApiKey
    API_KEY_NKL = ""

    def __init__(self, isNakalaProd=False, apiKey = "01234567-89ab-cdef-0123-456789abcdef"):
        
        # par défaut on considère que l'on travail sur la version de test.
        # si on travail sur la version de production
        # il faut changer les URL
        if isNakalaProd:
            # les urls de Nakala_production
            self.BASE_URL = "https://nakala.fr"
            self.API_URL = "https://api.nakala.fr"
        
        # on met à jour la ApiKey avec la valeur donnée en paramètre entrant
        self.API_KEY_NKL = apiKey
            
        
    def apiKey_isEmpty(self):
        """
        Savoir si la ApiKey a été renseigné.
        Seul une partie des actions Get sur données public peuvent s'effectuer
        sans ApiKey. 
            
        Returns
        -------
        dfData : BOOL

    
        """   
        if self.API_KEY_NKL == "":
            return True
        else:
            return False
        
