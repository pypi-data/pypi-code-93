__all__ = ["_is_validate_align","_is_validate_overfill","_is_validate_coltype"]

COLTYPES = ["grid","indexed","nogrid"]
OVERFILL = ["scale","newtable","encode"]
ALIGN = ["c","l","r"]

def _is_validate_align(pos):
    if pos in ALIGN:
        return True
    else:
        print("You should write a valid value for the align parameter")
        return False

def _is_validate_overfill(overfill):
    if overfill in OVERFILL:
        return True
    else:
        print("You should write a valid value for the ovefill parameter")
        return False
    
def _is_validate_coltype(col):
    if col in COLTYPES:
        return True
    else:
        print("You should write a valid value for the coltype parameter")
        return False

def _validate_options(options):
    if not _is_validate_align(options['align']):
        return False
    if not _is_validate_coltype(options['coltype']):
        return False
    if not _is_validate_overfill(options["overfill"]):
        return False
    else:
        return True