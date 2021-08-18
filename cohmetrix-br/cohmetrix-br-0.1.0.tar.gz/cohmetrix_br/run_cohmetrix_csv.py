import pandas as pd
import csv
from cohmetrixBR import run_coh_metrix

if __name__ == '__main__':

    forum = pd.read_csv('essay_dataset.csv', encoding="ISO-8859-1")

    with open('essay_dataset_coh-metrix4.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(
            ["ID", "cm.DESPC", "cm.DESSC", "cm.DESWC", "cm.DESPL", "cm.DESPLd", "cm.DESSL", "cm.DESSLd", "cm.DESWLsy",
             "cm.DESWLsyd", "cm.DESWLlt", "cm.DESWLltd",
             "cm.CRFNO1", "cm.CRFAO1", "cm.CRFSO1", "cm.CRFNOa", "cm.CRFAOa", "cm.CRFSOa", "cm.CRFCWO1", "cm.CRFCWO1d",
             "cm.CRFCWOa", "cm.CRFCWOad", "cm.CRFANP1", "cm.CRFANPa",
             "cm.LSASS1", "cm.LSASS1d", "cm.LSASSp", "cm.LSASSpd", "cm.LSAPP1", "cm.LSAPP1d", "cm.LSAGN", "cm.LSAGNd",
             "cm.LDTTRc", "cm.LDTTRa", "cm.LDMTLDa", "cm.LDVOCDa",
             "cm.CNCAll", "cm.CNCCaus", "cm.CNCLogic", "cm.CNCADC", "cm.CNCTemp", "cm.CNCAdd", "cm.CNCPos", "cm.CNCNeg",
             "cm.CNCAlter", "cm.CNCConclu", "cm.CNCExpli", "cm.CNCConce", "cm.CNCCondi", "cm.CNCConfor", "cm.CNCFinal",
             "cm.CNCProp", "cm.CNCComp", "cm.CNCConse", "cm.CNCInte",
             "cm.SMCAUSv", "cm.SMCAUSvp", "cm.SMCAUSr", "cm.SMCAUSlsa", "cm.SMCAUSwn",
             "cm.SYNLE", "cm.SYNMEDpos", "cm.SYNMEDwrd", "cm.SYNMEDlem", "cm.SYNSTRUTa", "cm.SYNSTRUTt",
             "cm.DRNP", "cm.DRVP", "cm.DRAP", "cm.DRPP", "cm.DRPVAL", "cm.DRNEG", "cm.DRGERUND", "cm.DRINF",
             "cm.WRDNOUN", "cm.WRDVERB", "cm.WRDADJ", "cm.WRDADV", "cm.WRDPRO", "cm.WRDPRP1s",
             "cm.WRDPRP1p", "cm.WRDPRP2", "cm.WRDPRP3s", "cm.WRDPRP3p", "cm.WRDFRQc", "cm.WRDFRQa", "cm.WRDFRQmc",
             "cm.WRDAOAc", "cm.WRDFAMc", "cm.WRDCNCc", "cm.WRDIMGc", "cm.WRDMEAc",
             "cm.RDFRE", "cm.RDFKGL", "cm.RDL2"])

        for index, row in forum.iterrows():
            print(row['ID'])
            # print(liwc.liwcFeatures(r))
            result_cohmetrix = run_coh_metrix.coh_metrix_features(row['text'])  # extração de features

            writer.writerow([row['ID'], result_cohmetrix[0], result_cohmetrix[1], result_cohmetrix[2], result_cohmetrix[3],
                             result_cohmetrix[4]
                                , result_cohmetrix[5], result_cohmetrix[6], result_cohmetrix[7], result_cohmetrix[8],
                             result_cohmetrix[9]
                                , result_cohmetrix[10], result_cohmetrix[11], result_cohmetrix[12], result_cohmetrix[13],
                             result_cohmetrix[14]
                                , result_cohmetrix[15], result_cohmetrix[16], result_cohmetrix[17], result_cohmetrix[18],
                             result_cohmetrix[19]
                                , result_cohmetrix[20], result_cohmetrix[21], result_cohmetrix[22], result_cohmetrix[23],
                             result_cohmetrix[24]
                                , result_cohmetrix[25], result_cohmetrix[26], result_cohmetrix[27], result_cohmetrix[28],
                             result_cohmetrix[29]
                                , result_cohmetrix[30], result_cohmetrix[31], result_cohmetrix[32], result_cohmetrix[33],
                             result_cohmetrix[34]
                                , result_cohmetrix[35], result_cohmetrix[36], result_cohmetrix[37], result_cohmetrix[38],
                             result_cohmetrix[39]
                                , result_cohmetrix[40], result_cohmetrix[41], result_cohmetrix[42], result_cohmetrix[43],
                             result_cohmetrix[44]
                                , result_cohmetrix[45], result_cohmetrix[46], result_cohmetrix[47], result_cohmetrix[48],
                             result_cohmetrix[49]
                                , result_cohmetrix[50], result_cohmetrix[51], result_cohmetrix[52], result_cohmetrix[53],
                             result_cohmetrix[54]
                                , result_cohmetrix[55], result_cohmetrix[56], result_cohmetrix[57], result_cohmetrix[58],
                             result_cohmetrix[59]
                                , result_cohmetrix[60], result_cohmetrix[61], result_cohmetrix[62], result_cohmetrix[63],
                             result_cohmetrix[64]
                                , result_cohmetrix[65], result_cohmetrix[66], result_cohmetrix[67], result_cohmetrix[68],
                             result_cohmetrix[69]
                                , result_cohmetrix[70], result_cohmetrix[71], result_cohmetrix[72], result_cohmetrix[73],
                             result_cohmetrix[74]
                                , result_cohmetrix[75], result_cohmetrix[76], result_cohmetrix[77], result_cohmetrix[78],
                             result_cohmetrix[79]
                                , result_cohmetrix[80], result_cohmetrix[81], result_cohmetrix[82], result_cohmetrix[83],
                             result_cohmetrix[84]
                                , result_cohmetrix[85], result_cohmetrix[86], result_cohmetrix[87], result_cohmetrix[88],
                             result_cohmetrix[89]
                                , result_cohmetrix[90], result_cohmetrix[91], result_cohmetrix[92], result_cohmetrix[93]])
