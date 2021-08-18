from liwc import liwc_features
import pandas as pd
import csv
if __name__ == '__main__':
    redacoes = pd.read_csv('essay_dataset.csv')
    # print(redacoes[['ID','Texto']])

    with open('../data/essay_datasetLIWC.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["ID", "liwc.funct", "liwc.pronoun", "liwc.ppron", "liwc.i", "liwc.we", "liwc.you", "liwc.shehe",
                         "liwc.they", "liwc.ipron", "liwc.article"
                            , "liwc.verb", "liwc.auxverb", "liwc.past", "liwc.present", "liwc.future", "liwc.adverb",
                         "liwc.preps",
                         "liwc.conj", "liwc.negate", "liwc.quant"
                            , "liwc.number", "liwc.swear", "liwc.social", "liwc.family", "liwc.friend", "liwc.humans",
                         "liwc.affect",
                         "liwc.posemo", "liwc.negemo", "liwc.anx"
                            , "liwc.anger", "liwc.sad", "liwc.cogmech", "liwc.insight", "liwc.cause", "liwc.discrep",
                         "liwc.tentat",
                         "liwc.certain", "liwc.inhib", "liwc.incl"
                            , "liwc.excl", "liwc.percept", "liwc.see", "liwc.hear", "liwc.feel", "liwc.bio", "liwc.body",
                         "liwc.health",
                         "liwc.sexual", "liwc.ingest"
                            , "liwc.relativ", "liwc.motion", "liwc.space", "liwc.time", "liwc.work", "liwc.achieve",
                         "liwc.leisure", "liwc.home", "liwc.money", "liwc.relig"
                            , "liwc.death", "liwc.assent", "liwc.nonfl", "liwc.filler"])

        for index, row in redacoes.iterrows():
            print(row['ID'])
            # print(liwc.liwcFeatures(r))
            result_liwc = liwc_features(row['text'])  # extração de features

            writer.writerow([row['ID'], result_liwc[0], result_liwc[1], result_liwc[2], result_liwc[3], result_liwc[4]
                                , result_liwc[5], result_liwc[6], result_liwc[7], result_liwc[8], result_liwc[9],
                             result_liwc[10]
                                , result_liwc[11], result_liwc[12], result_liwc[13], result_liwc[14], result_liwc[15],
                             result_liwc[16]
                                , result_liwc[17], result_liwc[18], result_liwc[19], result_liwc[20], result_liwc[21],
                             result_liwc[22]
                                , result_liwc[23], result_liwc[24], result_liwc[25], result_liwc[26], result_liwc[27],
                             result_liwc[28]
                                , result_liwc[29], result_liwc[30], result_liwc[31], result_liwc[32], result_liwc[33],
                             result_liwc[34]
                                , result_liwc[35], result_liwc[36], result_liwc[37], result_liwc[38], result_liwc[39],
                             result_liwc[40]
                                , result_liwc[41], result_liwc[42], result_liwc[43], result_liwc[44], result_liwc[45],
                             result_liwc[46]
                                , result_liwc[47], result_liwc[48], result_liwc[49], result_liwc[50], result_liwc[51],
                             result_liwc[52]
                                , result_liwc[53], result_liwc[54], result_liwc[55], result_liwc[56], result_liwc[57],
                             result_liwc[58]
                                , result_liwc[59], result_liwc[60], result_liwc[61], result_liwc[62], result_liwc[63]])
