import sqlite3
import os
import re

from tempfile import NamedTemporaryFile
from Bio import SeqIO

import pandas as pd

from fastanalizer.pyfasta.pyfastatools import Align

def align(BASE_DIR):
    conn = sqlite3.connect(os.path.join(BASE_DIR, "fastanalizer.sqlite3"))
    cursor = conn.cursor()

    cursor.execute("""SELECT id, dsc_sequencia, cd_requisicao FROM pipeline_requisicao WHERE sn_cdsearch = True AND sn_align = False AND sn_error = False AND dt_conclusao IS NULL""")
    jobs = cursor.fetchall()

    for job in jobs:

        if not os.path.exists(os.path.join(job[2], "domainsearch")):
            print("Pasta não existe: {}".format(job[2]))
            continue    
        if not os.path.exists(os.path.join(job[2], "align")):
            os.makedirs(os.path.join(job[2], "align"))

        frames = []
        for f in os.listdir(os.path.join(job[2], "domainsearch")):
            if (f.startswith("hitdata")) and (f.endswith(".txt")):
                df = pd.read_csv(os.path.join(job[2], "domainsearch", f), skiprows=7, sep="\t")
                frames.append(df)
        if len(frames) > 0:
            df = pd.concat(frames)
            del frames

            df["database"] = df["Accession"].apply(lambda x: re.search(r"[A-z]+", x).group(0))
            df["Query"] = df["Query"].apply(lambda x: re.sub(r"Q#[0-9]+\s-\s>","",x))

        temp = NamedTemporaryFile(mode="w+t")
        temp.write(job[1])
        temp.seek(0)

        fasta = SeqIO.parse(temp, "fasta")
        SeqIO.write(fasta, os.path.join(job[2], "align", "base.fasta"), "fasta")
        
        temp.seek(0)
        fasta = SeqIO.parse(temp, "fasta")
        del temp
        
        seqs = {}
        seqs["Query"] = []
        seqs["Sequence"] = []
        for f in fasta:
            seqs["Query"].append(f.description)
            seqs["Sequence"].append(str(f.seq))
        
        del fasta

        fdf = pd.DataFrame.from_dict(seqs)
        df = pd.merge(df, fdf, on="Query", how="right")

        del fdf

        df = df[df.Accession == df.query("""`Hit type` == 'specific'""").groupby(["database"]).Accession.value_counts().nlargest(1).rename_axis(["Database","Accession"]).reset_index(name='Count').iloc[0]["Accession"]].reset_index(drop=True)

        #df = df.query("""`Hit type` == 'specific'""")
        df["Sequence"] = df.apply(lambda x: x["Sequence"][x["From"]:x["To"]], axis=1)

        df = df.sort_values(by=["Bitscore"], ascending=False)
        df = df.drop_duplicates(subset=["Sequence"], keep="first")
        df["RQuery"] = "seq" + df.index.map(str)

        df[["Query", "RQuery", "Sequence"]].to_csv(os.path.join(job[2], "align", "rename.txt"), index=False, sep="\t")
        
        seqs = df[["RQuery", "Sequence"]].to_dict("split")
        saida = open(os.path.join(job[2], "align", "job.fasta"), "w")
        for seq in seqs["data"]:
            saida.write(">" + seq[0] + "\n")
            saida.write(seq[1] + "\n")
        saida.close()

        stdout = open(os.path.join(job[2], "align", "align.fasta"), "w")
        stderr = open(os.path.join(job[2], "align", "align-stderr.fasta"), "w")

        p = Align.mafft(os.path.join(job[2], 'align', 'job.fasta'), stdout, stderr)

        stdout.close()
        stderr.close()

        cursor.execute("""UPDATE pipeline_requisicao SET sn_align = True WHERE id = {}""".format(job[0]))
        conn.commit()
    
    cursor.close()
    conn.close()
    return 0