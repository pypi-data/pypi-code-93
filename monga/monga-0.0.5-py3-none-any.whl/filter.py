# ==============================
# belum terpakai
# ==============================
class Filter:
    def limit(lim: int = 10):
        return lim

    def skip(page: int = 1, lim: int = 10):
        return (page - 1) * lim
