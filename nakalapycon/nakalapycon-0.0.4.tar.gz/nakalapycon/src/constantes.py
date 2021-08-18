# -*- coding: utf-8 -*-
"""
Created on Tue Jan  5 10:17:57 2021

@author: Michael Nauge, Université de Poitiers
"""



# un dictionnaire permettant de faciliter l'attribution 
# pour des humains d'un data_type
# nous conseillons de passer par la fonction vocabTypeGetUriByKey(key)
# plutôt que de l'utiliser directement
VOCABTYPE = {
    
    # types classiques (dublincore)
    #-------------------------------------------------
    "text":"http://purl.org/coar/resource_type/c_18cf",
    "image":"http://purl.org/coar/resource_type/c_c513",
    "video":"http://purl.org/coar/resource_type/c_12ce",
    "sound":"http://purl.org/coar/resource_type/c_18cc",
    
    # Attention : lorsque l'on dépose un fichier JPG contenant un texte manuscrit ou tapuscrit
    # il faut choisir le type text plutôt que le type image    
    # c'est probablement là le principal intérêt de préciser cette information 
    # à chaque data nakala car en général l'extension du fichier suffit
    # à connaitre le type
    #-------------------------------------------------
    
    
    # types fils des types classiques ou plus précis ou rares
    # mais dont l'utilisation ne fait pas toujours concensus dans certaines
    # communautés disciplinaires
    #-------------------------------------------------
    "journal article":"http://purl.org/coar/resource_type/c_6501",
    "conference poster":"http://purl.org/coar/resource_type/c_6670",
    "conference object":"http://purl.org/coar/resource_type/c_c94f",
    "learning object":"http://purl.org/coar/resource_type/c_e059",
    "book":"http://purl.org/coar/resource_type/c_2f33",
    "map":"http://purl.org/coar/resource_type/c_12cd",
    "dataset":"http://purl.org/coar/resource_type/c_ddb1",
    "software":"http://purl.org/coar/resource_type/c_5ce6",
    "other":"http://purl.org/coar/resource_type/c_1843",
    "ArchiveMaterial":"http://purl.org/library/ArchiveMaterial",
    "Collection":"http://purl.org/ontology/bibo/Collection",
    "bibliography":"http://purl.org/coar/resource_type/c_86bc",
    "Series":"http://purl.org/ontology/bibo/Series",
    "book review":"http://purl.org/coar/resource_type/c_ba08",
    "manuscript":"http://purl.org/coar/resource_type/c_0040",
    "letter":"http://purl.org/coar/resource_type/c_0857", # A brief description of important new research, also known as “communication”. 
    "report":"http://purl.org/coar/resource_type/c_93fc",
    "periodical":"http://purl.org/coar/resource_type/c_2659", # This concept is deprecated 
    "preprint":"http://purl.org/coar/resource_type/c_816b",
    "review":"http://purl.org/coar/resource_type/c_efa0",
    "musical notation":"http://purl.org/coar/resource_type/c_18cw",
    "SurveyDataSet":"https://w3id.org/survey-ontology#SurveyDataSet",    
    "thesis":"http://purl.org/coar/resource_type/c_46ec",
    "website":"http://purl.org/coar/resource_type/c_7ad9",
    "data paper":"http://purl.org/coar/resource_type/c_beb9",
    "interactive resource":"http://purl.org/coar/resource_type/c_e9a0"
    }




def vocabTypeGetUriByKey(key):
    """
    Obtenir l'uri associé à un nom de concept
    exemple: vocabTypeGetUriByKey(key="image")
    Doit retourner : "http://purl.org/coar/resource_type/c_c513"
    
    Nous conseillons d'utiliser cette fonction 
    plutôt que directement le dictionnaire VOCABTYPE car 
    cett fonction se charge de vérifier l'existance de la key passé en paramètre
    et évite une levée d'exception bloquante. Dans ce cas l'uri retourné sera
    "unknown by nakalapycon or nakala"
    

    Parameters
    key : str
    	une clé 
        
    Returns
    -------
    uri : str
        l'Uri d'un concept datatype reconnu par nakala,
        si la clé f
        

    """   
    
    value = "unknown by nakalapycon"
    
    if key in VOCABTYPE:
        return VOCABTYPE[key]
    
    return value




def vocabTypeGetKeyByUri(uri):
    """
    Obtenir un version compréhensible par un humain du concept
    qui se cache derrière une uri de concept nakala
    
    

    Parameters
    ----------
    uri : str
        une uri présente dans VOCABTYPE

    Returns
    -------
    key : str
        le preflabel du concept associé à l'uri

    """
    
    value = "unknown by nakalapycon"
 
    keys = [k for k, v in VOCABTYPE.items() if v == uri]
    
    
    if len(keys)==1:
        return keys[0]

    return value

    