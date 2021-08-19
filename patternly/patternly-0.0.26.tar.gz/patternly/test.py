import pickle

class PFSA:
    def __init__(self, ann_err, mrg_eps, syn_str, sym_frq, pitilde, connx):
        self.ann_err = ann_err
        self.mrg_eps = mrg_eps
        self.syn_str = syn_str
        self.sym_frq = sym_frq
        self.pitilde = pitilde
        self.connx = connx

def save_model(path="model.pickle"):
    """ Save model to file

    Args:
        path (str): path to save model to
    """

    # if not self.fitted:
    #     raise ValueError("Model has not been fit yet")

    # for _, cluster_file in enumerate(self.cluster_files):
    #     with open(cluster_file, "r") as f:
    #         cluster_str = f.read()
    #         print(cluster_str)

    cluster_file = "examples/zed_temp/clean_392bb683-80be-4f97-b645-b42575717335"
    with open(cluster_file, "r") as f:
        next_val = lambda f: next(f).split(":")[1].strip()
        ann_err = float(next_val(f))
        mrg_eps = float(next_val(f))
        syn_str = next_val(f)
        sym_frq = [float(n) for n in next_val(f).split(" ")]
        size = int(next_val(f).split("(")[1].split(")")[0])
        next(f) # skip #PITILDE line
        pitilde = [[float(val) for val in next(f).strip().split(" ")] for _ in range(size)]
        size = int(next_val(f).split("(")[1].split(")")[0])
        next(f) # skip #CONNX line
        connx = [[int(val) for val in next(f).strip().split(" ")] for _ in range(size)]


    with open("examples/zed_temp/clean_8b15ee5c-3f65-4786-8bc2-73981a05fb81.png", "rb") as f:
        png_bytes = f.read()

    d = {0: {
            "%ANN_ERR": ann_err,
            "%MRG_EPS": mrg_eps,
            "%SYN_STR": syn_str,
            "%SYM_FRQ": sym_frq,
            "%PITILDE": pitilde,
            "%CONNX": connx,
        },
        "model": PFSA(ann_err, mrg_eps, syn_str, sym_frq, pitilde, connx),
    }


    p = PFSA(ann_err, mrg_eps, syn_str, sym_frq, pitilde, connx)
    with open(path, "wb") as f:
        pickle.dump(d, f)

    with open(path, "rb") as f:
        model = pickle.load(f)

    pfsa_objs = model[0]
    with open("test.pfsa", "w") as f:
        f.write(f"%ANN_ERR: {pfsa_objs['%ANN_ERR']}\n")
        f.write(f"%MRG_EPS: {pfsa_objs['%MRG_EPS']}\n")
        f.write(f"%SYN_STR: {pfsa_objs['%SYN_STR']}\n")
        f.write(f"%SYM_FRQ: ")
        for sym_frq in pfsa_objs["%SYM_FRQ"]:
            suffix = " " if str(sym_frq) != str(pfsa_objs["%SYM_FRQ"][-1]) else " \n"
            f.write(f"{sym_frq}{suffix}")
        f.write(f"%PITILDE: size({len(pfsa_objs['%PITILDE'])})\n")
        f.write(f"#PITILDE\n")
        for pitilde in pfsa_objs["%PITILDE"]:
            for val in pitilde:
                suffix = " " if str(val) != str(pitilde[-1]) else " \n"
                f.write(f"{val}{suffix}")
        f.write(f"%CONNX: size({len(pfsa_objs['%CONNX'])})\n")
        f.write(f"#CONNX\n")
        for connx in pfsa_objs["%CONNX"]:
            for val in connx:
                suffix = " " if str(val) != str(connx[-1]) else " \n"
                f.write(f"{val}{suffix}")
        f.write("\n")

save_model()