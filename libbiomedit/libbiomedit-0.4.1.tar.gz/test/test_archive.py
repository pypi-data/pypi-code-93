import io
import tarfile
import tempfile
import unittest
import zipfile
from datetime import datetime

from libbiomedit.archive import archive_reader


def make_tar(content, path: str):
    with tarfile.open(path, mode="w") as tar:
        for f_name, f_content in content:
            f_io_content = io.BytesIO(f_content)
            t_info = tarfile.TarInfo(f_name)
            t_info.size = len(f_io_content.getvalue())
            tar.addfile(t_info, f_io_content)


def make_zip(content, path: str):
    with zipfile.ZipFile(path, mode="w") as zip_obj:
        for f_name, f_content in content:
            zip_obj.writestr(
                zipfile.ZipInfo(f_name, date_time=datetime.utcnow().timetuple()[:6]),
                f_content,
            )


class TestArchiveReader(unittest.TestCase):
    def test_reader(self):
        archive_content = (
            ("metadata.json", b'{"test": true}'),
            ("data.tar.gz.gpg", b"some initial binary data: \x00\x01"),
            ("metadata.json.sig", b"Some signature"),
        )
        with tempfile.NamedTemporaryFile() as tmp:
            for archive_fn in (make_zip, make_tar):
                with self.subTest(archive_fn.__name__):
                    archive_fn(archive_content, tmp.name)
                    with archive_reader(tmp.name) as archive:
                        # Existing files
                        for file_name, content in archive_content:
                            self.assertEqual(
                                archive.extract_member(file_name).read(), content
                            )
                        self.assertListEqual(
                            archive.namelist(), [x[0] for x in archive_content]
                        )
                        # Missing file
                        missing_file_name = "missing.json"
                        with self.assertRaises(KeyError) as cm:
                            archive.extract_member(missing_file_name)
                        self.assertEqual(
                            str(cm.exception),
                            f"'File object {missing_file_name} not found in {tmp.name}'",
                        )

            with self.subTest("Not at file"):
                name = "not_a_file"
                with tarfile.open(tmp.name, mode="w") as tar:
                    t_info = tarfile.TarInfo(name)
                    t_info.type = tarfile.DIRTYPE
                    tar.addfile(t_info, b"")
                with archive_reader(tmp.name) as archive:
                    with self.assertRaises(KeyError):
                        archive.extract_member(name)

            with self.subTest("Not an archive"):
                tmp.truncate()
                tmp.write(b"foo")
                with self.assertRaises(TypeError) as cm:
                    with archive_reader(tmp.name):
                        pass
                self.assertEqual(
                    str(cm.exception),
                    f"Input file '{tmp.name}' is not a .zip or .tar archive.\n"
                    "Only .zip and .tar files can be used as input.",
                )
