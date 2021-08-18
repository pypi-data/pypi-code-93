from functools import partial
from billiard.pool import Pool
from fastapi import FastAPI
from pydantic import BaseModel, typing
from starlette.responses import JSONResponse
import sys
import liwc
# from cohmetrixBR.run_coh_metrix import CohMetrix
import orjson
sys.path.insert(0, "..")
from cohmetrixBR import connectives, descriptive, lsa, lexical_diversity_coh, situation_model, \
    syntactic_complexity, syntactic_pattern_density
from cohmetrixBR import readability as readability
from cohmetrixBR import word_information as information

import time


class ORJSONResponse(JSONResponse):
    media_type = "application/json"

    # https://levelup.gitconnected.com/introduction-to-orjson-3d06dde79208
    # https://github.com/tiangolo/fastapi/issues/459
    def render(self, content: typing.Any) -> bytes:
        return orjson.dumps(content, option=orjson.OPT_NAIVE_UTC | orjson.OPT_SERIALIZE_NUMPY)


app = FastAPI(default_response_class=ORJSONResponse)


# cohMetrix = CohMetrix()


# pydantic models

def get_columns_values_coh_metrix():
    return ["cm.DESPC", "cm.DESSC", "cm.DESWC", "cm.DESPL", "cm.DESPLd", "cm.DESSL", "cm.DESSLd", "cm.DESWLsy",
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
            "cm.RDFRE", "cm.RDFKGL", "cm.RDL2"]


def get_columns_values_liwc():
    return ["liwc.funct", "liwc.pronoun", "liwc.ppron", "liwc.i", "liwc.we", "liwc.you", "liwc.shehe",
            "liwc.they", "liwc.ipron", "liwc.article", "liwc.verb", "liwc.auxverb", "liwc.past",
            "liwc.present", "liwc.future", "liwc.adverb", "liwc.preps", "liwc.conj", "liwc.negate",
            "liwc.quant", "liwc.number", "liwc.swear", "liwc.social", "liwc.family", "liwc.friend",
            "liwc.humans", "liwc.affect", "liwc.posemo", "liwc.negemo", "liwc.anx", "liwc.anger", "liwc.sad",
            "liwc.cogmech", "liwc.insight", "liwc.cause", "liwc.discrep", "liwc.tentat", "liwc.certain",
            "liwc.inhib", "liwc.incl", "liwc.excl", "liwc.percept", "liwc.see", "liwc.hear", "liwc.feel",
            "liwc.bio", "liwc.body", "liwc.health", "liwc.sexual", "liwc.ingest", "liwc.relativ",
            "liwc.motion", "liwc.space", "liwc.time", "liwc.work", "liwc.achieve", "liwc.leisure",
            "liwc.home", "liwc.money", "liwc.relig", "liwc.death", "liwc.assent", "liwc.nonfl", "liwc.filler"]


def get_features_liwc(text):
    return liwc.liwc_features(text)


# def get_features_coh_metrix(text):
#     return cohMetrix.coh_metrix_features(text)


class StockIn(BaseModel):
    texto: str
    threads: int


class StockOut(BaseModel):
    features: list


# routes


@app.get("/ping")
async def pong():
    return {"ping": "pongasdhasf!"}


# noinspection PyBroadException
def aux(f, text):
    try:
        return f(text)
    except:
        return -1


@app.post("/xtract", status_code=200)
async def get_prediction(payload: StockIn):
    texto = payload.texto
    liwc_features = get_features_liwc(texto)
    coh_metrix_features = [descriptive.DESPC, descriptive.DESSC,
                           descriptive.DESWC, descriptive.DESPL,
                           descriptive.DESPLd, descriptive.DESSL,
                           descriptive.DESSLd, descriptive.DESWLsy,
                           descriptive.DESWLsyd, descriptive.DESWLlt,
                           descriptive.DESWLltd, #referential_cohesion.CRFNO1,
                           #referential_cohesion.CRFAO1, referential_cohesion.CRFSO1,
                           #referential_cohesion.CRFNOa, referential_cohesion.CRFAOa,
                           #referential_cohesion.CRFSOa,
                           #(referential_cohesion.CRFCWO1),
                           #(referential_cohesion.CRFCWO1d),
                           # referential_cohesion.CRFCWOa,
                           # referential_cohesion.CRFCWOad, referential_cohesion.CRFANP1,
                           # referential_cohesion.CRFANPa,
                           lsa.LSASS1, lsa.LSASS1d,
                           (lsa.LSASSp), (lsa.LSASSpd),
                           lsa.LSAPP1,
                           lsa.LSAPP1d, lsa.LSAGN, lsa.LSAGNd,
                           lexical_diversity_coh.LDTTRc,
                           #lexical_diversity_coh.LDTTRa,
                           lexical_diversity_coh.LDMTLDa, lexical_diversity_coh.LDVOCDa,
                           connectives.CNCAll, connectives.CNCCaus,
                           connectives.CNCLogic, connectives.CNCADC,
                           connectives.CNCTemp, connectives.CNCAdd,
                           connectives.CNCPos, connectives.CNCNeg,
                           connectives.CNCAlter, connectives.CNCConclu,
                           connectives.CNCExpli, connectives.CNCConce,
                           connectives.CNCCondi, connectives.CNCConfor,
                           connectives.CNCFinal, connectives.CNCProp,
                           connectives.CNCComp, connectives.CNCConse,
                           connectives.CNCInte, situation_model.SMCAUSv,
                           situation_model.SMCAUSvp, situation_model.SMCAUSr,
                           situation_model.SMCAUSlsa, situation_model.SMCAUSwn,
                           syntactic_complexity.SYNLE, syntactic_complexity.SYNMEDpos,
                           syntactic_complexity.SYNMEDwrd, syntactic_complexity.SYNMEDlem,
                           syntactic_complexity.SYNSTRUTa, syntactic_complexity.SYNSTRUTt,
                           # syntactic_pattern_density.DRNP, syntactic_pattern_density.DRVP,
                           # syntactic_pattern_density.DRAP,
                           # syntactic_pattern_density.DRPP, syntactic_pattern_density.DRPVAL,
                           # syntactic_pattern_density.DRNEG,
                           # syntactic_pattern_density.DRGERUND, syntactic_pattern_density.DRINF,
                           # information.WRDNOUN, information.WRDVERB,
                           # information.WRDADJ, information.WRDADV,
                           # information.WRDPRO,
                           information.WRDPRP1s,
                           information.WRDPRP1p,   ( information.WRDPRP2),
                           information.WRDPRP3s, information.WRDPRP3p,
                           information.WRDFRQc, information.WRDFRQa,
                           information.WRDFRQmc, information.WRDAOAc,
                           information.WRDFAMc, information.WRDCNCc,
                           information.WRDIMGc, information.WRDMEAc,
                           readability.RDFRE, readability.RDFKGL,
                           # readability.RDL2
                           ]
    pool = Pool(threads=payload.threads)
    is_active = (pool.map_async(partial(aux, text=texto), coh_metrix_features))
    is_active.wait()
    pool.close()
    return {"features": liwc_features+is_active.get()}
