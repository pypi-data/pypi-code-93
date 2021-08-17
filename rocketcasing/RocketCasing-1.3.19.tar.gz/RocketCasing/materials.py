"""
Created on Tue Jan 26 19:32:08 2021
@author: Lucas Valentim
"""
#Yield Strength (Fty) Força de Rendimento
#Ultimate Strength (Ftu) Força máxima
#modulo de elasticidade (E) Módulo de elasticidade
#coeficiente de poisson (v) Coeficiente de Poisson
mec_prop={
    'aço c 1010 laminação quente':{
        'Fty':165,
        'Ftu':296,
        'E':200100,
        'v':0.32},
    'aço c 1010 laminação fria':{
        'Fty':414,
        'Ftu':496,
        'E':200100,
        'v':0.32},
    'aço c 1015 laminação quente':{
        'Fty':228,
        'Ftu':379,
        'E':200100,
        'v':0.32},
    'aço c 1015 normalizado':{
        'Fty':241,
        'Ftu':345,
        'E':200100,
        'v':0.32},
    'aço c 1025 laminação quente':{
        'Fty':310,
        'Ftu':462,
        'E':200100,
        'v':0.32},
    'aço c 1025 normalizado':{
        'Fty':331,
        'Ftu':448,
        'E':200100,
        'v':0.32},
    'aço c 1025 laminação fria':{
        'Fty':483,
        'Ftu':586,
        'E':200100,
        'v':0.32},
    'aço inox 304':{
        'Fty':517,
        'Ftu':724,
        'E':186300,
        'v':0.27},
    'aço inox 301':{
        'Fty':517,
        'Ftu':862,
        'E':186300,
        'v':0.27},
    'aço aisi 4130 normalizado MIL-T-6736':{
        'Fty':517,
        'Ftu':655,
        'E':200100,
        'v':0.32},
    'aço aisi 4130 laminação fria MIL-T-6736':{
        'Fty':621,
        'Ftu':690,
        'E':200100,
        'v':0.32},
    'aluminio 6061-t4':{
        'Fty':110,
        'Ftu':207,
        'E':68310,
        'v':0.33},
    'aluminio 6061-t6':{
        'Fty':241,
        'Ftu':290,
        'E':68310,
        'v':0.33},
    'aluminio 6061-t6511 extrusado':{
        'Fty':241,
        'Ftu':290,
        'E':68310,
        'v':0.33},
    'aluminio 2024-t3':{
        'Fty':310,
        'Ftu':455,
        'E':72450,
        'v':0.33},
    'aluminio 2024-t42':{
        'Fty':262,
        'Ftu':427,
        'E':72450,
        'v':0.33},
    'aluminio 7075-t6':{
        'Fty':455,
        'Ftu':531,
        'E':71760,
        'v':0.33},
    'aluminio 7075-t73':{
        'Fty':386,
        'Ftu':455,
        'E':71760,
        'v':0.33},
    'policloreto de vinila':{
        'Fty':41,
        'Ftu':51,
        'E':2898,
        'v':0.41},
    'acrilonitrila butadieno estireno':{
        'Fty':35,
        'Ftu':41,
        'E':2001,
        'v':0.0},
    'papelão':{
        'Fty':0,
        'Ftu':14,
        'E':0,
        'v':0.0},
    'tubo de metal eletrico anelado':{
        'Fty':296,
        'Ftu':393,
        'E':200100,
        'v':0.32},
    'tubo de metal eletrico laminado':{
        'Fty':310,
        'Ftu':414,
        'E':200100,
        'v':0.32}
    }
'''

b=p['Fty']/p['Ftu']
print("Razão da força do material: ",'{:.5f}'.format(b))

B=(9.5833*b**4)+(-33.528*b**3)+(44.929*b**2)+(-28.479*b)+8.6475
print("Fator de ruptura: ",'{:.5f}'.format(B))
'''