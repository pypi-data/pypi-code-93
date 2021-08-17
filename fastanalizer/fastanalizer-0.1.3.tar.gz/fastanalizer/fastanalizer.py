import argparse
import uuid
import sqlite3
import os
import concurrent.futures
from operator import attrgetter
from datetime import datetime

from Bio import SeqIO

from fastanalizer.geral import geral
from fastanalizer.domainsearch import domainsearch
from fastanalizer.pdomain import domaintrim
from fastanalizer.align import align
from fastanalizer.tree import nj_tree


class SortingHelpFormatter(argparse.RawDescriptionHelpFormatter):
    def add_arguments(self, actions):
        actions = sorted(actions, key=attrgetter('option_strings'))
        super(SortingHelpFormatter, self).add_arguments(actions)

def main():

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    CONN = sqlite3.connect(os.path.join(BASE_DIR, "fastanalizer.sqlite3"))
    CURSOR = CONN.cursor()
    HIGH = ["HIGH"]
    LOW = [*HIGH,"LOW"]
    LOG = [*LOW, "LOG"]

    desc = f"""    {'-'*40}
    FastAnalizer v0.1 Alpha (2021/Ago)
    Fast usage: fastanalizer myfile.fasta
    {'-'*40}"""

    parser = argparse.ArgumentParser(description=desc, formatter_class=SortingHelpFormatter)

    ##Requireds
    parser.add_argument('file', nargs=1, help="A multifasta file to analize")

    ##Optionals
    parser.add_argument('--title', help="A title to the project")
    parser.add_argument('--database', help="The database used for domain searching and trimming.", choices=["PFAM", "CDD", "COG", "TIGRFAM", "ALL"], default="ALL")
    parser.add_argument('--checkpoint', help="Restart project on given checkpoint. Must inform project ID", choices=sorted(["ALIGN","DOMAINSEARCH", "GERAL", "PHYLO","DOMAINTRIM"]))
    parser.add_argument('--id', help="Project ID. Required for checkpoint usage.")
    parser.add_argument('--verbose', help="Application verbose level. Default to high verbose.", choices=["LOG", "LOW", "HIGH"], default="HIGH")
    parser.add_argument('--output', help="Set graphs output format", choices=["HTML", "PNG", "SVG", "PDF"], default="HTML")

    args = parser.parse_args()

    with open(args.file[0], "r") as arquivo:
        texto = SeqIO.parse(arquivo, "fasta")
        if not any(texto):
            raise Exception("Empty file provided.")
        del texto

        arquivo.seek(0)
        dsc_sequencia = arquivo.read()
        cd_requisicao = str(uuid.uuid4())
        dt_requisicao = datetime.now().isoformat()
        nm_titulo = args.title or "Analysis"
        tp_database = args.database

        sql = f"""INSERT INTO pipeline_requisicao (
                dsc_sequencia,
                cd_requisicao,
                dt_requisicao,
                nm_titulo,
                tp_database
            )
            VALUES (
                "{dsc_sequencia}",
                "{cd_requisicao}",
                "{dt_requisicao}",
                "{nm_titulo}",
                "{tp_database}"
            )
        """

        CURSOR.execute(sql)
        CONN.commit()
        if not CURSOR.lastrowid:
            raise Exception("Start project failed.")

        if args.verbose in LOW:
            print(f"Requisition code: {cd_requisicao}")
            print(f"Requisition date: {dt_requisicao}")
            print(f"Requisition title: {nm_titulo or 'Not provided'}")

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(geral, BASE_DIR=BASE_DIR, output=args.output),
            executor.submit(domainsearch, BASE_DIR=BASE_DIR)
        ]
    for future in concurrent.futures.as_completed(futures, timeout=200):
        result = future.result()
        if result:
            print(f"Falha a verificar")

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(domaintrim, BASE_DIR=BASE_DIR, database=tp_database, output=args.output)
        ]
    for future in concurrent.futures.as_completed(futures, timeout=200):
        result = future.result()
        if result:
            CONN.commit()
            CONN.close()
            raise Exception()

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(align, BASE_DIR=BASE_DIR)
        ]
    for future in concurrent.futures.as_completed(futures, timeout=200):
        result = future.result()
        if result:
            CONN.commit()
            CONN.close()
            raise Exception()

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(nj_tree, BASE_DIR=BASE_DIR, nm_titulo=nm_titulo, output=args.output)
        ]
    for future in concurrent.futures.as_completed(futures, timeout=200):
        result = future.result()
        if result:
            CONN.commit()
            CONN.close()
            raise Exception()

    CURSOR.execute(f"""UPDATE pipeline_requisicao SET dt_conclusao = "{datetime.now().isoformat()}" WHERE cd_requisicao = "{cd_requisicao}" """)
    CONN.commit()
    CONN.close()

if __name__ == '__main__':
    main()