import os
import re
import sys
import operator
import subprocess



def runshell(args, type = ""):
    
    if type == "stdout":
        a, b = args
        with open(b, "w") as f:
            subprocess.call(a, stdout= f)

    else:
        p = subprocess.Popen(args)
        p.communicate()


def export_fasta(aln: dict, outname: str):
    """
    This function assumes sequences names
    are already formated (i.e., names starting with ">")
    """
    with open(outname, 'w') as f:
        for k,v in aln.items():
            f.write( "%s\n%s\n" % (k,v))


def fas_to_dic(file):
    
    file_content = open(file, 'r').readlines()
    seqs_list   = []
    
    for i in file_content:
        line = i.strip()
        if line: # just if file starts empty
            seqs_list.append(line) 
    
    keys = [] 
    values = []    
    i = 0
    while(">" in seqs_list[i]):
        keys.append(seqs_list[i])
        i += 1 
        JustOneValue = []

        while((">" in seqs_list[i]) == False):
            JustOneValue.append(seqs_list[i]) 
            i += 1

            if(i == len(seqs_list)):
                i -= 1
                break

        values.append("".join(JustOneValue).upper().replace(" ", ""))
        
    return dict(zip(keys, values))


def remove_files(files):

    for f in files:
        try:
            os.remove(f)
        except FileNotFoundError:
            pass

def check_empty_positions(aln, file, outname):
    # file = '/Users/ulises/Desktop/GOL/software/GGpy/demo/toggi/E1644.fasta_2_ggi.tsv'
    # aln = fas_to_dic(file)
    gap_chars = set(['N', '-', '!', '?'])
    seq_len = len(next(iter(aln.values())))

    all_char_pos1 = set()
    all_char_pos2 = set()
    all_char_pos3 = set()

    for v in aln.values():
        for p in range(0, seq_len, 3):
            all_char_pos1.update(v[p])
            all_char_pos2.update(v[p + 1])
            all_char_pos3.update(v[p + 2])

    is_pos1_empty = not (all_char_pos1 - gap_chars)
    is_pos2_empty = not (all_char_pos2 - gap_chars)
    is_pos3_empty = not (all_char_pos3 - gap_chars)

    all_empty = is_pos1_empty and is_pos2_empty and is_pos3_empty
    all_filled = not is_pos1_empty and not is_pos2_empty and not is_pos3_empty

    if all_empty:
        sys.stderr.write("'%s' file has only gap characters\n" % file)
        sys.stderr.flush()
        sys.exit(1)

    if all_filled:
        return False

    new_aln = {}
    for k,v in aln.items():
        mystr = ""
        for i in range(0, seq_len, 3):

            F = '' if is_pos1_empty else v[i]
            S = '' if is_pos2_empty else v[i + 1]
            T = '' if is_pos3_empty else v[i + 2]
            mystr += (F + S + T)

        new_aln[k] = mystr
    
    seq_new_len = len(next(iter(new_aln.values())))

    filled = 3 - sum([is_pos1_empty, is_pos2_empty, is_pos3_empty])
    with open(outname, 'w') as outf:
        for i in range(filled):
            outf.write(
                "DNA, p{pos} = {pos}-{seq_len}\\{npart}\n".format(
                    pos = i + 1,
                    seq_len = seq_new_len,
                    npart = filled
                )
            )
    
    with open(file, 'w') as f:
        for k,v in new_aln.items():
            f.write( "%s\n%s\n" % (k,v))
            
    return True

def codon_partitions(file, outname = None):

    aln = fas_to_dic(file)
    lengths = set([len(v) for _,v in aln.items()])

    if lengths.__len__() > 1:
        sys.stderr.write("'%s' file has sequences with different lengths\n" % file)
        sys.stderr.flush()
        sys.exit(1)

    procesed = check_empty_positions(aln, file, outname)

    if procesed:
        return None
    
    aln_length = lengths.pop()
    
    with open(outname, 'w') as outf:
        outf.write("DNA, p1 = 1-%s\\3\n" % aln_length)
        outf.write("DNA, p2 = 2-%s\\3\n" % aln_length)
        outf.write("DNA, p3 = 3-%s\\3\n" % aln_length)

    return None

def _filter(indexes: list, aln: dict, seqlength: int, offset: int) -> dict:
    """
    if indexes list is empty, it means
    there is anything to save because any column
    pass the maximun allowed proportion condition.

    then, return None
    """

    if not indexes:
        return None

    out = {}
    for k,v in aln.items():
        mystr  = ""
        for c in range(0, seqlength, offset):
            if c in indexes:
                mystr += v[c:c+offset]
        out[k] = mystr

    seqlength = _seq_length(out)

    if not seqlength:
        return None

    return out

def _get_gap_prop(aln: dict, seqlength: int, offset: int)-> dict:

    idxs = []
    for c in range(0, seqlength, offset):

        mystr = ""
        for v in aln.values():
            mystr += v[c:c+offset]

        gap_prop = mystr.count('-')/len(mystr)
        idxs.append( (c, gap_prop) )

    return idxs

def _seq_length(aln:dict)-> int:
    return len(next(iter(aln.values())))

def convertMissing2Gap(aln: dict, isprot = False) -> dict:

    for k,v in aln.items():
        if isprot:
            aln[k] = v.replace("X", "-")

        else:
            aln[k] = v.replace("N", "-")

    return aln

def close_gaps(aln: dict, is_codon_aware: bool = True, model: str = 'GTRGAMM') -> dict:
    """
    Moves:
    1. It converts N to gaps
    2. get proportions
    3. filter


    * If `aln` is empty, returns None
    * If `aln` is not empty, `aln` has values with length
    * If not seqlength after processing, None is returned
    """
    # aln = {'a':'---cat--a', 'b':'---cat--a'}
    # is_codon_aware = not True
    if not aln:
        return None
        
    offset    = 3 if is_codon_aware else 1
    aln       = convertMissing2Gap( aln = aln, isprot = re.findall('^PROT', model) )
    seqlength = _seq_length(aln)

    idxs = []
    idxs_prop = _get_gap_prop(aln, seqlength, offset)

    for c, gap_prop in idxs_prop:
        if not gap_prop == 1:
            idxs.append(c)

    return _filter(idxs, aln, seqlength, offset)
