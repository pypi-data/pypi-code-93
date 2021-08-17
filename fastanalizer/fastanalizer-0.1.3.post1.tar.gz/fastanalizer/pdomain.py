import sqlite3
import os
import re

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

from sklearn.preprocessing import MinMaxScaler

def domaintrim(BASE_DIR, database="ALL", output="HTML"):
    conn = sqlite3.connect(os.path.join(BASE_DIR, "fastanalizer.sqlite3"))
    cursor = conn.cursor()

    cursor.execute("""SELECT id, dsc_sequencia, cd_requisicao FROM pipeline_requisicao WHERE sn_cdsearch = True AND sn_pdomain = False AND sn_error = False AND dt_conclusao IS NULL""")
    jobs = cursor.fetchall()

    for job in jobs:

        if not os.path.exists(os.path.join(job[2], "domainsearch")):
            print("Dir not found: {}".format(job[2]))
            continue    
        if not os.path.exists(os.path.join(job[2], "pdomain")):
            os.makedirs(os.path.join(job[2], "pdomain"))

        
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

            #ddf = df.query("""Incomplete == ' - ' & `Hit type` == 'specific'""").groupby(["database", "Hit type"]).count()

            #ddf = df.query("""`Hit type` == 'specific'""").groupby(["database", "Accession"]).count()
            edf = df.query("""`Hit type` == 'specific'""").groupby(["database"]).Accession.value_counts().nlargest(10).rename_axis(["Database","Accession"]).reset_index(name='Count')
            
            #Bitscore
            ddf = df[["Hit type", "database", "Accession", "Bitscore"]].query("""`Hit type` == 'specific'""").groupby(["database","Accession"]).mean()
            ddf["Normalized Bitscore"] = (MinMaxScaler().fit_transform(ddf[["Bitscore"]].values.astype(float)))*(edf["Count"].values.max()/2)

            #Evalue
            dddf = df[["Hit type", "database", "Accession", "E-Value"]].query("""`Hit type` == 'specific'""").groupby(["database","Accession"]).mean()
            ddf["NormEvalue"] = MinMaxScaler().fit_transform(dddf[["E-Value"]].values.astype(float))
            
            result = pd.merge(edf, ddf, on="Accession", how="left")
            result = pd.merge(result, dddf, on="Accession", how="left")

            fig = go.Figure()
            fig = px.bar(result, x="Accession", y="Count",title="Protein Domains - Specific hits", template="plotly_white", color="Database")

            fig.add_trace(
                go.Scatter(x=result[["Accession"]].values.reshape(1,-1).tolist()[0], y=result[["Normalized Bitscore"]].values.reshape(1,-1).tolist()[0], name="Normalized Bitscore", line=dict(color='CRIMSON', width=2))
            )
            fig.add_trace(
                go.Scatter(x=result[["Accession"]].values.reshape(1,-1).tolist()[0], y=np.array([edf["Count"].values.max()/2 for x in result[["Accession"]].values.reshape(1,-1).tolist()[0]]), name="Max Bitscore", line=dict(color='DARKRED', width=2, dash="dot"))
            )
            fig.update_layout(font_family="Roboto")
            fig.update_xaxes(type="category", categoryarray=result[["Accession"]].values.reshape(1,-1).tolist()[0], categoryorder="array")
            
            #fig.show()
            
            if output == "HTML":
                fig.write_html(os.path.join(job[2], "pdomain", "pdomain.html"))
            elif output in ["PNG", "SVG", "PDF"]:
                fig.write_image(os.path.join(job[2], "pdomain", f"pdomain.{output.lower()}"), engine="kaleido")
            else:
                fig.write_html(os.path.join(job[2], "pdomain", "pdomain.html"))

            cursor.execute("""UPDATE pipeline_requisicao SET sn_pdomain = True WHERE id = {}""".format(job[0]))
            conn.commit()

    cursor.close()
    conn.close()

    return 0