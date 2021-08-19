import locale

LOC_INIT_123: bool = False


def num_to_currency(value: float, grouping: bool = True) -> str:
    global LOC_INIT_123

    if not LOC_INIT_123:
        locale.setlocale(locale.LC_ALL, "en_US.UTF-8")
        LOC_INIT_123 = True

    return locale.currency(val=value, grouping=grouping)
