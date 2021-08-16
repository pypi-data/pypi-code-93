import os
import shlex
import subprocess

from Bio import SeqIO

from pandas import DataFrame

class FastaDataFrame(DataFrame):
    
    def __init__(self, data=None, index=None, columns=None, dtype=None, copy=False):
        super().__init__(data, index, columns, dtype, copy)

class Fasta:
    
    @staticmethod
    def read_fasta(in_file, file_type="fasta") -> FastaDataFrame:
        fasta = SeqIO.parse(in_file, file_type)
        del in_file

        data = {}
        data["desc"] = []
        data["seq"] = []
        data["size"] = []

        for f in fasta:
            data["desc"].append(str(f.description))
            data["seq"].append(str(f.seq))
            data["size"].append(len(str(f.seq)))
        del fasta

        df = FastaDataFrame.from_dict(data=data)
        del data

        return df

    @staticmethod
    def to_fasta():
        pass

class Align:

    @staticmethod
    def mafft(input, stdout, stderr, out_order="inputorder", strategy="auto", thread=-1, maxiterate=0, base_dir=None):
        BASE_DIR = base_dir or os.path.dirname(os.path.abspath(__file__))
        mafft = os.path.join(BASE_DIR, "mafft")
        args = shlex.split(f"""{mafft} --{strategy} --{out_order} --maxiterate {maxiterate} --thread {thread} "{input}" """)
        p = subprocess.Popen(args, stdout=stdout, stderr=stderr)
        p.wait()
        return p

class Tree:
    pass