import re
import urllib.request
import warnings
import string
from os import PathLike
from typing import (
    Iterable,
    Iterator,
    Optional,
    List,
    Tuple,
    Sequence,
    Union,
)
import gpg_lite as gpg

from .archive import archive_reader
from .dpkg import METADATA_FILE_SIG, METADATA_FILE


def fingerprint2keyid(fingerprint: str, keyid_len: int = 16) -> str:
    """Extracts a PGP Key ID from a fingerprint. By default the 'long'
    Key ID (16 chars) is returned.
    """
    if len(fingerprint) < keyid_len:
        raise RuntimeError(f"Fingerpint must be at least {keyid_len} characters long.")
    return fingerprint[-keyid_len:]


def pgp_key_as_str(key: gpg.Key, full_fingerprint: bool = True) -> str:
    """Return the PGP key in the form of a string"""
    key_user_id = key.uids[0]
    return (
        f"{key_user_id.full_name} <{key_user_id.email}> "
        f"[{key.fingerprint if full_fingerprint else key.key_id}]"
    )


def verify_metadata_signature(
    tar_file: Union[str, PathLike],
    gpg_store: gpg.GPGStore,
    signee_fingerprint: Optional[str] = None,
    key_authority_fingerprint: Optional[str] = None,
    keyserver_url: Optional[str] = None,
    validate_key_origin: bool = False,
    allow_key_download: bool = True,
    url_opener=urllib.request.urlopen,
):
    """Verify that an archive file contains a metadata file that is signed by
    a valid PGP key. Depending on the optional arguments that are passed, an
    increasing amounts of checks are done (see the argument details below).

    :param tar_file: archive file (zip/tar) containing a signature to check.
    :param gpg_store: key database as gnupg object.
    :param signee_fingerprint: if specified, the function verifies that the
        signature on the metadata file matches the specified fingerprint.
    :param key_authority_fingerprint: if specified, the function verifies that
        the metadata's signee key (i.e the key that signed the metadata file)
        is itself signed by the key of the specified key certification
        authority.
    :param keyserver_url: URL of keyserver from where the keys must originate.
    :param validate_key_origin: if True, the signee's key origin must be
        keyserver_url, otherwise the metadata signature check fails.
    :param allow_key_download: if True (the default), the metadata signee's key
        is attempted to be downloaded (if missing in local keyring) or
        refreshed (if present) from the specified keyserver (if any). If False,
        download and refresh of the signee's key is disabled, even if a
        keyserver is specified.
    :param url_opener: optional drop in for urllib.request.urlopen to allow
        proxying.
    :raise RuntimeError: if the signature does not exist or is invalid.
    """

    error_prefix = f"Metadata signature check failed for [{tar_file}]"

    with archive_reader(tar_file) as archive:
        # Retrieve signature from (detached) file.
        try:
            signature = archive.extract_member(METADATA_FILE_SIG).read()
        except (KeyError, ValueError) as e:
            raise RuntimeError(f"{error_prefix}: signature is missing") from e

        # Retrieve metadata file content - this is needed for signature
        # verification.
        try:
            metadata = archive.extract_member(METADATA_FILE).read()
        except (KeyError, ValueError) as e:
            raise RuntimeError(f"{error_prefix}: metadata is missing") from e

    # Verify signature, and retrieve the signee's fingerprint.
    try:
        fingerprint = gpg_store.verify_detached_sig(metadata, signature)
    except gpg.GPGError as e:
        raise RuntimeError(f"{error_prefix}: signature is invalid. {e}") from e

    if signee_fingerprint and signee_fingerprint != fingerprint:
        raise RuntimeError(
            f"{tar_file}: signature of metdata file '{fingerprint}' does not "
            f"match the sender fingerprint '{signee_fingerprint}' indicated "
            "in the metadata file."
        )

    # Verify that the signee's key is valid.
    try:
        next(
            retrieve_refresh_and_validate_keys(
                key_search_terms=(fingerprint,),
                gpg_store=gpg_store,
                key_authority_fingerprint=key_authority_fingerprint,
                keyserver_url=keyserver_url,
                validate_key_origin=validate_key_origin,
                allow_key_download=allow_key_download,
                url_opener=url_opener,
            )
        )
    except RuntimeError as e:
        raise RuntimeError(f"{error_prefix}: signee's key is invalid. {e}") from e


def retrieve_and_refresh_certification_authority_key(
    key_fingerprint: str,
    gpg_store: gpg.GPGStore,
    keyserver_url: Optional[str] = None,
    validate_key_origin: bool = False,
    allow_key_download=True,
    url_opener=urllib.request.urlopen,
) -> gpg.Key:
    """Retrieves and refreshes the PGP key of a key certification authority.
    For parameter description, see the retrieve_refresh_and_validate_keys()
    function documentation.
    """

    # Only full fingerprints are allowed when searching for the key
    # certification authority's key.
    if len(key_fingerprint) != 40 or any(
        x not in string.hexdigits for x in key_fingerprint
    ):
        raise RuntimeError(
            f"The provided key certification authority fingerprint "
            f"[{key_fingerprint}] is not a valid fingerprint. "
            f"It must be a 40 characters hexadecimal value."
        )

    try:
        # Retrieve and refresh the key. Validation of the key, which in this
        # case amounts to checking if it is self-signed, is done in a separate
        # step to avoid entering an infinite recursion.
        (authority_key,) = retrieve_refresh_and_validate_keys(
            key_search_terms=(key_fingerprint,),
            gpg_store=gpg_store,
            key_authority_fingerprint=None,
            keyserver_url=keyserver_url,
            validate_key_origin=False,
            allow_key_download=allow_key_download,
            url_opener=url_opener,
        )
        # Verify the key is self-signed. If asked for, also validate its origin.
        validate_pub_key(
            key=authority_key,
            gpg_store=gpg_store,
            signee_key=authority_key,
            keyserver_url=keyserver_url if validate_key_origin else None,
        )

    except RuntimeError as e:
        raise RuntimeError(
            "An error occurred while trying to load the key "
            f"certification authority's key: {str(e)}"
        ) from None

    return authority_key


def retrieve_refresh_and_validate_keys(
    key_search_terms: Iterable[str],
    gpg_store: gpg.GPGStore,
    key_authority_fingerprint: Optional[str] = None,
    keyserver_url: Optional[str] = None,
    validate_key_origin: bool = False,
    allow_key_download=True,
    url_opener=urllib.request.urlopen,
) -> Iterator[gpg.Key]:
    """Retrieve public PGP keys based on fingerprints or long key from the
    user's local keyring. If the keys are not available locally, an attempt
    to download them from a keyserver (if specified) is made.
    Exactly one key is returned for each key search term (an error is raised
    if a given search term returns multiple or no key). Keys are returned in
    the same order as the input search terms.

    Summary of performed tasks:
     - Retrieve key from local keyring, or download missing keys from the
       keyserver.
     - Refresh local copies of keys by re-downloading them from keyserver.
     - Validate keys by checking they are signed by the key authority's key.

    :param key_search_terms: fingerprint, key ID or email of the key(s) to
        retrieve.
    :param gpg_store: key database as gnupg object.
    :param key_authority_fingerprint: if specified, the function
        verifies that all retrieved keys are signed by the specified key
        authority's key.
    :param keyserver_url: URL of keyserver from where the keys must originate.
    :param validate_key_origin: if True, the retrieved key's origin must be
        keyserver_url, otherwise an error is raised.
    :param allow_key_download: if True (the default), PGP keys are attempted to
        be downloaded (if missing in local keyring) or refreshed (if present)
        from the specified keyserver (if any). If False, download and refresh of
        keys is disabled, even if a keyserver is specified.
    :param url_opener: Optional drop in for urllib.request.urlopen to allow
        proxying.
    :return: Iterator with the retrieved keys as gpg.Key objects.
    :raise RuntimeError: raised if multiple keys are found for a given key_id.
    """
    if key_authority_fingerprint:
        key_authority_key = retrieve_and_refresh_certification_authority_key(
            key_fingerprint=key_authority_fingerprint,
            gpg_store=gpg_store,
            keyserver_url=keyserver_url,
            validate_key_origin=validate_key_origin,
            allow_key_download=allow_key_download,
            url_opener=url_opener,
        )

    # Note: the reason we the search for keys is done sequentially is so that
    # they can be returned in the same order as the input search terms.
    for key_search_term in key_search_terms:
        keys = list(gpg_store.list_pub_keys(search_terms=(key_search_term,), sigs=True))

        # Refresh key if it is present in the local keyring.
        if len(keys) == 1:
            if allow_key_download and keyserver_url:
                (key,) = refresh_keys(
                    keys=keys,
                    gpg_store=gpg_store,
                    sigs=True,
                    keyserver_url=keyserver_url,
                    url_opener=url_opener,
                )
            else:
                # If key auto-download is disabled, the key is not refreshed.
                (key,) = keys

        # If no local key is found, try to download it from a keyserver.
        elif not keys:
            error_prefix = f"Key [{key_search_term}] is not available in local keyring"
            if not keyserver_url:
                raise RuntimeError(error_prefix + " and no keyserver URL is provided.")
            if not allow_key_download:
                raise RuntimeError(error_prefix + " and key download is disabled.")

            try:
                key = download_key(
                    key_search_term,
                    gpg_store,
                    keyserver_url,
                    sigs=True,
                    url_opener=url_opener,
                )
            except (gpg.KeyserverError, gpg.KeyserverKeyNotFoundError) as e:
                raise RuntimeError(str(e)) from e

        # If more than one key is matching the search term, raise an error.
        else:
            raise RuntimeError(
                f"Ambiguous input: more than one key in your local keyring "
                f"matches with {key_search_term}. This problem can be solved "
                f"by using key fingerprints as search terms."
            )

        # Verify that the key is signed by the key certification authority.
        if key_authority_fingerprint:
            validate_pub_key(
                key=key,
                gpg_store=gpg_store,
                signee_key=key_authority_key,
                keyserver_url=keyserver_url if validate_key_origin else None,
            )

        yield key


def download_key(
    search_term: str,
    gpg_store: gpg.GPGStore,
    keyserver_url: str,
    sigs: bool = True,
    url_opener=urllib.request.urlopen,
) -> gpg.Key:
    """Download a single PGP key from the specified keyserver (keyserver_url)
    and return it as a gpg-lite Key object.
    An error is raised if:
     * No key matching search_term is found on the keyserver.
     * More than one key matches search_term on the keyserver.
    """

    # Search for a key matching the search term on the keyserver.
    key_info = list(gpg.search_keyserver(search_term, keyserver_url, url_opener))
    if not key_info:
        raise RuntimeError(
            f"No key matching the search term [{search_term}] was found on "
            f"the specified keyserver [{keyserver_url}]."
        )
    if len(key_info) > 1:
        raise RuntimeError(
            "Ambiguous input: more than one key on the keyserver "
            f"[{keyserver_url}] is matching for the search term "
            f"[{search_term}]. Please try using the full key fingerprint."
        )
    key_fingerprint = key_info[0].fingerprint

    # Download the key from the keyserver to the user's local keyring.
    gpg_store.recv_keys(key_fingerprint, keyserver=keyserver_url, url_opener=url_opener)
    try:
        (key,) = gpg_store.list_pub_keys(search_terms=(key_fingerprint,), sigs=sigs)
    except ValueError:
        raise RuntimeError(
            f"Download of key [{key_fingerprint}] from [{keyserver_url}] failed."
        ) from None
    return key


def refresh_keys(
    keys: Sequence[gpg.Key],
    gpg_store: gpg.GPGStore,
    sigs: bool = True,
    keyserver_url: Optional[str] = None,
    url_opener=urllib.request.urlopen,
) -> List[gpg.Key]:
    """Refresh local copies of input keys by re-downloading them from either
    (in this order):
     - a default keyserver (keyserver_url), if specified.
     - the keyserver indicated as 'origin' in the key, if any.
    For keys that could not be refreshed, a warning is displayed.

    :param gpg_store: local GnuPG keyring.
    :param keys: PGP key(s) to refresh.
    :param sigs: if True, return keys with their signatures.
    :param keyserver_url: url of default keyserver from where to refresh keys.
    :param url_opener: optional drop in for urllib.request.urlopen to allow
        proxying.
    :return: same list of keys as passed in input, but refreshed.
    :raise RuntimeError: if after refresh fingerprints do not match.
    """
    # Loop through all keys and attempt to refresh them from (in this order):
    #  - a default keyserver, if one was provided with 'keyserver_url'.
    #  - the key's origin keyserver, if one is listed for the key.
    nonrefreshed_keys = set()
    keyservers = (keyserver_url,) if keyserver_url else ()
    for key in set(keys):
        for keyserver in keyservers + ((key.origin,) if key.origin else ()):
            try:
                gpg_store.recv_keys(
                    key.fingerprint, keyserver=keyserver, url_opener=url_opener
                )
                break
            except (gpg.KeyserverError, gpg.KeyserverKeyNotFoundError):
                pass
        else:
            nonrefreshed_keys.add(key)

    # Warn users about keys that could not be refreshed.
    if nonrefreshed_keys:
        warnings.warn(
            "The following keys could not be refreshed: "
            + ", ".join(
                [
                    f"{pgp_key_as_str(key)} [origin = {key.origin}]"
                    for key in nonrefreshed_keys
                ]
            )
        )

    # Reload all keys from local keyring. Since the key search is based on
    # fingerprint, each search should always yield exactly one hit.
    fingerprints = [key.fingerprint for key in keys]
    refreshed_keys = {
        key.fingerprint: key
        for key in gpg_store.list_pub_keys(search_terms=set(fingerprints), sigs=sigs)
    }
    if set(fingerprints) != set(refreshed_keys):
        raise RuntimeError(
            "Fingerprint mismatch after refresh. Before: "
            + ", ".join(fingerprints)
            + "\nAfter: "
            + ", ".join(refreshed_keys)
        )
    return [refreshed_keys[fpr] for fpr in fingerprints]


def validate_pub_key(
    key: gpg.Key,
    gpg_store: gpg.GPGStore,
    signee_key: Optional[gpg.Key] = None,
    keyserver_url: Optional[str] = None,
) -> None:
    """Carries out checks on the GnuPG key passed as input. Raises an error if
    one of the check fails, otherwise returns None. The following elements are
    checked:
     - verify key is not revoked.
     - if a signee_key is provided: verify the input key is signed by
       signee_key.
     - if keyserver_url is provided: verify that the input key's origin is
       the specified keyserver.

    :param key: GnuPG key to validate.
    :param signee_key: signee's key - the key whose signature must be on the
        key being validated. If missing, the check for the signee's key
        signature is skipped.
    :param keyserver_url: URL of keyserver from where the keys must originate.
    :raises RuntimeError: error is raised if one of the checks fails.
    """
    if key.validity is gpg.Validity.revoked:
        raise RuntimeError(f"{key.uids[0]} key has been revoked")
    if signee_key:
        assert_key_is_signed(key, signee_key, gpg_store, sig_class="13x")
    if keyserver_url:
        assert_keyserver_origin_valid(key=key, keyserver=keyserver_url)


def assert_key_is_signed(
    key: gpg.Key, signee_key: gpg.Key, gpg_store: gpg.GPGStore, sig_class: str = "13x"
) -> None:
    """Check that a PGP key is signed by signee_key, and that the signature's
    level of trust matches sig_class.

    :param key: key to check.
    :param signee_key: signee's key - the key whose signature must be on the
        key being verified.
    :param sig_class: class/level of confidence that the signee attributed to
        the key that has been signed. By default this value is set to '13x',
        which corresponds to the level:
          - Positive certification of a User ID and Public-Key packet. The
            issuer of this certification has done substantial verification of
            the claim of identity.
    :raises RuntimeError:
    """

    # If a valid signature of the signee's key is not found on the key to
    # verify, an error is raised.
    if not any(
        (
            # pylint: disable=fixme
            # TODO: the signature_matches_fingerprint_legacy_gpg_support()
            #       function was introduced to provide support for older GnuPG
            #       versions (see issue #17).
            #       Once support for older GnuPG versions is no longer needed,
            #       it can be removed and replaced by:
            #         sig.issuer_fingerprint == signee_key.fingerprint
            signature_matches_fingerprint_legacy_gpg_support(
                signature=sig,
                fingerprint=signee_key.fingerprint,
                gpg_store=gpg_store,
            )
            and sig.signature_class == sig_class
            for sig in key.valid_signatures
        )
    ):
        # Error case 1: a signature exists, but it was revoked.
        signee_key_str = pgp_key_as_str(signee_key, full_fingerprint=True)
        if any(
            (
                signature_matches_fingerprint_legacy_gpg_support(
                    signature=sig,
                    fingerprint=signee_key.fingerprint,
                    gpg_store=gpg_store,
                )
                and sig.signature_class == sig_class
                for sig in key.signatures
            )
        ):
            raise RuntimeError(
                f"{key.uids[0]} has an invalid or revoked signature by "
                f"{signee_key_str}. Only keys with valid signatures can be used"
            )

        # Error case 2: no signature.
        raise RuntimeError(
            f"{key.uids[0]} key is not authorized. Please get this key signed "
            f"by {signee_key_str} to allow it to be used. "
            f"If this is not your key, kindly ask its owner to get it signed."
        )


def signature_matches_fingerprint_legacy_gpg_support(
    signature: gpg.Signature, fingerprint: str, gpg_store: gpg.GPGStore
) -> bool:
    """Verify that the specified signature has the specified fingerprint.

    This function is only useful to support legacy GnuPG versions (e.g. 2.0.22)
    that are found on older operating systems (e.g. CentOS 7). This is because
    older versions of GnuPG do not show full fingerprints of signatures.

    Once the need to support these older system is dropped, this function is
    no longer needed.
    """
    if signature.issuer_fingerprint is not None:
        return signature.issuer_fingerprint == fingerprint

    signature_key_id = signature.issuer_key_id
    if signature_key_id == fingerprint[-16:]:
        # Verify there is only a single key matching the key ID in the
        # user's local keyring.
        matching_keys = gpg_store.list_pub_keys(search_terms=(signature_key_id,))
        if len(matching_keys) == 1:
            return matching_keys[0].fingerprint == fingerprint

        if len(matching_keys) == 0:
            raise RuntimeError(
                f"Cannot verify signature {signature} because no key with "
                f"key ID {signature_key_id} is present in the local keyring."
            )

        raise RuntimeError(
            f"Cannot verify signature {signature} because more than one "
            f"key with long key ID value {signature_key_id} is present "
            "in the local keyring. "
            "This error is only raised on machines that use old versions "
            "of GnuPG and can be resolved by either i) upgrading to a "
            "newer GnuPG version, or removing one of the keys with "
            "duplicated key ID."
        )

    return False


def assert_keyserver_origin_valid(key: gpg.Key, keyserver: str):
    """Verify that a key's origin keyserver matches the specified keyserver.
    If the key does not have any origin, the check is skipped.

    If both the key's origin keyserver and the specified keyserver contain
    port information in their URLs, then the port numbers are also compared
    and must match.
    Examples:
     * error   : "hagrid.hogwarts.org:11371" vs. "hagrid.hogwarts.org:11111"
     * no error: "hagrid.hogwarts.org:11371" vs. "hagrid.hogwarts.org"
    """
    if key.origin is None:
        return

    _, origin_hostname, origin_port = split_url(key.origin)
    _, keyserver_hostname, keyserver_port = split_url(keyserver)

    if origin_hostname != keyserver_hostname or (
        origin_port and keyserver_port and origin_port != keyserver_port
    ):
        raise RuntimeError(
            f"The origin of key '{key.uids[0]}' ({key.origin}) is not "
            f"the keyserver specified in the config: {keyserver}"
        )


def split_url(url: str) -> Tuple[Optional[str], str, Optional[str]]:
    """Similar to urllib.parse.urlparse, but also yields a hostname
    if there is no scheme.
    """
    match = re.fullmatch(r"(https?://|hkp://)?([^:]+)(:[0-9]+)?", url)
    if not match:
        raise RuntimeError(f"Invalid URL: {url}")
    scheme, host, port = match.groups()
    return scheme, host, port
