import logging
import pickle

import numpy as np
import pandas as pd
from pre_processing import Pipeline

logger = logging.getLogger(__name__)


class VictorThemes:
    def __init__(self, tfidf, vectorizer, temas_df):
        self.load_tfidf(tfidf)
        self.load_vectorizer(vectorizer)
        self.load_themes(temas_df)

    def load_tfidf(self, tfidf):
        if isinstance(tfidf, str):
            with open(tfidf, "rb") as f:
                tfidf = pickle.load(f)
        self.tfidf = tfidf

    def load_vectorizer(self, vectorizer):
        if isinstance(vectorizer, str):
            with open(vectorizer, "rb") as f:
                vectorizer = pickle.load(f)
        self.vectorizer = vectorizer

    def load_themes(self, temas_df):
        if isinstance(temas_df, str):
            temas_df = pd.read_pickle(temas_df)
        self.temas = temas_df

        if (
            "contagem" not in temas_df.columns
            or "tema" not in temas_df.columns  # noqa: W503
            or "samples_idx" not in temas_df.columns  # noqa: W503
            or "quantiles" not in temas_df.columns  # noqa: W503
        ):
            raise ValueError(
                "Dataframe incompleto. Colunas esperadas: contagem, tema, samples_idx e quantiles, colunas apresentadas {}".format(
                    temas_df.columns
                )
            )
        return temas_df

    def pertinencia(self, sim, tema_idx):
        max = self.temas.at[tema_idx, "quantiles"].tolist()[-1]
        min = self.temas.at[tema_idx, "quantiles"].tolist()[0]
        if min != max:
            return 100 * (sim - min) / (max - min)
        else:
            return False

    def predict(
        self, texto, ordenar_por="pertinencia", limiar_pert=-10000, limiar_sim=0
    ):

        logger.info("Text to TFIDF")

        output = []
        preprocessed = Pipeline(
            disabled_steps=["spellcheck", "tokenize", "transform_ner", "lemmatize"],
            embedding=False,
        ).apply(texto, verbose=False)
        sample_tfidf = self.vectorizer.transform([preprocessed])

        logger.info("Generate Similarities from text to all")
        sim_vec = (sample_tfidf * self.tfidf.T).toarray().reshape((-1))

        logger.info(
            "For each theme, get pertinence, " "max, average and min similarities"
        )

        for t, row in self.temas.iterrows():
            if row["contagem"] > 2 and set(row["tema"]) != set([0]):
                sim_t = sim_vec[
                    row["samples_idx"]
                ].tolist()  # lista de similaridades do tema
                sim_t.sort()
                avg_sim_t = sum(sim_t) / len(sim_t)  # similaridade media
                q = np.quantile(
                    sim_t, [0, 0.25, 0.5, 0.75, 1]
                )  # ultimo elemento 'e a similaridade maxima'
                p1 = self.pertinencia(q[-1], t)  # calcula a pertinencia
                if p1:
                    # filtra de acordo com os criterios de pertinencia e
                    # similaridade
                    if p1 >= limiar_pert and q[-1] >= limiar_sim:
                        output.append(
                            (p1, q[-1], avg_sim_t, q[0], row["tema"], row["contagem"])
                        )

                        # devolve: pertinencia, similaridade maxima, media e
                        # minima, tema e numero de amostras do tema

        logger.info("Order the results by pertinence or maximum similarity")

        if ordenar_por == "pertinencia":
            output = sorted(output, key=lambda x: x[0])[::-1]
        elif ordenar_por == "similaridade":
            output = sorted(output, key=lambda x: x[1])[::-1]
        else:
            print("warning: opcao de ordenamento nao reconhecida")
        return output
