"""
Convert data to EDICTOR's Sqlite format.
"""
from lexibase import LexiBase
from lingpy import Wordlist


def get_lexibase(
        path, name, columns=None, preprocessing=None, namespace=None,
        lexibase=False):

    wordlist = Wordlist.from_cldf(
            path,
            columns=columns or (
                "language_id",
                "concept_name",
                "value",
                "form",
                "segments",
                "comment"),
            namespace=namespace or dict([
                ("language_id", "doculect"),
                ("concept_name", "concept"),
                ("value", "value"),
                ("form", "form"),
                ("segments", "tokens"),
                ("comment", "note")
                ]))

    if preprocessing:
        D = preprocessing(wordlist)
    else:
        D = {idx: wordlist[idx] for idx in wordlist}
        D[0] = wordlist.columns

    if not lexibase:
        Wordlist(D).output("tsv", filename=name, ignore="all", prettify=False)
    else:
        lex = LexiBase(D, dbase=name+".sqlite3")
        lex.create(name)

    
