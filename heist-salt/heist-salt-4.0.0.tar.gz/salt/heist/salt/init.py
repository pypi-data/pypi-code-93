def __init__(hub):
    for dyne in ("salt", "tool"):
        hub.pop.sub.add(dyne_name=dyne)
    hub.pop.sub.load_subdirs(hub.salt, recurse=True)
