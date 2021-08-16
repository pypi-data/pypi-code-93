import os
import sqlite3

import pandas as pd
import plotly.express as px

from tempfile import NamedTemporaryFile

from collections import Counter
from collections import OrderedDict

from fastanalizer.pyfasta.pyfastatools import Fasta


def geral(BASE_DIR, output="HTML"):
    conn = sqlite3.connect(os.path.join(BASE_DIR, "fastanalizer.sqlite3"))
    cursor = conn.cursor()

    cursor.execute("SELECT id, dsc_sequencia, cd_requisicao, nm_titulo FROM pipeline_requisicao WHERE sn_geral = 0 and dt_conclusao IS NULL")

    jobs = cursor.fetchall()

    for job in jobs:

        if not os.path.exists(os.path.join(job[2], "general")):
            os.makedirs(os.path.join(job[2], "general"))

        title = job[3]

        temp = NamedTemporaryFile(mode="w+t")
        temp.write(job[1])
        temp.seek(0)

        df = Fasta.read_fasta(temp)
        del temp

        ddf = df.describe()
        ddf = ddf.reset_index()
        ddf = ddf.astype({"index":"category"})
        ddf = ddf.rename(columns={"index":"Metrics"})

        fig = px.bar(ddf, x="size", y="Metrics", title=f"{title or 'FASTA'} - Sequence Metrics", template="plotly_white", color="Metrics")
        fig.update_layout(font_family="Roboto")    
        fig.update_yaxes(type="category")

        if output == "HTML":
            fig.write_html(os.path.join(job[2], "general", "metrics.html"))
        elif output in ["PNG", "SVG", "PDF"]:
            fig.write_image(os.path.join(job[2], "general", f"metrics.{output.lower()}"), engine="kaleido")
        else:
            fig.write_html(os.path.join(job[2], "general", "metrics.html"))


        del fig
        del ddf

        aa = OrderedDict(Counter(df['seq'].str.cat()))
        bb = {}
        bb["Amino acids"] = list(aa.keys())
        bb["Count"] = list(aa.values())
        del aa

        df = pd.DataFrame.from_dict(bb)
        df["Percentage"] = df.groupby(["Amino acids"]).apply(lambda x: 100 * x / df["Count"].sum())
        fig = px.scatter(df, x="Amino acids", y="Percentage", size="Count", title="Amino acids distribution", template="plotly_white", color="Amino acids")
        fig.update_layout(font_family="Roboto", showlegend=False)
        
        if output == "HTML":
            fig.write_html(os.path.join(job[2], "general", "aa.html"))
        elif output in ["PNG", "SVG", "PDF"]:
            fig.write_image(os.path.join(job[2], "general", f"aa.{output.lower()}"), engine="kaleido")
        else:
            fig.write_html(os.path.join(job[2], "general", "aa.html"))
        
        del fig
        del bb
        del df

        cursor.execute(f"""UPDATE pipeline_requisicao SET sn_geral = True WHERE id = {job[0]}""")
        conn.commit()
        
    cursor.close()
    conn.close()

    return 0