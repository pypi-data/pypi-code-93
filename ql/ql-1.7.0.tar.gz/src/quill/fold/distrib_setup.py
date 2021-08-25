__all__ = ["create_ns_aliases", "create_routing_table", "create_manifest"]

def create_ns_aliases(par):
    file_path = par / "alias.mmd"
    lines = [
        "-spin.systems=ss",
        "",
        "-spin=∫:",
        "-:log=",
        "-,:ocu=",
        "-,:arc=app",
        "-,:erg=",
        "-,:opt=",
        "-,:arb=",
        "-,:doc=",
        "",
        "-qu=q:",
        "-:cal=",
        "-,:conf=",
        "-,:pore=biorx",
        "-,:qrx=arx",
        "-,:poll=",
        "-,:reed=",
        "-,:noto=ruinoto",
        "-,:plot=plotspot",
        "-,:labs=",
    ]
    with open(file_path, "w") as f:
        f.write("\n".join(lines))


def create_routing_table(par):
    file_path = par / "routing.mmd"
    lines = [
        "-spin.systems=",
        "",
        "-spin:",
        "-:log=",
        "-,:ocu=",
        "-,:arc=",
        "-,:erg=",
        "-,:opt=",
        "-,:arb=",
        "-,:doc=",
        "",
        "-qu:",
        "-:cal=",
        "-,:conf=",
        "-,:pore=",
        "-,:qrx=",
        "-,:poll=",
        "-,:reed=",
        "-,:noto=",
        "-,:plot=",
        "-,:labs=",
    ]
    with open(file_path, "w") as f:
        f.write("\n".join(lines))


def create_manifest(par):
    file_path = par / "manifest.mmd"
    lines = [
        "-spin.systems:spin-systems:4:",
        "-:cal:qu-cal:3",
        "-,:log:spin-log:4",
        "-,:conf:qu-conf:4",
        "-,:pore:qu-pore:2",
        "-,:ocu:naiveoculus:4",
        "-,:arc:appendens:4",
        "-,:qrx:qu-arx:4",
        "-,:erg:spin-erg:1",
        "-,:opt:spin-opt:1",
        "-,:poll:qu-poll:2",
        "-,:arb:spin-arb:1",
        "-,:reed:qu-reed:3",
        "-,:noto:qu-noto:2",
        "-,:plot:qu-plot:1",
        "-,:doc:spin-doc:2",
        "-,:labs:qu-labs:1",
    ]
    with open(file_path, "w") as f:
        f.write("\n".join(lines))
