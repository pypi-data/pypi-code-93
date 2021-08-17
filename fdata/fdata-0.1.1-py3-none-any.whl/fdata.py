import pandas as pd
import csv
import time
import itertools

class_dfs = []
missing_dfs = []
positives = []
indices = []
grouped_list = []

final_dfs = []
miss_dfs = []
final_storage_list = []
final_missing_storage_list = []

additions = []
custom_dfs = []

pt_list = []
outs_code_list = []

reactions_by_id = {}
reactions_by_id_list = []
final_reacs = []

outcomes_by_id = {}
outcomes_by_id_list = []
final_outs = []

counter_list = []
counter_list_2 = []

def sorter(drug_file_path,top_indices=None):
    
    grouped_list = []
    drug_file = pd.read_csv(drug_file_path, delimiter='$')

    drug_file.prod_ai = drug_file.prod_ai.astype(str)
    drug_file.prod_ai = drug_file.prod_ai.map(lambda x: x.replace('.', ''))
    
    index = drug_file[drug_file.prod_ai != 'nan'].index
    nan_index = drug_file[drug_file.prod_ai == 'nan'].index
    
    present = drug_file.prod_ai.loc[index]
    present_primaryids = drug_file.primaryid.loc[index]
    
    absent = drug_file.prod_ai.loc[nan_index]
    absent_primaryids = drug_file.primaryid.loc[nan_index]
    
    class_df = pd.DataFrame(columns=['primaryid', 'prod_ai', 'class_id', 'class', 'indication'])
    missing_df = pd.DataFrame(columns=['primaryid', 'prod_ai', 'class_id', 'class', 'indication'])
    
    class_df.primaryid = present_primaryids
    class_df.prod_ai = present
    
    missing_df = absent_primaryids
    missing_df.prod_ai = absent
    
    if top_indices == None:
        top_indices = -1
    grouped_list = [class_df[class_df.loc[:,'prod_ai'] == x].index for x in class_df.prod_ai.value_counts()[:top_indices].index]
    class_df = class_df.loc[itertools.chain.from_iterable(grouped_list)]
    
    
    class_dfs.append([class_df])
    missing_dfs.append([missing_df])
    positives.append([present])
    indices.append([index])
    
    print('Check "class_dfs", "missing_dfs", "positives" and "indices" for output')

def map_1(class_df, array_split):
    start_time = time.time()
    
    for x,y in zip(class_df.prod_ai,class_df.index):
        if x.endswith('COSMETICS'):
            class_df.loc[y, 'class_id'] = 300
            class_df.loc[y, 'class'] = 'cosmetic'
            class_df.loc[y, 'indication'] = 'non-prescription use'
        elif x.endswith('MAB') or x.startswith('GALCANEZUMAB-GNLM') or x.startswith('EMGALITY')or x.startswith('COSENTYX') or x.startswith('DUPIXENT') or x.endswith('DUPIXENT') or x.startswith('XOLAIR') or x.startswith('ACTEMRA') or x.startswith('STELARA'):
            class_df.loc[y, 'class_id'] = 301
            class_df.loc[y, 'class'] = 'monoclonal_antibody'
            class_df.loc[y, 'indication'] = 'autoimmune diseases'
        
        elif x.startswith('ADAPALENE'):
            class_df.loc[y, 'class_id'] = 302
            class_df.loc[y, 'class'] = 'retinoid'
            class_df.loc[y, 'indication'] = 'acne vulgaris'
        elif x.startswith('PREDNIS*') or x.endswith('*LONE') or x.endswith('*SONE') or x.startswith('MOMETASONE FUROATE') or x.startswith('FLUTICASONE PROPIONATE') or x.startswith('FLONASE'):
            class_df.loc[y, 'class_id'] = 38
            class_df.loc[y, 'class'] = 'corticosteroid'
            class_df.loc[y, 'indication'] = 'immunosupressant'
        elif x.startswith('ACETAMINOPHEN') or x.startswith('TYLENOL'):
            class_df.loc[y, 'class_id'] = 52
            class_df.loc[y, 'class'] = 'analgesic'
            class_df.loc[y, 'indication'] = 'fever reducer'
        elif x.startswith('ASPIRIN') or x.startswith('IBUPROFEN') or x.startswith('MELOXICAM') or x.startswith('MOBIC') or x.endswith('FENAC') or x.endswith('PROFEN') or x.startswith('CELECOXIB') or x.startswith('CELEBREX') or x.startswith('NAPROXEN') or x.startswith('NAPROSYN'):
            class_df.loc[y, 'class_id'] = 55
            class_df.loc[y, 'class'] = 'nonsteroidal anti-inflammatory drug'
            class_df.loc[y, 'indication'] = 'fever reducer, inflammation, pain management'
        elif x.endswith('STATIN', 0, 12) or x.endswith('STATIN'):
            class_df.loc[y, 'class_id'] = 4
            class_df.loc[y, 'class'] = 'HMG-CoA reductase inhibitor'
            class_df.loc[y, 'indication'] = 'hyperlipidemia'
        elif x.endswith('IDE'):
            if x.endswith('HYDROCHLORIDE'):
                pass
            else:
                class_df.loc[y, 'class_id'] = 20
                class_df.loc[y, 'class'] = 'loop diuretics'
                class_df.loc[y, 'indication'] = 'hypertension'
        elif x.startswith('METHOTREXATE') or x.startswith('CYTARABINE') or x.startswith('FLUDARABINE PHOSPHATE') or x.startswith('FLUDARA'):
            class_df.loc[y, 'class_id'] = 39
            class_df.loc[y, 'class'] = 'antimetabolites'
            class_df.loc[y, 'indication'] = 'cancer treatment'
        elif x.startswith('AVONEX') or x.startswith('INTERFERON BETA-1A'):
            class_df.loc[y, 'class_id'] = 44
            class_df.loc[y, 'class'] = 'interferon'
            class_df.loc[y, 'indication'] = 'multiple sclerosis'
        elif x.startswith('GABAPENTIN') or x.startswith('LYRICA') or x.startswith('PREGABALIN') or x.startswith('BACLOFEN'):
            class_df.loc[y, 'class_id'] = 45
            class_df.loc[y, 'class'] = 'GABA analogue'
            class_df.loc[y, 'indication'] = 'anticonvulsant, fibromyalgia, nerve pain'
        elif x.startswith('METFORMIN'):
            class_df.loc[y, 'class_id'] = 62
            class_df.loc[y, 'class'] = 'biguanides'
            class_df.loc[y, 'indication'] = 'diabetic management'
        elif x.startswith('AMLODIPINE'):
            class_df.loc[y, 'class_id'] = 46
            class_df.loc[y, 'class'] = 'calcium channel blocker'
            class_df.loc[y, 'indication'] = 'hypertension, chest pain'
        elif x.startswith('INFLECTRA') or x.startswith('INFLIXIMAB-DYYB') or x.startswith('HUMIRA') or x.startswith('REMICADE') or x.endswith('INFLIXIMAB') or x.startswith('CERTOLIZUMAB PEGOL') or x.startswith('CIMZIA'):
            class_df.loc[y, 'class_id'] = 41
            class_df.loc[y, 'class'] = 'TNF blocking agent'
            class_df.loc[y, 'indication'] = 'autoimmune diseases'
        elif x.startswith('XARELTO') or x.startswith('WARFARIN') or x.startswith('RIVAROXABAN'):
            class_df.loc[y, 'class_id'] = 40
            class_df.loc[y, 'class'] = 'anticoagulant' 
            class_df.loc[y, 'indication'] = 'blood clots'
        elif x.startswith('ENBREL') or x.startswith('ETANERCEPT'):
            class_df.loc[y, 'class_id'] = 42
            class_df.loc[y, 'class'] = 'TNF inhibitor'
            class_df.loc[y, 'indication'] = 'autoimmune diseases'
        elif x.startswith('ELIQUIS') or x.startswith('APIXABAN'):
            class_df.loc[y, 'class_id'] = 68
            class_df.loc[y, 'class'] = 'factor Xa inhibitor anticoagulant'
            class_df.loc[y, 'indication'] = 'nonvalvular atrial fibrilation'
        elif x.startswith('OTEZLA') or x.startswith('APREMILAST') or x.startswith('SILDENAFIL CITRATE'):
            class_df.loc[y, 'class_id'] = 54
            class_df.loc[y, 'class'] = 'phosphodiesterase inhibitor'
            class_df.loc[y, 'indication'] = 'autoimmune diseases, erectile dysfunction'
        elif x.startswith('PROAIR HFA') or x.startswith('ALBUTEROL SULFATE'):
            class_df.loc[y, 'class_id'] = 79
            class_df.loc[y, 'class'] = 'beta-2 adrenergic agonist'
            class_df.loc[y, 'indication'] = 'asthma'    
        elif x.startswith('SYNTHROID') or x.startswith('LEVOTHYROXINE') or x.startswith('TESTOSTERONE') or x.startswith('ESTROGENS, CONJUGATED') or x.startswith('ETONOGESTREL') or x.startswith('NEXPLANON') or x.startswith('IMPLANON') or x.startswith('MELATONIN') or x.startswith('ESTRADIOL') or x.startswith('ESTRACE') or x.endswith('TROPIN') or x.startswith('LEVONORGESTREL') or x.startswith('TESTOSTERONE CYPIONATE') or x.startswith('DEPO-TESTOSTERONE'):
            class_df.loc[y, 'class_id'] = 70
            class_df.loc[y, 'class'] = 'hormone'
            class_df.loc[y, 'indication'] = 'hormone deficiency'    
        elif x.endswith('PRIL'):
            class_df.loc[y, 'class_id'] = 2
            class_df.loc[y, 'class'] = 'ACE_inhibitor'
            class_df.loc[y, 'indication'] = 'hypertenstion'    
        elif x.startswith('ORENCIA') or x.startswith('ABATACEPT') or x.startswith('GLATIRAMER ACETATE') or x.startswith('REVLIMID') or x.startswith('LENALIDOMIDE'):
            class_df.loc[y, 'class_id'] = 50
            class_df.loc[y, 'class'] = 'immunomodulator'
            class_df.loc[y, 'indication'] = 'autoimmune diseases'   
        elif x.startswith('PACLITAXEL') or x.startswith('TAXOL') or x.startswith('VINCRISTINE SULFATE') or x.startswith('DOCETAXEL') or x.startswith('TAXOTERE'):
            class_df.loc[y, 'class_id'] = 99
            class_df.loc[y, 'class'] = 'antimicrotubule agent'
            class_df.loc[y, 'indication'] = 'cancer treatment'   
        elif x.startswith('PROGRAF') or x.startswith('TACROLIMUS'):
            class_df.loc[y, 'class_id'] = 81
            class_df.loc[y, 'class'] = 'immunosuppressant'
            class_df.loc[y, 'indication'] = 'prophylaxis of organ rejection'
        elif x.startswith('SINEMET') or x.startswith('CARBIDOPA\LEVODOPA') or x.startswith('LEVODOPA'):
            class_df.loc[y, 'class_id'] = 84
            class_df.loc[y, 'class'] = 'decarboxylase inhibitor, CNS agent'
            class_df.loc[y, 'indication'] = 'parkinsons disease'    
        elif x.startswith('LANTUS') or x.startswith('INSULIN GLARGINE') or x.startswith('INSULIN NOS') or x.startswith('INSULIN ASPART') or x.startswith('NOVOLOG')or x.startswith('INSULIN HUMAN') or x.startswith('MYXREDLIN') or x.startswith('HUMALOG') or x.startswith('INSULIN LISPRO'): 
            class_df.loc[y, 'class_id'] = 82
            class_df.loc[y, 'class'] = 'human insulin analog'
            class_df.loc[y, 'indication'] = 'glycemic management, T1 diabetes, T2 diabetes'    
        elif x.endswith('AZEPAM') or x.endswith('ZOLAM'):
            class_df.loc[y, 'class_id'] = 5
            class_df.loc[y, 'class'] = 'benzodiazepine'
            class_df.loc[y, 'indication'] = 'anxiety'            
        elif x.endswith('IUM') or x.endswith('URONIUM'):
            class_df.loc[y, 'class_id'] = 23
            class_df.loc[y, 'class'] = 'nondepolarizing paralytics'
            class_df.loc[y, 'indication'] = 'anesthesia'          
        elif x.startswith('XELJANZ') or x.startswith('TOFACITINIB') or x.startswith('IMATINIB MESYLATE') or x.startswith('EVEROLIMUS') or x.endswith('LIB') or x.endswith('NIB') or x.endswith('TINIB') or x.startswith('ANIB') or x.endswith('RAFENIB') or x.startswith('IBRANCE') or x.startswith('PALBOCICLIB'):
            class_df.loc[y, 'class_id'] = 47
            class_df.loc[y, 'class'] = 'tyrosine kinase inhibitor'
            class_df.loc[y, 'indication'] = 'autoimmune diseases, cancer treatment'
        
        elif x.startswith('VITAMIN') or x.startswith('BIOTIN') or x.startswith('UBIDECARENONE') or x.startswith('MINERALS\VITAMINS') or x.startswith('FERROUS SULFATE') or x.startswith('FISH OIL') or x.startswith('IRON') or x.startswith('ERGOCALCIFEROL') or x.startswith('CHOLECALCIFEROL') or x.startswith('CYANOCOBALAMIN') or x.startswith('ASCORBIC ACID') or x.startswith('FOLIC'):
            class_df.loc[y, 'class_id'] = 74
            class_df.loc[y, 'class'] = 'vitamin, mineral, antioxidant'
            class_df.loc[y, 'indication'] = 'dietary supplement'    
        elif x.startswith('CLOZARIL') or x.startswith('CLOZAPINE') or x.startswith('HALOPERIDOL') or x.startswith('PALIPERIDONE PALMITATE') or x.startswith('INVEGA SUSTENNA') or x.startswith('RISPERIDONE') or x.startswith('RISPERDAL') or x.startswith('PIMAVANSERIN TARTRATE') or x.startswith('NUPLAZID') or x.startswith('QUETIAPINE') or x.startswith('OLANZAPINE') or x.startswith('ZYPREXA'):
            class_df.loc[y, 'class_id'] = 98
            class_df.loc[y, 'class'] = 'antipsychotic'
            class_df.loc[y, 'indication'] = 'schizophrenia'         
        else:
            pass
        

            
    class_df.class_id = class_df.class_id.astype(str)
    lead_df = class_df[class_df.class_id != 'nan']
    df_2 = class_df[class_df.class_id == 'nan']
    
    idx = df_2.index
    drugs = df_2.prod_ai

    end_time = time.time()
    total_min = (end_time - start_time) / 60
    total_hr = total_min / 60
    print(total_min)
    print('first stage complete, check "lead_df" for current output. Initiating stage two...')
   
    return map_2(df_2,drugs,idx,lead_df,array_split)  

def map_2(class_df,drugs,idx,lead_df,array_split):
    start_time = time.time()
    
    for x,y in zip(drugs,idx):
        
        if x.endswith('AFIL'): 
            class_df.loc[y, 'class_id'] = 6
            class_df.loc[y, 'class'] = 'phosphodiesterase inhibitor'
            class_df.loc[y, 'indication'] = 'erectile dysfunction, hypertension'
        elif x.endswith('ANE'):
            class_df.loc[y, 'class_id'] = 7
            class_df.loc[y, 'class'] = 'inhaled anestetics'
            class_df.loc[y, 'indication'] = 'anesthesia'
        elif x.endswith('ARTAN'):
            class_df.loc[y, 'class_id'] = 8
            class_df.loc[y, 'class'] = 'angiotension receptor blocker'
            class_df.loc[y, 'indication'] = 'hypertension'
        elif x.endswith('AZINE'):
            class_df.loc[y, 'class_id'] = 9
            class_df.loc[y, 'class'] = 'phenothiazines'
            class_df.loc[y, 'indication'] = 'antipsychotic'    
        elif x.endswith('TIDINE') or x.endswith('ZANTAC') or x.startswith('KETOTIFEN FUMARATE') or x.endswith('ZYRTEC') or x.startswith('CETERIZINE') or x.endswith('ZINE') or x.endswith('DINE') or x.endswith('MINE') or x.startswith('DIPHENHYDRAMINE') or x.startswith('BENADRYL') or x.startswith('LORATADINE') or x.startswith('CLARITIN'):
            class_df.loc[y, 'class_id'] = 3
            class_df.loc[y, 'class'] = 'antihistamine'
            class_df.loc[y, 'indication'] = 'allergy'
        elif x.endswith('BARBITAL'):
            class_df.loc[y, 'class_id'] = 11
            class_df.loc[y, 'class'] = 'barbituates'
            class_df.loc[y, 'indication'] = 'anxiety'
        elif x.endswith('CAINE'):
            class_df.loc[y, 'class_id'] = 12
            class_df.loc[y, 'class'] = 'local anesthetics'
            class_df.loc[y, 'indication'] = 'anesthesia'
        elif x.endswith('CILLIN'):
            class_df.loc[y, 'class_id'] = 13
            class_df.loc[y, 'class'] = 'penecillin antibiotics'
            class_df.loc[y, 'indication'] = 'antibiotic'
        elif x.endswith('CYCLINE'):
            class_df.loc[y, 'class_id'] = 14
            class_df.loc[y, 'class'] = 'tetracyclines'
            class_df.loc[y, 'indication'] = 'antibiotic'
        elif x.endswith('ETINE'):
            class_df.loc[y, 'class_id'] = 15
            class_df.loc[y, 'class'] = 'selective serotonia reuptake inhibitors'
            class_df.loc[y, 'indication'] = 'depression'
        elif x.endswith('FEB') or x.endswith('FENE'):
            class_df.loc[y, 'class_id'] = 16
            class_df.loc[y, 'class'] = 'selective estrogen response modifiers'
            class_df.loc[y, 'indication'] = 'osteoprosis, cancer treatment'
        elif x.endswith('FLOXACIN'):
            class_df.loc[y, 'class_id'] = 17
            class_df.loc[y, 'class'] = 'fluoroquinolones'
            class_df.loc[y, 'indication'] = 'antibiotics'
        elif x.endswith('FUNGIN'):
            class_df.loc[y, 'class_id'] = 18
            class_df.loc[y, 'class'] = 'echinocandins'
            class_df.loc[y, 'indication'] = 'antifungal'
        elif x.endswith('GRASTIM') or x.endswith('GRAMOSTIM'):
            class_df.loc[y, 'class_id'] = 19
            class_df.loc[y, 'class'] = 'granulocyte colony stimulating factors'
            class_df.loc[y, 'indication'] = 'blood dyscrasias'
        elif x.endswith('IPINE') or x.startswith('DILTIAZEM'):
            class_df.loc[y, 'class_id'] = 21
            class_df.loc[y, 'class'] = 'dihydropyridine calcium channel blockers'
            class_df.loc[y, 'indication'] = 'hypertension'
        elif x.endswith('IPRAMINE'):
            class_df.loc[y, 'class_id'] = 22
            class_df.loc[y, 'class'] = 'tricyclic antidepressants'
            class_df.loc[y, 'indication'] = 'depression'  
        elif x.endswith('LUKAST'):
            class_df.loc[y, 'class_id'] = 24
            class_df.loc[y, 'class'] = 'LTD receptor antagonist'
            class_df.loc[y, 'indication'] = 'asthma'
        elif x.endswith('NAVIR'):
            class_df.loc[y, 'class_id'] = 25
            class_df.loc[y, 'class'] = 'protease inhibitor'
            class_df.loc[y, 'indication'] = 'antiviral'
        elif x.endswith('*LOL') or x.startswith('COREG') or x.startswith('TIMOLOL MALEATE') or x.startswith('BISOPROLOL FUMARATE') or x.startswith('ZEBETA'):
            class_df.loc[y, 'class_id'] = 26
            class_df.loc[y, 'class'] = 'beta blocker'
            class_df.loc[y, 'indication'] = 'hypertension'
        elif x.endswith('OXIN'):
            class_df.loc[y, 'class_id'] = 27
            class_df.loc[y, 'class'] = 'cardiac glycoside'
            class_df.loc[y, 'indication'] = 'arrhythmias'
        elif x.endswith('PYHLLINE'):
            class_df.loc[y, 'class_id'] = 28
            class_df.loc[y, 'class'] = 'methlxanthine'
            class_df.loc[y, 'indication'] = 'bronchodilator'
        elif x.endswith('QUINE') or x.startswith('PLAQUENIL') or x.startswith('HYDROXYCHLOROQUINE SULFATE'):
            class_df.loc[y, 'class_id'] = 29
            class_df.loc[y, 'class'] = 'quinolone derivatives'
            class_df.loc[y, 'indication'] = 'antimalarial'
        elif x.endswith('TECAN'):
            class_df.loc[y, 'class_id'] = 30
            class_df.loc[y, 'class'] = 'topoisomerase-1 inhibitor'
            class_df.loc[y, 'indication'] = 'chemotherapy'
        elif x.endswith('TEROL') or x.startswith('FLUTICASONE FUROATE\VILANTEROL TRIFENATATE') or x.startswith('BREO'):
            class_df.loc[y, 'class_id'] = 31
            class_df.loc[y, 'class'] = 'Beta-2 agonist'
            class_df.loc[y, 'indication'] = 'bronchodilator'
        elif x.endswith('TINE'):
            class_df.loc[y, 'class_id'] = 32
            class_df.loc[y, 'class'] = 'allylamine antifungals'
            class_df.loc[y, 'indication'] = 'antifungal'
        elif x.endswith('TOPOSIDE'):
            class_df.loc[y, 'class_id'] = 33
            class_df.loc[y, 'class'] = 'topoisomerase-2 inhibitor'
            class_df.loc[y, 'indication'] = 'chemotherapy'
        elif x.endswith('TRIPTAN'):
            class_df.loc[y, 'class_id'] = 34
            class_df.loc[y, 'class'] = '5-HT1B/1D agonist'
            class_df.loc[y, 'indication'] = 'migraines'
        elif x.endswith('VAPTAN'):
            class_df.loc[y, 'class_id'] = 36
            class_df.loc[y, 'class'] = 'vasopressin receptor antagonist'
            class_df.loc[y, 'indication'] = 'hypertension'
        elif x.endswith('ZOSIN'):
            class_df.loc[y, 'class_id'] = 37
            class_df.loc[y, 'class'] = 'alpha-1 antagonist'
            class_df.loc[y, 'indication'] = 'hypertension, BPH'       
        
        elif x.startswith('TRUVADA') or x.startswith('DESCOVY') or x.endswith('*TENOFOVIR ALAFENAMIDE FUMARATE') or x.endswith('*DISOPROXIL FUMARATE') or x.startswith('VIREAD') or x.startswith('EMTRIVA') or x.startswith('EMTRICITABINE') or x.startswith('ATRIPLA'):
            class_df.loc[y, 'class_id'] = 51 
            class_df.loc[y, 'class'] = 'reverse transcriptase inhibitor'
            class_df.loc[y, 'indication'] = 'antiviral'   
        else:
            pass
        

    
    class_df.class_id = class_df.class_id.astype(str)
            
    df_2 = class_df[class_df.class_id != 'nan']
    df_3 = class_df[class_df.class_id == 'nan']
    final_df = pd.concat([lead_df, df_2])
    
    idx = df_3.index
    drugs = df_3.prod_ai
     
    end_time = time.time()
    total_min = (end_time - start_time) / 60
    total_hr = total_min / 60
    print(total_min)
    print('second stage complete. Initiating stage three...')
    
    return map_3(df_3,drugs,idx,final_df,array_split)

def map_3(class_df,drugs,idx,final_df,array_split):
    start_time = time.time()
    
    for x,y in zip(drugs,idx):
        
        if x.startswith('TECFIDERA') or x.startswith('DIMETHYL FUMARATE'):
            class_df.loc[y, 'class_id'] = 56
            class_df.loc[y, 'class'] = 'dimethyl fumarate, fumaric acid ester'
            class_df.loc[y, 'indication'] = 'multiple sclerosis'  
        elif x.startswith('NEULASTA'):
            class_df.loc[y, 'class_id'] = 63
            class_df.loc[y, 'class'] = 'granulocyte colony stimulating factor'
            class_df.loc[y, 'indication'] = 'febrile neutropenia'
        elif x.startswith('OXYCONTIN') or x.startswith('OXYCODONE') or x.startswith('CODEINE') or x.endswith('CODONE') or x.endswith('PHINE') or x.endswith('TANYL') or x.endswith('MORPHONE') or x.startswith('TRAMADOL') or x.startswith('ROXANOL') or x.startswith('MORPHINE SULFATE') or x.startswith('SUBLIMAZE') or x.startswith('FENTANYL'):
            class_df.loc[y, 'class_id'] = 67
            class_df.loc[y, 'class'] = 'opioid agonist'
            class_df.loc[y, 'indication'] = 'pain management'  
        elif x.startswith('TRULICITY'):
            class_df.loc[y, 'class_id'] = 76
            class_df.loc[y, 'class'] = 'glp-1 receptor agonist'
            class_df.loc[y, 'indication'] = 'glycemic management' 
        elif x.startswith('REMODULIN') or x.startswith('TREPROSTINIL'):
            class_df.loc[y, 'class_id'] = 83
            class_df.loc[y, 'class'] = 'prostacyclin vasodialator'
            class_df.loc[y, 'indication'] = 'pulmonary arterial hypertension, transition from Flolan' 
        elif x.startswith('DILANTIN') or x.startswith('PHENYTOIN') or x.startswith('VALPROIC ACID') or x.startswith('CARBAMAZEPINE') or x.startswith('TEGRETOL') or x.startswith('TOPIRAMATE') or x.startswith('TOPAMAX')or x.startswith('LEVETIRACETAM') or x.startswith('KEPPRA'):
            class_df.loc[y, 'class_id'] = 85
            class_df.loc[y, 'class'] = 'anticonvulsants'
            class_df.loc[y, 'indication'] = 'epilepsy'
        elif x.startswith('ZITHROMAX') or x.startswith('AZITHROMYCIN') or x.startswith('BACTRIM') or x.startswith('SULFAMETHOXAZOLE\TRIMETHOPRIM'):
            class_df.loc[y, 'class_id'] = 86
            class_df.loc[y, 'class'] = 'antibacterial'
            class_df.loc[y, 'indication'] = 'bacterial infection'
    
    
    class_df.class_id = class_df.class_id.astype(str)
            
    df_3 = class_df[class_df.class_id != 'nan']
    df_4 = class_df[class_df.class_id == 'nan']
    final_df = pd.concat([final_df, df_3])
    
    idx = df_4.index
    drugs = df_4.prod_ai
     
    end_time = time.time()
    total_min = (end_time - start_time) / 60
    total_hr = total_min / 60
    print(total_min)
    print('third stage complete. Initiating stage four...')
    
    return map_4(df_4,drugs,idx,final_df, array_split)

def map_4(class_df,drugs,idx,final_df,array_split):
    start_time = time.time()
    
    for x,y in zip(drugs,idx):
        if x.startswith('IMIQUIMOD') or x.startswith('ALDARA'):
            class_df.loc[y, 'class_id'] = 88
            class_df.loc[y, 'class'] = 'immune response modifier'
            class_df.loc[y, 'indication'] = 'actinic keratosis, genital warts'
        elif x.startswith('ZYLOPRIM') or x.startswith('ALOPRIM') or x.startswith('FEBUXOSTAT') or x.startswith('ALLOPURINOL'):
            class_df.loc[y, 'class_id'] = 89
            class_df.loc[y, 'class'] = 'xanthine oxidase inhibitor'
            class_df.loc[y, 'indication'] = 'gout prevention'
        elif x.startswith('HUMAN IMMUNOGLOBULIN G'):
            class_df.loc[y, 'class_id'] = 90
            class_df.loc[y, 'class'] = 'immune system supplement'
            class_df.loc[y, 'indication'] = 'immunodeficiency, Kawasaki syndrome, GvH disease'
        elif x.startswith('XALATAN') or x.startswith('LATANOPROST') or x.startswith('TRAVOPROST') or x.startswith('TRAVATAN'):
            class_df.loc[y, 'class_id'] = 91
            class_df.loc[y, 'class'] = 'prostanoid selective FP receptor agonist'
            class_df.loc[y, 'indication'] = 'open-angle glaucoma, ocular hypertension'
        elif x.startswith('ACYCLOVIR') or x.startswith('ZOVIRAX'):
            class_df.loc[y, 'class_id'] = 93
            class_df.loc[y, 'class'] = 'synthetic nucleoside analogue'
            class_df.loc[y, 'indication'] = 'herpes'
        elif x.startswith('PLAVIX') or x.startswith('CLOPIDOGREL'):
            class_df.loc[y, 'class_id'] = 94
            class_df.loc[y, 'class'] = 'P2Y-12 platelet inhibitor'
            class_df.loc[y, 'indication'] = 'myocardial infarction, stroke, extablished peripheral arterial disease'
        elif x.startswith('ZOFRAN') or x.startswith('ONDANSETRON'):
            class_df.loc[y, 'class_id'] = 96
            class_df.loc[y, 'class'] = '5-HT receptor antagonist'
            class_df.loc[y, 'indication'] = 'nausea prevention'  
        elif x.startswith('UPTRAVI') or x.startswith('SELEXIPAG'):
            class_df.loc[y, 'class_id'] = 100
            class_df.loc[y, 'class'] = 'prostacyclin receptor agonist'
            class_df.loc[y, 'indication'] = 'pulmonary arterial hypertension'
        elif x.startswith('XYREM') or x.startswith('SODIUM OXYBATE'):
            class_df.loc[y, 'class_id'] = 101
            class_df.loc[y, 'class'] = 'CNS depressant'
            class_df.loc[y, 'indication'] = 'cataplexy, excessive daytime sleepiness'
        elif x.startswith('MYCOPHENOLATE MOFETIL') or x.startswith('CELLCEPT') or x.startswith('AZATHIOPRINE') or x.startswith('IMURAN'): 
            class_df.loc[y, 'class_id'] = 103
            class_df.loc[y, 'class'] = 'antimetabolite immunosuppressant'
            class_df.loc[y, 'indication'] = 'prophylaxis of organ rejection'
        elif x.startswith('OCTREOTIDE ACETATE') or x.startswith('SANDOSTATIN'): 
            class_df.loc[y, 'class_id'] = 104
            class_df.loc[y, 'class'] = 'somatostatin analogue'
            class_df.loc[y, 'indication'] = 'acromegaly, diarrhea'
        elif x.startswith('ESCITALOPRAM OXALATE') or x.startswith('LEXAPRO'): 
            class_df.loc[y, 'class_id'] = 105
            class_df.loc[y, 'class'] = 'selective serotonin reuptake inhibitor'
            class_df.loc[y, 'indication'] = 'antidepressant'
        elif x.startswith('CARBOPLATIN') or x.startswith('PARAPLATIN') or x.startswith('SODIUM BICARBONATE') or x.startswith('CISPLATIN') or x.startswith('ELOXATIN') or x.startswith('OXALIPLATIN'): 
            class_df.loc[y, 'class_id'] = 108
            class_df.loc[y, 'class'] = 'alkylating agent'
            class_df.loc[y, 'indication'] = 'cancer treatment'
        elif x.startswith('CYCLOSPORINE') or x.startswith('SANDIMMUNE'): 
            class_df.loc[y, 'class_id'] = 110
            class_df.loc[y, 'class'] = 'nonribosomal peptide'
            class_df.loc[y, 'indication'] = 'prophylaxis of organ rejection'
        elif x.startswith('SPIRONOLACTONE') or x.startswith('ALDACTONE'): 
            class_df.loc[y, 'class_id'] = 111
            class_df.loc[y, 'class'] = 'aldonsterone antagonist'
            class_df.loc[y, 'indication'] = 'heart failure, edema management, hypertension'
        elif x.startswith('MACITENTAN') or x.startswith('OPSUMIT') or x.startswith('BOSENTAN') or x.startswith('AMBRISENTAN') or x.startswith('LETAIRIS'): 
            class_df.loc[y, 'class_id'] = 112
            class_df.loc[y, 'class'] = 'endothelin receptor antagonist'
            class_df.loc[y, 'indication'] = 'pulmonary aterial hypertension'
        elif x.startswith('VENETOCLAX') or x.startswith('VENCLEXTA'): 
            class_df.loc[y, 'class_id'] = 116
            class_df.loc[y, 'class'] = 'BCL-2 inhibitor'
            class_df.loc[y, 'indication'] = 'cancer treatment'
        elif x.startswith('FLUTICASONE PROPIONATE\SALMETEROL XINAFOATE') or x.startswith('ADVAIR DISKUS') or x.startswith('BUDESONIDE\FORMOTEROL FUMARATE DIHYDRATE') or x.startswith('SYMBICORT'): 
            class_df.loc[y, 'class_id'] = 119
            class_df.loc[y, 'class'] = 'corticosteroid, long-acting beta agonist'
            class_df.loc[y, 'indication'] = 'asthma'
        elif x.startswith('ZOLPIDEM') or x.startswith('AMBIEN') or x.startswith('ZOPICLONE'): 
            class_df.loc[y, 'class_id'] = 122
            class_df.loc[y, 'class'] = 'sedative-hypnotics'
            class_df.loc[y, 'indication'] = 'insomnia'
        elif x.startswith('LAMOTRIGINE'): 
            class_df.loc[y, 'class_id'] = 126
            class_df.loc[y, 'class'] = 'phenyltriazine'
            class_df.loc[y, 'indication'] = 'epilepsy, bipolar disorder'
        elif x.startswith('LEUPROLIDE ACETATE') or x.startswith('LUPRON DEPOT'): 
            class_df.loc[y, 'class_id'] = 127
            class_df.loc[y, 'class'] = 'gonadotropin-releasing hormone agonist'
            class_df.loc[y, 'indication'] = 'cancer treatment'
        elif x.startswith('BORTEZOMIB') or x.startswith('VELCADE'): 
            class_df.loc[y, 'class_id'] = 129 
            class_df.loc[y, 'class'] = 'antineoplastic agent, proteasome inhibitor'
            class_df.loc[y, 'indication'] = 'cancer treatment'
        elif x.startswith('MIRTAZAPINE') or x.startswith('REMERON'): 
            class_df.loc[y, 'class_id'] = 130
            class_df.loc[y, 'class'] = 'antidepressant'
            class_df.loc[y, 'indication'] = 'major depressive disorder, post-traumatic stress disorder'
        elif x.startswith('UNSPECIFIED INGREDIENT'):
            class_df.loc[y, 'class_id'] = 131
            class_df.loc[y, 'class'] = 'unknown'
            class_df.loc[y, 'indication'] = 'unknown'
        elif x.startswith('FLUOROURACIL') or x.startswith('CAPECITABINE') or x.startswith('XELODA') or x.startswith('GEMCITABINE') or x.startswith('GEMZAR'):
            class_df.loc[y, 'class_id'] = 132
            class_df.loc[y, 'class'] = 'nucleoside metabolic inhibitor'
            class_df.loc[y, 'indication'] = 'cancer treatment'
        elif x.startswith('EPINEPHRINE') or x.startswith('DROXIDOPA'):
            class_df.loc[y, 'class_id'] = 133
            class_df.loc[y, 'class'] = 'alpha and beta adrenergic agonist' 
            class_df.loc[y, 'indication'] = 'septic and anaphylaxis shock'
        elif x.startswith('ERENUMAB-AOOE') or x.startswith('AIMOVIG'):
            class_df.loc[y, 'class_id'] = 134
            class_df.loc[y, 'class'] = 'calcitonin gene-related peptide receptor antagonist '
            class_df.loc[y, 'indication'] = 'migraine'
        elif x.startswith('MINOXIDIL') or x.startswith('ROGAINE') or x.startswith('NITROGLYCERIN') or x.startswith('EPOPROSTENOL') or x.startswith('FLOLAN'):
            class_df.loc[y, 'class_id'] = 135
            class_df.loc[y, 'class'] = 'vasodialator'
            class_df.loc[y, 'indication'] = 'blood vessel expansion'
        elif x.startswith('BONIVA') or x.startswith('IBANDRONIC') or x.startswith('ZOLEDRONIC ACID') or x.startswith('ZOMETA'):
            class_df.loc[y, 'class_id'] = 136
            class_df.loc[y, 'class'] = 'bisphosphonate'
            class_df.loc[y, 'indication'] = 'osteoporosis'
        elif x.startswith('REMDESIVIR'):
            class_df.loc[y, 'class_id'] = 137
            class_df.loc[y, 'class'] = 'SARS-CoV-2 nucleotide analog RNA polymerase inhibitor'
            class_df.loc[y, 'indication'] = 'antiviral'
    
    
    class_df.class_id = class_df.class_id.astype(str)
            
    df_4 = class_df[class_df.class_id != 'nan']
    df_5 = class_df[class_df.class_id == 'nan']
    final_df = pd.concat([final_df, df_4])
    
    idx = df_5.index
    drugs = df_5.prod_ai
     
    end_time = time.time()
    total_min = (end_time - start_time) / 60
    total_hr = total_min / 60
    print(total_min)
    print('fourth stage complete. Initiating stage five...')
    
    return map_5(df_5,drugs,idx,final_df,array_split)

def map_5(class_df,drugs,idx, final_df,array_split):
    start_time = time.time()
    
    for x,y in zip(drugs,idx):
        if x.startswith('BRIMONIDINE TARTRATE') or x.startswith('ALPHAGAN'):
            class_df.loc[y, 'class_id'] = 138
            class_df.loc[y, 'class'] = 'alpha adrenergic agonist'
            class_df.loc[y, 'indication'] = 'open-angle glaucoma or ocular hypertension'
        elif x.startswith('NIRAPARIB') or x.startswith('ZEJULA'):
            class_df.loc[y, 'class_id'] = 139
            class_df.loc[y, 'class'] = 'PARP inhibitor'
            class_df.loc[y, 'indication'] = 'cancer treatment'
        elif x.startswith('FEMARA') or x.startswith('LETROZOLE'):
            class_df.loc[y, 'class_id'] = 140
            class_df.loc[y, 'class'] = 'aromatase inhibitor'
            class_df.loc[y, 'indication'] = 'cancer treatment'
        elif x.startswith('BIMATOPROST') or x.startswith('LUMIGAN'):
            class_df.loc[y, 'class_id'] = 141
            class_df.loc[y, 'class'] = 'prostaglandin analog'
            class_df.loc[y, 'indication'] = 'open angle glaucoma or ocular hypertension'
        elif x.startswith('FLOMAX') or x.startswith('TAMSULOSIN'):
            class_df.loc[y, 'class_id'] = 142
            class_df.loc[y, 'class'] = 'alpha-1 adrenoceptor antagonist'
            class_df.loc[y, 'indication'] = 'benign prostatic hyperplasia'
        elif x.startswith('AMITRIPTYLINE'):
            class_df.loc[y, 'class_id'] = 143
            class_df.loc[y, 'class'] = 'tricyclic antidepressant'
            class_df.loc[y, 'indication'] = 'anxiety, post-traumatic stress disorder'
        elif x.startswith('MIRABEGRON') or x.startswith('MYRBETRIQ'):
            class_df.loc[y, 'class_id'] = 144
            class_df.loc[y, 'class'] = 'beta-3 adrenergic agonist'
            class_df.loc[y, 'indication'] = 'overactive bladder'
        elif x.startswith('VANCOMYCIN') or x.startswith('VANCOCIN'):
            class_df.loc[y, 'class_id'] = 145
            class_df.loc[y, 'class'] = 'glycopeptide antibiotic'
            class_df.loc[y, 'indication'] = 'gram-positive bacterial infection'
        elif x.startswith('CALCIUM CARBONATE'):
            class_df.loc[y, 'class_id'] = 146
            class_df.loc[y, 'class'] = 'antacid'
            class_df.loc[y, 'indication'] = 'heart burn'
        elif x.startswith('DOXORUBICIN'):
            class_df.loc[y, 'class_id'] = 147
            class_df.loc[y, 'class'] = 'anthracycline'
            class_df.loc[y, 'indication'] = 'cancer treatment'
        elif x.startswith('COBICISTAT\ELVITEGRAVIR\EMTRICITABINE\TENOFOVIR DISOPROXIL FUMARATE'):
            class_df.loc[y, 'class_id'] = 148
            class_df.loc[y, 'class'] = 'HIV-1 INSTI, CYP3A INHIBITOR, NUCLEOSIDE REVERSE TRANSCRIPTASE INHIBITOR'
            class_df.loc[y, 'indication'] = 'antiviral'
        elif x.startswith('EZETIMIBE') or x.startswith('ZETIA'):
            class_df.loc[y, 'class_id'] = 149
            class_df.loc[y, 'class'] = 'lipid-lowering compound'
            class_df.loc[y, 'indication'] = 'hypercholesterolemia'
        elif x.startswith('CALCIUM CHLORIDE\DEXTROSE\MAGNESIUM CHLORIDE\SODIUM CHLORIDE\SODIUM LACTATE') or x.startswith('DELFLEX'):
            class_df.loc[y, 'class_id'] = 150
            class_df.loc[y, 'class'] = 'dialysis adjunct'
            class_df.loc[y, 'indication'] = 'chronic kidney failure'
        elif x.startswith('CYCLOBENZAPRINE') or x.startswith('FLEXERIL'):
            class_df.loc[y, 'class_id'] = 151
            class_df.loc[y, 'class'] = 'skeletal muscle relaxant'
            class_df.loc[y, 'indication'] = 'muscle spasm'
        elif x.startswith('CEFTRIAXONE') or x.startswith('ROCEPHIN'):
            class_df.loc[y, 'class_id'] = 201
            class_df.loc[y, 'class'] = 'cephalosporin'
            class_df.loc[y, 'indication'] = 'antibiotic'
        elif x.startswith('ENOXAPARIN') or x.startswith('LOVENOX'):
            class_df.loc[y, 'class_id'] = 202
            class_df.loc[y, 'class'] = 'molecular weight herapins'
            class_df.loc[y, 'indication'] = 'deep vein thrombosis'
        elif x.startswith('EMPAGLIFLOZIN') or x.startswith('JARDIANCE'):
            class_df.loc[y, 'class_id'] = 154
            class_df.loc[y, 'class'] = 'sodium-glucose co-transporter 2'
            class_df.loc[y, 'indication'] = 'glucose management'
        elif x.startswith('MEROPENEM') or x.startswith('MERREM'):
            class_df.loc[y, 'class_id'] = 155
            class_df.loc[y, 'class'] = 'penem antibacterial'
            class_df.loc[y, 'indication'] = 'bacterial infection'
        elif x.startswith('AMIODARONE') or x.startswith('NEXTERONE'):
            class_df.loc[y, 'class_id'] = 156
            class_df.loc[y, 'class'] = 'potassium channel blocker'
            class_df.loc[y, 'indication'] = 'arrhythmia'
        elif x.startswith('RIOCIGUAT') or x.startswith('ADEMPAS'):
            class_df.loc[y, 'class_id'] = 158
            class_df.loc[y, 'class'] = 'soluble guanylate cyclase stimulator'
            class_df.loc[y, 'indication'] = 'CTEPH, PAH'
        elif x.startswith('LACTULOSE') or x.startswith('POLYETHYLENE GLYCOLS') or x.startswith('SENNOSIDES') or x.startswith('POLYETHYLENE GLYCOL 3350'):
            class_df.loc[y, 'class_id'] = 159
            class_df.loc[y, 'class'] = 'laxative'
            class_df.loc[y, 'indication'] = 'constipation'
        elif x.startswith('MYCOPHENOLIC ACID') or x.startswith('MYFORTIC'):
            class_df.loc[y, 'class_id'] = 160
            class_df.loc[y, 'class'] = 'guanosine nucleotide inhibitor'
            class_df.loc[y, 'indication'] = 'immunosupresant' 
        elif x.startswith('AMPHETAMINE ASPARTATE\AMPHETAMINE SULFATE\DEXTROAMPHETAMINE SACCHARATE\DEXTROAMPHETAMINE SULFATE'):
            class_df.loc[y, 'class_id'] = 161
            class_df.loc[y, 'class'] = 'stimulant'
            class_df.loc[y, 'indication'] = 'ADD/ADHD'
        elif x.startswith('SITAGLIPTIN PHOSPHATE'):
            class_df.loc[y, 'class_id'] = 162
            class_df.loc[y, 'class'] = 'dipeptidyl peptidase-4 inhibitor'
            class_df.loc[y, 'indication'] = 'dibetic management'
        elif x.startswith('VOXELOTOR'):
            class_df.loc[y, 'class_id'] = 163
            class_df.loc[y, 'class'] = 'hemoglobin S polymerization inhibitor'
            class_df.loc[y, 'indication'] = 'sickle cell disease'
        elif x.startswith('CLARITHROMYCIN'):
            class_df.loc[y, 'class_id'] = 164
            class_df.loc[y, 'class'] = 'macrolide antibiotic'
            class_df.loc[y, 'indication'] = 'bacterial infection'
        elif x.startswith('ANAKINRA'):
            class_df.loc[y, 'class_id'] = 165
            class_df.loc[y, 'class'] = 'interleukin antagonist'
            class_df.loc[y, 'indication'] = 'rheumatoid arthritis'
        elif x.startswith('FULVESTRANT'):
            class_df.loc[y, 'class_id'] = 166
            class_df.loc[y, 'class'] = 'estrogen receptor antagonist'
            class_df.loc[y, 'indication'] = 'cancer treatment'
        elif x.startswith('ELEXACAFTOR\IVACAFTOR\TEZACAFTOR'):
            class_df.loc[y, 'class_id'] = 200
            class_df.loc[y, 'class'] = 'cystic fibrosis transmembrane conductance regulator corrector/potentiator'
            class_df.loc[y, 'indication'] = 'cystic fibrosis'
        elif x.startswith('CANNABIDIOL'):
            class_df.loc[y, 'class_id'] = 201
            class_df.loc[y, 'class'] = 'phytocannabionoid'
            class_df.loc[y, 'indication'] = 'seizures'
        elif x.startswith('NALTREXONE'):
            class_df.loc[y, 'class_id'] = 202
            class_df.loc[y, 'class'] = 'opioid antagonist'
            class_df.loc[y, 'indication'] = 'alcholism, opioid dependence'
        elif x.startswith('PIRFENIDONE'):
            class_df.loc[y, 'class_id'] = 203
            class_df.loc[y, 'class'] = 'pyridone'
            class_df.loc[y, 'indication'] = 'idiopathic pulmonary fibrosis'
        elif x.startswith('GUAIFENESIN'):
            class_df.loc[y, 'class_id'] = 204
            class_df.loc[y, 'class'] = 'expectorant'
            class_df.loc[y, 'indication'] = 'common cold'
        elif x.startswith('VENLAFAXINE'):
            class_df.loc[y, 'class_id'] = 205
            class_df.loc[y, 'class'] = 'serotonin and norepinephrine reuptake inhibitor'
            class_df.loc[y, 'indication'] = 'depression'
        elif x.startswith('BUPROPION'):
            class_df.loc[y, 'class_id'] = 206
            class_df.loc[y, 'class'] = 'norepinephrine and dopamine reuptake inhibitor'
            class_df.loc[y, 'indication'] = 'depression'
        elif x.startswith('LINEZOLID'):
            class_df.loc[y, 'class_id'] = 207
            class_df.loc[y, 'class'] = 'oxazolidinone'
            class_df.loc[y, 'indication'] = 'antibiotic'
        elif x.startswith('LEUCOVORIN'):
            class_df.loc[y, 'class_id'] = 208
            class_df.loc[y, 'class'] = 'folic acid analog'
            class_df.loc[y, 'indication'] = 'cancer treatment adjunct'
        elif x.startswith('CEPHALEXIN'):
            class_df.loc[y, 'class_id'] = 209
            class_df.loc[y, 'class'] = 'cephlasporin antibiotic'
            class_df.loc[y, 'indication'] = 'repiratory tract infection'
        elif x.startswith('DABIGATRAN ETEXILATE MESYLATE'):
            class_df.loc[y, 'class_id'] = 210
            class_df.loc[y, 'class'] = 'anticoagulant'
            class_df.loc[y, 'indication'] = 'blood clots'
        elif x.startswith('OXYGEN'):
            class_df.loc[y, 'class_id'] = 211
            class_df.loc[y, 'class'] = 'medical gas'
            class_df.loc[y, 'indication'] = 'compromised breathing'
        elif x.startswith('DARBEPOETIN ALFA'):
            class_df.loc[y, 'class_id'] = 212
            class_df.loc[y, 'class'] = 'erythropoiesis-stimulating agent'
            class_df.loc[y, 'indication'] = 'anemia'
        elif x.startswith('PANCRELIPASE AMYLASE\PANCRELIPASE LIPASE\PANCRELIPASE PROTEASE'):
            class_df.loc[y, 'class_id'] = 213
            class_df.loc[y, 'class'] = 'amylase, lipase, protease'
            class_df.loc[y, 'indication'] = 'exocrine pancreatic insufficiency'
        elif x.startswith('ABIRATERONE ACETATE'):
            class_df.loc[y, 'class_id'] = 214
            class_df.loc[y, 'class'] = 'CYP17 inhibitor'
            class_df.loc[y, 'indication'] = 'cancer treatment'
        elif x.startswith('FENOFIBRATE'):
            class_df.loc[y, 'class_id'] = 215
            class_df.loc[y, 'class'] = 'peroxisome proliferator-activated receptor alpha agonist'
            class_df.loc[y, 'indication'] = 'hypertriglyceridemia'
        elif x.startswith('HUMAN C1-ESTERASE INHIBITOR'):
            class_df.loc[y, 'class_id'] = 216
            class_df.loc[y, 'class'] = 'C1 esterase inhibitor'
            class_df.loc[y, 'indication'] = 'hereditary angioedema'
        elif x.startswith('ANTIHEMOPHILIC FACTOR, HUMAN RECOMBINANT'):
            class_df.loc[y, 'class_id'] = 217
            class_df.loc[y, 'class'] = 'coagulation factor'
            class_df.loc[y, 'indication'] = 'hemophilia A'
        elif x.startswith('CLINDAMYCIN'):
            class_df.loc[y, 'class_id'] = 218
            class_df.loc[y, 'class'] = 'lincomycin antibiotic'
            class_df.loc[y, 'indication'] = 'bacterial infection'
        elif x.startswith('COLCHICINE'):
            class_df.loc[y, 'class_id'] = 219
            class_df.loc[y, 'class'] = 'anti-gout agent'
            class_df.loc[y, 'indication'] = 'gout'
        elif x.startswith(r'FLUTICASONE FUROATE\UMECLIDINIUM BROMIDE\VILANTEROL TRIFENATATE'):
            class_df.loc[y, 'class_id'] = 220
            class_df.loc[y, 'class'] = 'corticosteroid, anticholinergic, long-acting beta2-adrenergic agonist'
            class_df.loc[y, 'indication'] = 'chronic obstructive pulmonary disease'
        elif x.startswith('TICAGRELOR'):
            class_df.loc[y, 'class_id'] = 221
            class_df.loc[y, 'class'] = 'P2Y12 platelet inhibitor'
            class_df.loc[y, 'indication'] = 'acute coronary syndrome, myocardial infarction'
        elif x.startswith('URSODIOL'):
            class_df.loc[y, 'class_id'] = 222
            class_df.loc[y, 'class'] = 'gallstone dissolution agent'
            class_df.loc[y, 'indication'] = 'gallstone prevention, primary biliary cirrhosis'
        elif x.startswith('COBICISTAT\ELVITEGRAVIR\EMTRICITABINE\TENOFOVIR ALAFENAMIDE FUMARATE'):
            class_df.loc[y, 'class_id'] = 223
            class_df.loc[y, 'class'] = 'integrase strand transfer inhibitor, CYP3A inhibotor, nucleoside analog reverse transcriptase inhibitor'
            class_df.loc[y, 'indication'] = 'antiviral'
        elif x.startswith('ANASTROZOLE'):
            class_df.loc[y, 'class_id'] = 224
            class_df.loc[y, 'class'] = 'nonsteroidal aromatase inhibitor'
            class_df.loc[y, 'indication'] = 'cancer treatment'
        elif x.startswith('AMIKACIN'):
            class_df.loc[y, 'class_id'] = 225
            class_df.loc[y, 'class'] = 'aminoglycoside antibiotic'
            class_df.loc[y, 'indication'] = 'antibacterial'
        elif x.startswith('OLAPARIB'):
            class_df.loc[y, 'class_id'] = 226
            class_df.loc[y, 'class'] = 'poly (ADP-ribose) polymerase inhibitor'
            class_df.loc[y, 'indication'] = 'cancer treatment'
        else:
            pass
    
    class_df.class_id = class_df.class_id.astype(str)
    miss_df = class_df[class_df.class_id == 'nan']
    class_df = class_df[class_df.class_id != 'nan']
    final_df = pd.concat([final_df, class_df])
    
    global final_storage_list
    global final_missing_storage_list
    
    final_storage_list.append(final_df)
    final_missing_storage_list.append(miss_df)
    
    if len(final_storage_list) == array_split:
        final_df = pd.concat(final_storage_list)
        final_df = final_df.sort_values(by='primaryid').reset_index(drop=True)
        final_dfs.append(final_df)
        
        miss_df = pd.concat(final_missing_storage_list)
        miss_df = miss_df.sort_values(by='primaryid').reset_index(drop=True)
        miss_dfs.append(miss_df)

        
        final_storage_list = []
        final_missing_storage_list = []
        print('final_df concatenated, onto the next...')
    else:
        pass
    
    
    end_time = time.time()
    total_min = (end_time - start_time) / 60
    total_hr = total_min / 60
    
    

    print(total_min)
    print('mapping complete, check "final_df" and "miss_df" for final outputs. Thank you.')


def reacs_map(reactions__file_path):
    
    reactions_by_id = {}
    with open(reactions__file_path) as csvfile:
        reacreader = csv.reader(csvfile, delimiter='$')
        next(reacreader) #skip headers
         
        for row in reacreader:

            ptlist = reactions_by_id.get(row[0], [])
            ptlist.append(row[2])
            reactions_by_id[row[0]] = ptlist

        reactions_by_id_list.append(reactions_by_id) 
        
            
    reac_df = pd.DataFrame(reactions_by_id.keys(), columns=(['primaryid']))
    reac_df = reac_df.sort_values(by='primaryid').set_index('primaryid')
    reac_df['pt'] = 'nan'
    
    for k,v in reactions_by_id.items():
        reac_df.loc[k, 'pt'] = ' , '.join(v)
    final_reacs.append(reac_df)
    
    print('completed')
    


def outs_map(outcomes_file_path):
    
    outcomes_by_id = {}
    with open(outcomes_file_path) as csvfile:
        outcreader = csv.reader(csvfile, delimiter='$')
        next(outcreader) #skip headers
        
        for row in outcreader:
            ptlist = outcomes_by_id.get(row[0], [])
            ptlist.append(row[2])
            outcomes_by_id[row[0]] = ptlist
        outcomes_by_id_list.append(outcomes_by_id)
        

    out_df = pd.DataFrame(outcomes_by_id.keys(), columns=(['primaryid']))
    out_df = out_df.sort_values(by='primaryid').set_index('primaryid')
    out_df['out_code'] = 'nan'
       
    for k,v in outcomes_by_id.items():
        out_df.loc[k,'out_code'] = ' , '.join(v)
    final_outs.append(out_df)
    
    print('done')


def file_merge(final_class_df_path, final_reac_path, final_out_path):
    
    if isinstance(final_class_df_path, str):
        sd = pd.read_csv(final_class_df_path)  
    if isinstance(final_reac_path, str):
        fr = pd.read_csv(final_reac_path)
    if isinstance(final_out_path, str):
        fo = pd.read_csv(final_out_path)
    else:
        sd = final_class_df_path
        fr = final_reac_path
        fo = final_out_path
    
    sd = sd.set_index('primaryid')
    fr = fr.set_index('primaryid')
    fo = fo.set_index('primaryid')
    sd['pt'] = 'nan'
    sd['out_code'] = 'nan'
    
    for x in fr.index:
        x = int(x)
        
        for z in sd.index:
            if x == z:
                sd.loc[z,'pt'] = fr.loc[x,'pt'] 
            else:
                pass
    print('finished with reactions')

    for y in fo.index:    
        y = int(y)
        
        for z in sd.index:
            if y == z:
                sd.loc[z,'out_code'] = fo.loc[y,'out_code']
            else:
                pass    
    print('finished with outcomes')
    sd = sd[['primaryid', 'drugname', 'class', 'class_id', 'indication', 'pt', 'out_code']].reset_index()
    print('completed')         
    custom_dfs.append(sd)