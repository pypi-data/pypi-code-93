#!/usr/bin/env python3.7

import pandas as pd
#from legacy import param


def read_summary(AD_sum, DB_sum, AD_group, DB_group):
    """
    Read from AD and DB summary files. 
    Grep gene names based on AD and DB group
    If group == G0, grep all
    """
    
    AD_summary = pd.read_table(AD_sum, sep=",")
    DB_summary = pd.read_table(DB_sum, sep=",")
    
    # grep group 
    if AD_group!="Gall":
        if AD_group == 'GM':
            AD_summary = AD_summary[(AD_summary.Plate.str.contains("Miha"))|(AD_summary.Group=="null_setD")] 
        else:
            AD_summary = AD_summary[(AD_summary.Group==AD_group) | (AD_summary.Group=="null_setD") ]
    
    if DB_group!="Gall":
        if DB_group == 'GM':
            DB_summary = DB_summary[(DB_summary.Plate.str.contains("Miha")) | (DB_summary.Group=="null_setD")] 
        else:
            DB_summary = DB_summary[(DB_summary.Group==DB_group) | (DB_summary.Group=="null_setD") ]
    
    # grep gene names
    AD_genes = AD_summary.Locus.tolist()
    DB_genes = DB_summary.Locus.tolist()
    return AD_genes, DB_genes


def read_summary_virus(AD_sum, DB_sum, AD_group, DB_group):

    AD_summary = pd.read_table(AD_sum, sep=",")
    DB_summary = pd.read_table(DB_sum, sep=",")
    if DB_group == "DBNC":
        vDBNC_df = pd.read_csv(param.vDBNC)
        DB_genes = vDBNC_df.ORF.tolist()

    if AD_group == "ADNC":
        vADNC_df = pd.read_csv(param.vADNC)
        AD_genes = vADNC_df.ORF.tolist()

    elif AD_group == "AD2u":
        vAD2u_df = pd.read_csv(param.vAD2u)
        AD_genes = vAD2u_df.ORF.tolist()

    elif AD_group == "ADall":
        vADall_df = pd.read_csv(param.vADall)
        AD_genes = vADall_df.ORF.tolist()

    if "G" in AD_group: # group sepecific
        AD_summary = AD_summary[(AD_summary.Group==AD_group) | (AD_summary.Group=="null_setD") ]
        AD_genes = AD_summary.Locus.tolist()
    else: # all genes
        AD_genes = AD_summary.Locus.tolist()

    if "G" in DB_group: # group specific
        DB_summary = DB_summary[(DB_summary.Group==DB_group) | (DB_summary.Group=="null_setD")]
        DB_genes = DB_summary.Locus.tolist()
    else: # all genes
        DB_genes = DB_summary.Locus.tolist()

    return AD_genes, DB_genes


def read_summary_hedgy(AD_sum, DB_sum, AD_group="G0", DB_group="G0"):

    AD_summary = pd.read_table(AD_sum, sep=",")
    DB_summary = pd.read_table(DB_sum, sep=",")

    AD_summary = AD_summary[(AD_summary.Group==AD_group) | (AD_summary.Group=="null_setD") ]
    AD_genes = AD_summary.Locus.tolist()

    DB_genes = DB_summary.Locus.tolist()
    return AD_genes, DB_genes


def parse_ds_ref(fasta):
    """
    separate dayag's fasta file
    """

    with open(fasta, "r") as ref, open("ds_AD_ref.fasta", "w") as ad, open("ds_DB_ref.fasta", "w") as db:
        c = ref.readlines()
        line =0
        while line in range(len(c)):
        #for line in c:
            # print line
            if ">c" in c[line]: 
                line+=2 
                continue
            
            if ">AD" in c[line]:
                ad.write(c[line])
                ad.write(c[line+1])
            else:
                db.write(c[line])
                db.write(c[line+1])
            line+=2


def get_pair_counts(AD, DB, f):
    # get counts from combined counts file based
    # on AD and DB
    df = pd.read_csv(f, index_col=0)
    #df.set_index("0")
    #print df
    df = df.stack().reset_index()
    df.columns = ["AD", "DB","c"]
    count = df[(df.AD.str.contains(AD))& (df.DB.str.contains(DB))]
    #print df[df.AD.str.contains(DB)]
    print(count)

if __name__ == "__main__":
    fasta = "./ds_ref/barcodes.fasta"
    #parse_ds_ref(fasta)
    f = "/home/rothlab/rli/02_dev/08_bfg_y2h/181109_test/yAD3DB3/yAD3DB3_med_combined_counts.csv"
    get_pair_counts("YNL032W", "YNL099C", f)



