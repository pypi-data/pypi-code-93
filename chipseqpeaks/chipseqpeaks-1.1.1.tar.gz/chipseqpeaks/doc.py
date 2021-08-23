#===============================================================================
# doc.py
#===============================================================================

# Constants ====================================================================

DOC = """The command for calling ChIP-seq or ATAC-seq peaks is 
`chipseqpeaks-call`. For ATAC-seq, the option `--atac-seq`
should be used. See the documentation by running:

chipseqpeaks-call --help
"""




# Functions ====================================================================

def main():
    print(DOC, end='')
