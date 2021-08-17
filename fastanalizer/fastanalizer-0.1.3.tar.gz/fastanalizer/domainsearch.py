import sqlite3
import os
import requests
import re
import multiprocessing
import time
from datetime import datetime

from tempfile import NamedTemporaryFile
from Bio import SeqIO

#From biopython.org large file spliter, modified to work
def batch_iterator(iterator, batch_size):
    entry = True
    while entry:
        batch = []
        while len(batch) < batch_size:
            try:
                entry = iterator.__next__()
            except StopIteration:
                entry = None
            if entry is None:
                break
            batch.append(entry)
        if batch:
            yield batch

class SearchCdSearch(multiprocessing.Process):

    def __init__(self, cd_requisicao, count, data, url):
        multiprocessing.Process.__init__(self)
        self.cd_requisicao = cd_requisicao
        self.data = data
        self.url = url
        self.count = count
        self.processID = str(cd_requisicao) + "-" + str(count)

    def run(self):
        #Inicia a busca
        params = {
            "useid1":"true",
            "compbasedadj":1,
            "maxhit":250,
            "tdata":"hits",
            "dmode":"full",
            "queries": self.data
        }
        status = ""
        cdsid = ""
        while True:
            r = requests.post(self.url, data=params) #Retorno da busca usando POST
            if (r.status_code == 200): #HTTP status code
                status = re.search(r"(status)\s+[0-9]", r.text) #Job status code
                if (status != "") and (status is not None):
                    status = re.split(r"\s",status.group(0))[-1]
                    if (status == "3") or (status == "0"):
                        cdsid = re.search(r"(cdsid)\s+(([0-z])+(\-)*)+",r.text)
                        cdsid = re.split(r"\s", cdsid.group(0))[-1]
                        break
                    else:
                        print("="*60)
                        print(self.processID)
                        print("Erro ao iniciar request")
                        print(r.text)
                        print("="*60)
                        break
            time.sleep(30)

        params = {
            "cdsid":cdsid,
            "dmode":"full",
            "tdata":"hits",
        }

        while True:
            r = requests.post(self.url, params=params)
            if (r.status_code == 200): #HTTP status code
                status = re.search(r"(status)\s+[0-9]", r.text) #Job status code
                if (status != "") and (status is not None):
                    status = status.group(0)[-1]
                    if status == "0":
                        fileName = "hitdata-" + str(self.count) + ".txt"
                        arquivo = open(os.path.join(self.cd_requisicao, "domainsearch", fileName), "w")
                        arquivo.write(r.text)
                        arquivo.close()
                        break
                    elif status == "3":
                        time.sleep(10)
                    else:
                        print("="*60)
                        print(self.processID)
                        print("Erro ao recuperar request")
                        print("Erro. Status {}".format(status))
                        print("="*60)
                        break

def domainsearch(BASE_DIR):
    conn = sqlite3.connect(os.path.join(BASE_DIR, "fastanalizer.sqlite3"))
    cursor = conn.cursor()

    cursor.execute("SELECT id, dsc_sequencia, cd_requisicao FROM pipeline_requisicao WHERE sn_cdsearch = 0 and dt_conclusao IS NULL")
    jobs = cursor.fetchall()

    joblist = []

    url = """https://www.ncbi.nlm.nih.gov/Structure/bwrpsb/bwrpsb.cgi"""

    for job in jobs:

        if not os.path.exists(os.path.join(job[2], "domainsearch")):
            os.makedirs(os.path.join(job[2], "domainsearch"))

        temp = NamedTemporaryFile(mode="w+t")
        temp.write(job[1])
        temp.seek(0)

        fasta = SeqIO.parse(temp, "fasta")

        for i, fa in enumerate(batch_iterator(fasta, 2000)):
            tempFasta = NamedTemporaryFile(mode="w+t")
            SeqIO.write(fa, tempFasta, "fasta")
            tempFasta.seek(0)
            th = SearchCdSearch(cd_requisicao=job[2], data=tempFasta.read(), count=i, url=url)
            joblist.append(th)

    for job in joblist:
        job.start()
        
    for job in joblist:
        job.join()

    for job in jobs:
        flag = 1
        for f in os.listdir(os.path.join(job[2], "domainsearch")):
            if f.endswith(".txt"):
                cursor.execute("""UPDATE pipeline_requisicao SET sn_cdsearch = True WHERE id = {}""".format(job[0]))
                conn.commit()
                flag = 0
                break
        if flag:
            cursor.execute("""UPDATE pipeline_requisicao SET sn_cdsearch = True, sn_error = True, dt_conclusao = {} WHERE id = {}""".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), job[0]))     
            conn.commit()
    cursor.close()
    conn.close()

    return 0