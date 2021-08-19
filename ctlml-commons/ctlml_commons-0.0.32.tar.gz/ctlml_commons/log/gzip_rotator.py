import gzip
import os


class GZipRotator:
    def __call__(self, source: str, destination: str):
        os.rename(source, destination)

        with open(destination, "rb") as file_in:
            with gzip.open("%s.gz" % destination, "wb") as file_out:
                file_out.writelines(file_in)

        os.remove(destination)
