#!/usr/bin/env python
# encoding=utf-8

import pandas as pd
from pybiomart import Server as BiomartServer
from pkg_resources import resource_filename

DATA = resource_filename(__name__, 'data/human.csv')

def BiomartLoader(species, biotype = ['protein_coding', 'lncRNA']):
    '''Load protein coding & lncRNA gene from biomart server'''
    if species == 'mouse':
        dataset_name = 'mmusculus_gene_ensembl'  # Mouse genes (GRCm38.p6)
    elif species == 'human':
        dataset_name = 'hsapiens_gene_ensembl'  # Human genes (GRCh38.p13)

    biomart_server = BiomartServer(host='http://www.ensembl.org')

    biomart_dataset = (biomart_server.marts['ENSEMBL_MART_ENSEMBL']
        .datasets[dataset_name])
    gene_display_name = biomart_server.marts['ENSEMBL_MART_ENSEMBL'].datasets[dataset_name].display_name
    print('load', gene_display_name, 'from biomart')

    genedata = biomart_dataset.query(attributes=['ensembl_gene_id',
                                                 'external_gene_name',
                                                 'chromosome_name',
                                                 'start_position',
                                                 'end_position',
                                                 'strand',
                                                 'gene_biotype'],
                                     filters={'biotype': biotype})
    return genedata

def merge(target, colname, info = 'gene_name', required = 'ensembl_gene_id', species = 'human', biotype = ['protein_coding', 'lncRNA'], version = 'default', how = 'inner'):
    '''add gene annotation information

    '''
    if species !='human':
        print("Sorry, it supports for human only for version 0.0.1")
        return 0


    if info == 'symbol':
        target.rename(columns={colname: 'gene_name'})
    elif info == 'ensemblid':
        target.rename(columns={colname: 'ensembl_gene_id'})
    if version != 'default':
        target = pd.merge(target, BiomartLoader(species, biotype),how = how)
    else:
        hm = pd.read_csv(DATA)
        target = pd.merge(target, hm, how = how)

    col = target.pop(required)
    target.insert(0, col.name, col)

    return target
