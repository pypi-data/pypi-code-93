import unittest
from unittest import mock
from typing import Optional
from contextlib import contextmanager

from libbiomedit import crypt
from libbiomedit.crypt import gpg


CN_UID = gpg.Uid(full_name="Chuck Norris", email="chuck.norris@roundhouse.gov")
CN_FINGERPRINT = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
CN_SIGNATURE = gpg.Signature(
    issuer_uid=CN_UID,
    issuer_key_id=CN_FINGERPRINT[-16:],
    issuer_fingerprint=CN_FINGERPRINT,
    creation_date="1550241679",
    signature_class="13x",
    validity=gpg.model.SignatureValidity.good,
)

AUTHORITY_UID = gpg.Uid(
    full_name="Unit Test Authority (validation key)", email="authority@roundhouse.gov"
)
AUTHORITY_FINGERPRINT = "ECCECCECCDECCECCECCECCDD3A6500D5C1DE39AC"
AUTHORITY_SIGNATURE = gpg.Signature(
    issuer_uid=AUTHORITY_UID,
    issuer_key_id=AUTHORITY_FINGERPRINT[-16:],
    issuer_fingerprint=AUTHORITY_FINGERPRINT,
    creation_date="1150241679",
    signature_class="13x",
    validity=gpg.model.SignatureValidity.good,
)

KEYSERVER = "http://hagrid.hogwarts.org:11371"


# PGP key of the "key certification authority", i.e. the key whose signature
# must be on other keys so that they get validated.
AUTHORITY_KEY = gpg.Key(
    key_id=AUTHORITY_FINGERPRINT[-16:],
    fingerprint=AUTHORITY_FINGERPRINT,
    validity=gpg.Validity.ultimately_valid,
    key_length=4096,
    pub_key_algorithm=1,
    creation_date="1150241679",
    uids=(AUTHORITY_UID,),
    owner_trust="u",
    key_type=gpg.KeyType.public,
    origin=KEYSERVER,
    signatures=(AUTHORITY_SIGNATURE,),
)

REVOKED_AUTHORITY_SIGNATURE = gpg.RevocationSignature(
    issuer_uid=AUTHORITY_UID,
    issuer_key_id=AUTHORITY_FINGERPRINT[-16:],
    issuer_fingerprint=AUTHORITY_FINGERPRINT,
    creation_date="1588066811",
    signature_class="30x",
    validity=gpg.model.SignatureValidity.good,
    reason="00",
    comment="revsig\\nInvalid email",
)

# Base data to generate default "user" PGP keys.
def mock_key(**kwargs):
    """Generate a mock PGP key."""

    mock_data = dict(
        key_id=CN_FINGERPRINT[-16:],
        fingerprint=CN_FINGERPRINT,
        validity=gpg.Validity.ultimately_valid,
        key_length=4096,
        pub_key_algorithm=1,
        creation_date="1550241679",
        uids=(CN_UID,),
        owner_trust="u",
        key_type=gpg.KeyType.public,
        origin=KEYSERVER,
        signatures=(CN_SIGNATURE, AUTHORITY_SIGNATURE),
        key_capabilities=frozenset(
            (
                gpg.KeyCapability.Sign(True),
                gpg.KeyCapability.Sign(False),
                gpg.KeyCapability.Certify(True),
                gpg.KeyCapability.Certify(False),
                gpg.KeyCapability.Encrypt(True),
            )
        ),
        sub_keys=(
            gpg.SubKey(
                key_type=gpg.KeyType.public,
                key_id="D892C41917B20115",
                fingerprint="55C5314BB9EFD19AE7CC4774D892C41917B20115",
                validity=gpg.Validity.ultimately_valid,
                key_length=4096,
                pub_key_algorithm=1,
                creation_date="1550241679",
                key_capabilities=frozenset((gpg.KeyCapability.Encrypt(False),)),
            ),
        ),
    )

    return gpg.Key(**{**mock_data, **kwargs})


def mock_key_info(**kwargs):
    mock_data = dict(
        uid=CN_UID,
        fingerprint=CN_FINGERPRINT,
        key_algorithm=1,
        key_length=4096,
        creation_date="1550241679",
        expiration_date=None,
    )
    return gpg.KeyInfo(**{**mock_data, **kwargs})


def mock_signature(**kwargs):
    mock_data = dict(
        issuer_uid=AUTHORITY_UID,
        issuer_key_id=AUTHORITY_FINGERPRINT[-16:],
        issuer_fingerprint=AUTHORITY_FINGERPRINT,
        creation_date="1150241679",
        signature_class="13x",
        validity=gpg.model.SignatureValidity.good,
    )

    return gpg.Signature(**{**mock_data, **kwargs})


class MockGPGStore:
    def __init__(self, keys, keyserver_keys):
        self.keys = keys
        self.keyserver_keys = keyserver_keys

    def list_pub_keys(self, search_terms, sigs=True):
        _ = sigs
        return [
            key
            for key in self.keys
            if any(key.fingerprint.endswith(x) for x in search_terms)
        ]

    def recv_keys(self, *fingerprints, keyserver=None, url_opener=None):
        _ = keyserver
        _ = url_opener
        received_keys = [
            key
            for key in self.keyserver_keys
            if any(key.fingerprint.endswith(x) for x in fingerprints)
        ]
        self.keys.extend(key for key in received_keys if key not in self.keys)


class MockBrokenGPGStore(MockGPGStore):
    """A broken GPGStore that is unable to download keys"""

    def recv_keys(self, *fingerprints, keyserver=None, url_opener=None):
        _ = fingerprints
        _ = keyserver
        _ = url_opener


def mock_search_keyserver(search_term, keyserver, url_opener):
    _ = keyserver
    _ = url_opener
    if search_term == AUTHORITY_FINGERPRINT:
        yield mock_key_info(fingerprint=AUTHORITY_FINGERPRINT)
    if search_term.endswith("C"):
        # Special case to simulate key not on keyserver.
        return None
    if search_term.endswith("D"):
        # Special case to simulate having multiple matches on keyserver.
        yield from [
            mock_key_info(fingerprint="D" * 40),
            mock_key_info(fingerprint="AD" * 20),
        ]
    else:
        if len(search_term) == 40:
            yield mock_key_info(fingerprint=search_term)
        else:
            for key_UID, fingerprint in (
                (AUTHORITY_UID, AUTHORITY_FINGERPRINT),
                (CN_UID, CN_FINGERPRINT),
            ):
                if search_term in (key_UID.email, key_UID.full_name):
                    yield mock_key_info(fingerprint=fingerprint)

    return None


class TestCrypt(unittest.TestCase):
    def setUp(self):
        self.key1 = mock_key(signatures=(AUTHORITY_SIGNATURE,))

    def test_pgp_key_as_str(self):
        # Verify that the rendering of a key as string works as expected.
        for full_fingerprint in (True, False):
            self.assertEqual(
                crypt.pgp_key_as_str(self.key1, full_fingerprint=full_fingerprint),
                f"{CN_UID.full_name} <{CN_UID.email}> "
                f"[{CN_FINGERPRINT if full_fingerprint else CN_FINGERPRINT[-16:]}]",
            )

    def test_assert_keyserver_origin_valid(self):
        # Verify that keys originating from the correct keyserver raise no
        # errors.
        keys = (self.key1, mock_key(origin="hagrid.hogwarts.org"))
        for key in keys:
            for keyserver in (
                KEYSERVER,
                "http://hagrid.hogwarts.org",
                "hagrid.hogwarts.org:11371",
                "hagrid.hogwarts.org",
                "hkp://hagrid.hogwarts.org:11371",
            ):
                with self.subTest(key=keys.index(key), keyserver=keyserver):
                    crypt.assert_keyserver_origin_valid(key=key, keyserver=keyserver)

        # Verify that keys originating from an incorrect keyserver raise an
        # error.
        for keyserver in (
            "snape.hogwarts.org",
            "hagrid.hogwarts.org:11111",
        ):
            with self.assertRaises(RuntimeError):
                crypt.assert_keyserver_origin_valid(self.key1, keyserver)

        bad_key = mock_key(origin="snape.hogwarts.org")
        with self.assertRaises(RuntimeError):
            crypt.assert_keyserver_origin_valid(bad_key, KEYSERVER)

    def test_assert_key_is_signed(self):
        # Check that a correctly signed key does not raise any error.
        mock_gpg_store = mock.Mock()
        crypt.assert_key_is_signed(
            key=self.key1, signee_key=AUTHORITY_KEY, gpg_store=mock_gpg_store
        )

        # Check that when a key is not signed by signee_key, an error is raised.
        # Note: self.key1 is not self-signed, so this must raise an error.
        with self.assertRaises(RuntimeError):
            crypt.assert_key_is_signed(
                key=self.key1, signee_key=self.key1, gpg_store=mock_gpg_store
            )

        # Check that a key with a fake signature (it has the same key ID as the
        # real key authority) raises an error.
        for fake_signature in (
            mock_signature(issuer_fingerprint="FA4E" + AUTHORITY_FINGERPRINT[4:]),
            mock_signature(signature_class="12x"),
            mock_signature(validity=gpg.model.SignatureValidity.bad),
            mock_signature(validity=gpg.model.SignatureValidity.no_public_key),
        ):
            fake_signature_key = mock_key(signatures=(CN_SIGNATURE, fake_signature))
            with self.assertRaises(RuntimeError):
                crypt.assert_key_is_signed(
                    fake_signature_key,
                    signee_key=AUTHORITY_KEY,
                    gpg_store=mock_gpg_store,
                )

        # Check that adding a revoked signee signature on the key raises an
        # error.
        revoked_key = mock_key(
            signatures=self.key1.signatures + (REVOKED_AUTHORITY_SIGNATURE,)
        )
        with self.assertRaises(RuntimeError):
            crypt.assert_key_is_signed(
                revoked_key, signee_key=AUTHORITY_KEY, gpg_store=mock_gpg_store
            )

        # Check legacy GnuPG support:
        # Old GnuPG versions do not retrieve the issuer_fingerprint of
        # signatures.
        legacy_signature = gpg.Signature(
            issuer_uid=AUTHORITY_UID,
            issuer_key_id=AUTHORITY_FINGERPRINT[-16:],
            issuer_fingerprint=None,
            creation_date="1150241679",
            signature_class="13x",
            validity=gpg.model.SignatureValidity.good,
        )
        legacy_key = mock_key(signatures=(CN_SIGNATURE, legacy_signature))
        crypt.assert_key_is_signed(
            legacy_key,
            signee_key=AUTHORITY_KEY,
            gpg_store=MockGPGStore(keys=[AUTHORITY_KEY], keyserver_keys=[]),
        )
        # If the key is missing locally, an error should be raised.
        with self.assertRaises(RuntimeError):
            crypt.assert_key_is_signed(
                legacy_key,
                signee_key=AUTHORITY_KEY,
                gpg_store=MockGPGStore(keys=[], keyserver_keys=[]),
            )
        # If another key with the same key ID is present in the local keyring,
        # an error should be raised.
        fake_authority_key = mock_key(
            fingerprint="A" * 16 + AUTHORITY_FINGERPRINT[-16:]
        )
        with self.assertRaises(RuntimeError):
            crypt.assert_key_is_signed(
                legacy_key,
                signee_key=AUTHORITY_KEY,
                gpg_store=MockGPGStore(
                    keys=[AUTHORITY_KEY, fake_authority_key], keyserver_keys=[]
                ),
            )

    def test_validate_pub_key(self):
        # Check that valid keys do not raise any errors.
        mock_gpg_store = mock.Mock()
        crypt.validate_pub_key(self.key1, gpg_store=mock_gpg_store)
        crypt.validate_pub_key(
            self.key1, keyserver_url=KEYSERVER, gpg_store=mock_gpg_store
        )
        crypt.validate_pub_key(
            self.key1,
            signee_key=AUTHORITY_KEY,
            keyserver_url=KEYSERVER,
            gpg_store=mock_gpg_store,
        )

        # Check that invalid keys raise an error.
        with self.assertRaises(RuntimeError):
            revoked_key = mock_key(validity=gpg.Validity.revoked)
            crypt.validate_pub_key(revoked_key, gpg_store=mock_gpg_store)
        with self.assertRaises(RuntimeError):
            # This is expected to fail because key1 is not self signed.
            crypt.validate_pub_key(
                self.key1, signee_key=self.key1, gpg_store=mock_gpg_store
            )
        with self.assertRaises(RuntimeError):
            bad_key = mock_key(origin="snape.hogwarts.org")
            crypt.validate_pub_key(
                bad_key, keyserver_url=KEYSERVER, gpg_store=mock_gpg_store
            )

    def test_split_url(self):
        protocol = "http://"
        address = "hagrid.hogwarts.org"
        port = ":11371"
        self.assertEqual(crypt.split_url(KEYSERVER), (protocol, address, port))
        self.assertEqual(crypt.split_url(address + port), (None, address, port))
        self.assertEqual(crypt.split_url(protocol + address), (protocol, address, None))
        self.assertEqual(crypt.split_url(address), (None, address, None))
        with self.assertRaises(RuntimeError):
            crypt.split_url("keyserver.hogwar:ts.org")

    def test_verify_metadata_signature(self):
        class MockArchiveReader:
            def __init__(self, *, metadata=None, signature=None):
                self.contents = {}
                if metadata:
                    self.contents[crypt.METADATA_FILE] = metadata
                if signature:
                    self.contents[crypt.METADATA_FILE_SIG] = signature
                self.signature = signature
                self.metadata = metadata
                self.should_pass = metadata is not None and signature == b"valid"

            def extract_member(self, f: str):
                _ = self.contents[f]
                mock_f = mock.Mock()
                mock_f.read = mock.Mock(return_value=self.signature)
                return mock_f

            def __repr__(self):
                return f"MockArchiveReader({self.metadata}, {self.signature})"

        signee_fingerprint = CN_FINGERPRINT

        def mock_gpg_verify_detached_sig(_metadata, sig):
            if sig != b"valid":
                raise gpg.GPGError("Invalid")
            return signee_fingerprint

        for mock_archive in (
            MockArchiveReader(),
            MockArchiveReader(metadata=...),
            MockArchiveReader(signature=b"valid"),
            MockArchiveReader(signature=b"invalid"),
            MockArchiveReader(metadata=..., signature=b"valid"),
            MockArchiveReader(metadata=..., signature=b"invalid"),
        ):
            with self.subTest(tar=repr(mock_archive)):
                mock_archive_open_obj = mock.Mock(return_value=mock_archive)

                @contextmanager
                def mock_archive_reader_init(f):
                    yield mock_archive_open_obj(f)  # pylint: disable=cell-var-from-loop

                mock_gpg_store = mock.Mock()
                mock_gpg_store.verify_detached_sig = mock_gpg_verify_detached_sig
                mock_validate_keys_iter = mock.MagicMock()
                mock_validate_keys = mock.Mock(return_value=mock_validate_keys_iter)
                with mock.patch(
                    "libbiomedit.crypt.archive_reader", mock_archive_reader_init
                ), mock.patch(
                    "libbiomedit.crypt.retrieve_refresh_and_validate_keys",
                    mock_validate_keys,
                ):
                    with assert_conditional_raise(
                        self,
                        None
                        if mock_archive.should_pass
                        else (RuntimeError, gpg.GPGError),
                    ):
                        crypt.verify_metadata_signature(
                            tar_file="/faketar.tar",
                            gpg_store=mock_gpg_store,
                            signee_fingerprint=signee_fingerprint,
                            key_authority_fingerprint=AUTHORITY_FINGERPRINT,
                            keyserver_url="http://snape.hogwarts.org:11371",
                            validate_key_origin=True,
                            allow_key_download=False,
                        )

                mock_archive_open_obj.assert_called_once_with("/faketar.tar")
                if mock_archive.should_pass:
                    mock_validate_keys.assert_called_once_with(
                        key_search_terms=(signee_fingerprint,),
                        gpg_store=mock_gpg_store,
                        key_authority_fingerprint=AUTHORITY_FINGERPRINT,
                        keyserver_url="http://snape.hogwarts.org:11371",
                        validate_key_origin=True,
                        allow_key_download=False,
                        url_opener=crypt.urllib.request.urlopen,
                    )
                    mock_validate_keys_iter.__next__.assert_called_once()

        # Verify that a missmatch in fingerprint between metadata signee and
        # sender value indicated in the metadata raises an error.
        mock_gpg_store = mock.Mock()
        mock_gpg_store.verify_detached_sig = lambda x, y: AUTHORITY_FINGERPRINT
        mock_validate_keys_iter = mock.MagicMock()
        mock_validate_keys = mock.Mock(return_value=mock_validate_keys_iter)
        mock_archive_open_obj = mock.Mock(
            return_value=MockArchiveReader(metadata=..., signature=b"valid")
        )

        @contextmanager
        def mock_archive_reader_init_2(f):
            yield mock_archive_open_obj(f)  # pylint: disable=cell-var-from-loop

        with self.assertRaises(RuntimeError) as error, mock.patch(
            "libbiomedit.crypt.archive_reader", mock_archive_reader_init_2
        ), mock.patch(
            "libbiomedit.crypt.retrieve_refresh_and_validate_keys",
            mock_validate_keys,
        ):
            crypt.verify_metadata_signature(
                tar_file="/faketar.tar",
                gpg_store=mock_gpg_store,
                signee_fingerprint=CN_FINGERPRINT,
                key_authority_fingerprint=AUTHORITY_FINGERPRINT,
                keyserver_url="http://snape.hogwarts.org:11371",
                validate_key_origin=True,
                allow_key_download=False,
            )
        self.assertIn("does not match the sender fingerprint", str(error.exception))

    def test_download_key(self):

        # Check that when a search term matches exactly 1 key, the key gets
        # downloaded as expected.
        with mock.patch("gpg_lite.search_keyserver", mock_search_keyserver):
            for expected_key, search_term in (
                (self.key1, CN_FINGERPRINT),
                (self.key1, "Chuck Norris"),
                (self.key1, "chuck.norris@roundhouse.gov"),
                (AUTHORITY_KEY, AUTHORITY_FINGERPRINT),
                (AUTHORITY_KEY, "authority@roundhouse.gov"),
            ):
                downloaded_key = crypt.download_key(
                    search_term=search_term,
                    gpg_store=MockGPGStore(
                        keys=[], keyserver_keys=[AUTHORITY_KEY, self.key1]
                    ),
                    keyserver_url=KEYSERVER,
                )
                self.assertEqual(downloaded_key, expected_key)

        # Check that when no key is found on the keyserver, an error is raised.
        with mock.patch("gpg_lite.search_keyserver", mock_search_keyserver):
            for search_term in ("", "anonymous@roundhouse.gov"):
                with self.assertRaises(RuntimeError):
                    downloaded_key = crypt.download_key(
                        search_term="anonymous@roundhouse.gov",
                        gpg_store=MockGPGStore(keys=[], keyserver_keys=[self.key1]),
                        keyserver_url=KEYSERVER,
                    )

        # Check that when a search term matches multiple keys, an error is
        # raised. Note: passing a search term ending in "D" triggers multiple
        # matches on the mock keyserver.
        with mock.patch("gpg_lite.search_keyserver", mock_search_keyserver):
            with self.assertRaises(RuntimeError):
                downloaded_key = crypt.download_key(
                    search_term="D" * 40,
                    gpg_store=MockGPGStore(keys=[], keyserver_keys=[]),
                    keyserver_url=KEYSERVER,
                )

        # Check that when a key fails to download from the keyserver, an
        # error is raised.
        with mock.patch("gpg_lite.search_keyserver", mock_search_keyserver):
            with self.assertRaises(RuntimeError):
                downloaded_key = crypt.download_key(
                    search_term=CN_FINGERPRINT,
                    gpg_store=MockBrokenGPGStore(keys=[], keyserver_keys=[self.key1]),
                    keyserver_url=KEYSERVER,
                )

    def test_retrieve_and_refresh_certification_authority_key(self):

        # Check that a correct key authority key can be retrieved as expected.
        crypt.retrieve_and_refresh_certification_authority_key(
            key_fingerprint=AUTHORITY_FINGERPRINT,
            gpg_store=MockGPGStore(keys=[AUTHORITY_KEY], keyserver_keys=[]),
        )
        with mock.patch("gpg_lite.search_keyserver", mock_search_keyserver):
            crypt.retrieve_and_refresh_certification_authority_key(
                key_fingerprint=AUTHORITY_FINGERPRINT,
                gpg_store=MockGPGStore(keys=[], keyserver_keys=[AUTHORITY_KEY]),
                keyserver_url=KEYSERVER,
            )

        # Check that an error is raised if the input fingerprint is not a
        # proper fingerprint.
        for key_fingerprint in (
            AUTHORITY_FINGERPRINT[-16:],
            AUTHORITY_FINGERPRINT[-1] + "z",
        ):
            with self.assertRaises(RuntimeError):
                crypt.retrieve_and_refresh_certification_authority_key(
                    key_fingerprint=key_fingerprint,
                    gpg_store=MockGPGStore(keys=[AUTHORITY_KEY], keyserver_keys=[]),
                )

        # Check an error is raised if the key is missing from keyring and
        # keyserver.
        with self.assertRaises(RuntimeError):
            crypt.retrieve_and_refresh_certification_authority_key(
                key_fingerprint=AUTHORITY_FINGERPRINT,
                gpg_store=MockGPGStore(keys=[], keyserver_keys=[]),
            )

        # Check that an error is raised if the authority key is missing locally
        # and the download of keys is disabled.
        with self.assertRaises(RuntimeError), mock.patch(
            "gpg_lite.search_keyserver", mock_search_keyserver
        ):
            crypt.retrieve_and_refresh_certification_authority_key(
                key_fingerprint=AUTHORITY_FINGERPRINT,
                gpg_store=MockGPGStore(keys=[], keyserver_keys=[AUTHORITY_KEY]),
                keyserver_url=KEYSERVER,
                allow_key_download=False,
            )

    def test_retrieve_refresh_and_validate_keys(self):
        key_A = self.key1
        key_B = mock_key(key_id="B" * 16, fingerprint="B" * 40)
        key_C = mock_key(key_id="C" * 16, fingerprint="C" * 40)
        key_D = mock_key(
            key_id="D" * 16,
            fingerprint="D" * 40,
            signatures=(REVOKED_AUTHORITY_SIGNATURE,),
        )

        # Check that keys are returned in the same order as input search terms.
        keys = [key_A, key_B, key_C, key_D]
        search_terms = [key.fingerprint for key in keys]
        refreshed_keys = crypt.retrieve_refresh_and_validate_keys(
            key_search_terms=search_terms,
            gpg_store=MockGPGStore(keys=keys, keyserver_keys=[]),
        )
        self.assertEqual(search_terms, [key.fingerprint for key in refreshed_keys])

        # Check that if a key is missing from the GPGStore, an error is raised.
        with self.assertRaises(RuntimeError):
            list(
                crypt.retrieve_refresh_and_validate_keys(
                    key_search_terms=search_terms,
                    gpg_store=MockGPGStore(keys=keys[0:3], keyserver_keys=[]),
                )
            )

        # Check that if multiple keys with the same key ID or fingerprint exist
        # in the GPGStore, an error is raised.
        with self.assertRaises(RuntimeError):
            list(
                crypt.retrieve_refresh_and_validate_keys(
                    key_search_terms=search_terms,
                    gpg_store=MockGPGStore(keys=keys * 2, keyserver_keys=[]),
                )
            )

        # Check that if a key is missing, it gets downloaded from the keyserver.
        keys = [key_A, key_B]
        search_terms = [key.fingerprint for key in keys]
        with mock.patch("gpg_lite.search_keyserver", mock_search_keyserver):
            refreshed_keys = crypt.retrieve_refresh_and_validate_keys(
                key_search_terms=search_terms,
                gpg_store=MockGPGStore(keys=[key_A], keyserver_keys=keys),
                keyserver_url=KEYSERVER,
            )
            self.assertEqual(search_terms, [key.fingerprint for key in refreshed_keys])

        # Check that if a key is missing from both the local keyring and the
        # keyserver, an error is raised.
        keys = [key_A, key_B, key_C]
        with mock.patch("gpg_lite.search_keyserver", mock_search_keyserver):
            with self.assertRaises(RuntimeError):
                list(
                    crypt.retrieve_refresh_and_validate_keys(
                        key_search_terms=[key.fingerprint for key in keys],
                        gpg_store=MockGPGStore(keys=[key_A], keyserver_keys=keys[:-1]),
                        keyserver_url=KEYSERVER,
                    )
                )

        # Check that if key download is disabled, keys are not downloaded and
        # therefore a missing local key raises an error, even if present on the
        # keyserver.
        keys = [key_A, key_B]
        with mock.patch("gpg_lite.search_keyserver", mock_search_keyserver):
            with self.assertRaises(RuntimeError):
                list(
                    crypt.retrieve_refresh_and_validate_keys(
                        key_search_terms=[key.fingerprint for key in keys],
                        gpg_store=MockGPGStore(keys=[key_A], keyserver_keys=[key_B]),
                        keyserver_url=KEYSERVER,
                        allow_key_download=False,
                    )
                )

        # Check that if a search terms has more than 1 match on the keyserver,
        # an error is raised.
        keys = [key_A, key_B, key_D]
        with mock.patch("gpg_lite.search_keyserver", mock_search_keyserver):
            with self.assertRaises(RuntimeError):
                list(
                    crypt.retrieve_refresh_and_validate_keys(
                        key_search_terms=[key.fingerprint for key in keys],
                        gpg_store=MockGPGStore(keys=[key_A], keyserver_keys=keys[:-1]),
                        keyserver_url=KEYSERVER,
                    )
                )

        # Check that if a key authority fingerprint is passed, the keys that
        # are searched for are validated against it.
        keys = [key_A, key_B, key_C]
        search_terms = [key.fingerprint for key in keys]
        with mock.patch("gpg_lite.search_keyserver", mock_search_keyserver):
            refreshed_keys = crypt.retrieve_refresh_and_validate_keys(
                key_search_terms=search_terms,
                gpg_store=MockGPGStore(
                    keys=[key_A, key_C, AUTHORITY_KEY], keyserver_keys=keys
                ),
                keyserver_url=KEYSERVER,
                key_authority_fingerprint=AUTHORITY_FINGERPRINT,
            )
            self.assertEqual(search_terms, [key.fingerprint for key in refreshed_keys])

        # Check that if a key is invalid (Key_D), then an error is raised.
        keys = [key_A, key_B, key_D]
        with mock.patch("gpg_lite.search_keyserver", mock_search_keyserver):
            with self.assertRaises(RuntimeError):
                list(
                    crypt.retrieve_refresh_and_validate_keys(
                        key_search_terms=[key.fingerprint for key in keys],
                        gpg_store=MockGPGStore(
                            keys=[key_A, key_D, AUTHORITY_KEY], keyserver_keys=keys
                        ),
                        keyserver_url=KEYSERVER,
                        key_authority_fingerprint=AUTHORITY_FINGERPRINT,
                    )
                )

        # Check that if a key is present in the local keyring, it is gets
        # refreshed from the keyserver.
        keys = [key_A]
        search_terms = [key.fingerprint for key in keys]
        mock_gpg_store = MockGPGStore(keys=keys, keyserver_keys=[])
        mock_refresh_keys = mock.Mock(return_value=[key_A])
        with mock.patch("libbiomedit.crypt.refresh_keys", mock_refresh_keys):
            list(
                crypt.retrieve_refresh_and_validate_keys(
                    key_search_terms=search_terms,
                    gpg_store=mock_gpg_store,
                    keyserver_url=KEYSERVER,
                    allow_key_download=True,
                )
            )
            mock_refresh_keys.assert_called_once_with(
                keys=[key_A],
                gpg_store=mock_gpg_store,
                sigs=True,
                keyserver_url=KEYSERVER,
                url_opener=crypt.urllib.request.urlopen,
            )

        # Check that if key download is disabled, keys are not refreshed.
        mock_refresh_keys = mock.Mock(return_value=[key_A])
        with mock.patch("libbiomedit.crypt.refresh_keys", mock_refresh_keys):
            list(
                crypt.retrieve_refresh_and_validate_keys(
                    key_search_terms=search_terms,
                    gpg_store=mock_gpg_store,
                    keyserver_url=KEYSERVER,
                    allow_key_download=False,
                )
            )
            mock_refresh_keys.assert_not_called()

    def test_refresh_keys(self):
        keyerver_url = "http://snape.hogwarts.org:11371"
        keys = (
            self.key1,
            mock_key(fingerprint="B" * 40, origin=keyerver_url),
            mock_key(fingerprint="C" * 40, origin=keyerver_url),
            mock_key(fingerprint="D" * 40, origin=None),
        )

        def new_gpg_store(refreshed_keys):
            """Return a mock GPGStore object that contains the specified keys"""
            gpg_store = mock.Mock()
            gpg_store.recv_keys = mock.Mock()
            gpg_store.send_keys = mock.Mock()
            gpg_store.list_pub_keys = mock.Mock(return_value=refreshed_keys)
            return gpg_store

        # Check that when no keyserver is specified, only keys with an
        # origin are attempted to be refreshed.
        gpg_store = new_gpg_store(keys)
        urlopen = crypt.urllib.request.urlopen
        with self.assertWarns(UserWarning):
            new_keys = crypt.refresh_keys(
                keys, gpg_store, sigs=True, keyserver_url=None, url_opener=urlopen
            )
        # keys must be the same before and after the refresh.
        self.assertEqual(keys, tuple(new_keys))
        # key "D" should not be attempted to be refreshed because it does not
        # have an origin.
        gpg_store.recv_keys.assert_has_calls(
            (
                mock.call("A" * 40, keyserver=KEYSERVER, url_opener=urlopen),
                mock.call("B" * 40, keyserver=keyerver_url, url_opener=urlopen),
                mock.call("C" * 40, keyserver=keyerver_url, url_opener=urlopen),
            ),
            any_order=True,
        )
        # All keys must have been reloaded from the GPGstore. Note that we
        # use "keys=set(...)" to ensure that the order of the fingerprints
        # is the same as in the call to "list_pub_keys()", which varies
        # randomly from one python run to the other.
        gpg_store.list_pub_keys.assert_called_once_with(
            search_terms=set(40 * c for c in ("A", "B", "C", "D")), sigs=True
        )

        # Check that when a keyserver is specified, all keys are attempted
        # to be refreshed.
        new_keys = crypt.refresh_keys(
            keys, gpg_store, sigs=..., keyserver_url=KEYSERVER, url_opener=urlopen
        )
        # All keys must be attempted to be refreshed on the default keyserver.
        gpg_store.recv_keys.assert_has_calls(
            (
                mock.call("A" * 40, keyserver=KEYSERVER, url_opener=urlopen),
                mock.call("B" * 40, keyserver=KEYSERVER, url_opener=urlopen),
                mock.call("C" * 40, keyserver=KEYSERVER, url_opener=urlopen),
                mock.call("D" * 40, keyserver=KEYSERVER, url_opener=urlopen),
            ),
            any_order=True,
        )
        self.assertEqual(keys, tuple(new_keys))

        # Check that non-refreshed keys raise a warning.
        with self.assertWarns(UserWarning):
            crypt.refresh_keys(keys, gpg_store, sigs=...)

        # Check that duplicated keys are not refreshed multiple times.
        # Here we duplicate the 4 input keys 3 times, but still expect the
        # refresh keys function to be called only 4 times and not 4*3 times.
        gpg_store.recv_keys.reset_mock()
        new_keys = crypt.refresh_keys(
            keys * 3,
            gpg_store,
            sigs=...,
            keyserver_url=KEYSERVER,
            url_opener=urlopen,
        )
        self.assertEqual(gpg_store.recv_keys.call_count, len(keys))

        # Check that duplicated keys are returned duplicated:
        keys_dups = keys * 3
        gpg_store = new_gpg_store(keys)
        with self.assertWarns(UserWarning):
            new_keys = crypt.refresh_keys(keys_dups, gpg_store, sigs=...)
            self.assertEqual(keys_dups, tuple(new_keys))

        # Check that a missmatch between the number of keys in input and
        # the number of keys retrieved from the local keyring after the
        # refresh triggers an error.
        gpg_store = new_gpg_store(keys[1:])
        with self.assertRaises(RuntimeError), self.assertWarns(UserWarning):
            crypt.refresh_keys(keys, gpg_store, sigs=...)
        # Same as above, but this time the missmatch in only in one of the
        # fingerprints. The number of keys in input/output stays the same.
        gpg_store = new_gpg_store((mock_key(fingerprint="0" + 39 * "A"),) + keys[1:])
        with self.assertRaises(RuntimeError), self.assertWarns(UserWarning):
            crypt.refresh_keys(keys, gpg_store, sigs=...)

    def test_fingerprint2keyid(self):
        self.assertEqual(
            crypt.fingerprint2keyid(self.key1.fingerprint), self.key1.key_id
        )
        with self.assertRaises(RuntimeError):
            crypt.fingerprint2keyid("AAA")


@contextmanager
def assert_conditional_raise(test: unittest.TestCase, error_type: Optional[Exception]):
    if error_type:
        with test.assertRaises(error_type):  # type: ignore
            yield None
    else:
        yield None
