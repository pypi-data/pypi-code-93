
def annotation_arguments_to_map(annotation):
    annotations = {}
    if annotation:
        for a in annotation:
            try:
                (k, v) = a.split('=', 1)
                if not k:
                    raise KeyError(f"found null key for annotation {a}")

                if not v:
                    raise AttributeError(f"found null value for annotation {a}")

                annotations[k] = v
            except ValueError:
                raise ValueError(f"annotation format error - annotations must be of the form "
                                 f"(--annotation key=value), found: {a}")
    return annotations
