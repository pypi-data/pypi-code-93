def write_csv(file_location: str, text: str):
    with open(file_location, "wb+") as f_out:
        for line in text.split("\n"):
            if line.split(",")[0] == "":
                break
            f_out.write((line + "\n").encode("utf-8"))
