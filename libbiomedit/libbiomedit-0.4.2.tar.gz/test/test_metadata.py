import unittest
from datetime import datetime, timezone, timedelta

from libbiomedit.metadata import MetaData, ValidatedStr, HexStr1024, HexStr256, Purpose


class TestMetadata(unittest.TestCase):
    def test_validata_type_meta(self):
        def check(x, y):
            def _c(s):
                if not x < s < y:
                    raise ValueError("wrong")
                return s

            return _c

        class T(ValidatedStr):
            validator = check("1", "3")

        self.assertEqual(T("2"), "2")
        with self.assertRaises(ValueError):
            T("3")

    def setUp(self):
        self.dct = {
            "transfer_id": 42,
            "sender": "A" * 32,
            "recipients": ["B" * 256],
            "timestamp": "2019-10-11T14:50:12+0100",
            "checksum": "A" * 64,
            "checksum_algorithm": "SHA256",
            "compression_algorithm": "gzip",
            "version": MetaData.version,
            "purpose": "PRODUCTION",
        }
        self.metadata = MetaData(
            transfer_id=42,
            sender=HexStr1024("A" * 32),
            recipients=[HexStr1024("B" * 256)],
            timestamp=datetime(
                2019, 10, 11, 14, 50, 12, 0, timezone(timedelta(0, 3600), "CET")
            ),
            checksum=HexStr256("A" * 64),
            purpose=Purpose.PRODUCTION,
        )

    def test_from_dict(self):
        self.assertEqual(MetaData.from_dict(self.dct), self.metadata)
        invalid_dicts = [
            {
                "sender": "A" * 31,
                "recipients": ["B" * 256],
                "timestamp": "2019-10-11T14:50:12+0100",
                "checksum": "A" * 64,
                "version": MetaData.version,
            },
            {
                "transfer_id": 42,
                "sender": "A" * 32,
                "recipients": ["B" * 257],
                "timestamp": "2019-10-11T14:50:12+0100",
                "checksum": "A" * 64,
                "version": MetaData.version,
            },
            {
                "transfer_id": 42,
                "sender": "A" * 32,
                "recipients": ["B" * 256],
                "timestamp": "invalid timestamp",
                "checksum": "A" * 64,
                "version": MetaData.version,
            },
            {
                "transfer_id": 42,
                "sender": "A" * 32,
                "recipients": ["B" * 256],
                "timestamp": "2019-10-11T14:50:12+0100",
                "checksum": "A" * 65,
                "version": MetaData.version,
            },
            {
                "transfer_id": 42,
                "sender": "A" * 32,
                "recipients": ["B" * 256],
                "timestamp": "2019-10-11T14:50:12+0100",
                "checksum": "A" * 65,
                "version": MetaData.version,
                "purpose": "UNKNOWN",
            },
        ]
        for n, dct in enumerate(invalid_dicts):
            with self.subTest(index=n):
                with self.assertRaises(ValueError):
                    MetaData.from_dict(dct)
        dct = {
            "invalid_key": "Demo",
            "transfer_id": 42,
            "sender": "A" * 32,
            "recipients": ["B" * 256],
            "timestamp": "2019-10-11T14:50:12+0100",
            "checksum": "A" * 64,
            "version": MetaData.version,
            "purpose": "TEST",
        }
        with self.assertWarns(UserWarning):
            MetaData.from_dict(dct)

    def test_asdict(self):
        dct = {**self.dct, "checksum": "a" * 64}
        self.assertEqual(MetaData.asdict(self.metadata), dct)
