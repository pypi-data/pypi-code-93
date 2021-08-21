# Copyright  2014-2021 Vincent Texier <vit@free.fr>
#
# DuniterPy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# DuniterPy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import re
from typing import Type, TypeVar

from ..constants import (
    BLOCK_ID_REGEX,
    G1_CURRENCY_CODENAME,
    PUBKEY_REGEX,
    SIGNATURE_REGEX,
    UID_REGEX,
)

# required to type hint cls in classmethod
from ..key import SigningKey
from .block_id import BlockID
from .document import Document, MalformedDocumentError

IdentityType = TypeVar("IdentityType", bound="Identity")

VERSION = 10


class Identity(Document):
    """
    A document describing a self certification.
    """

    re_inline = re.compile(
        "({pubkey_regex}):({signature_regex}):({block_id_regex}):([^\n]+)\n".format(
            pubkey_regex=PUBKEY_REGEX,
            signature_regex=SIGNATURE_REGEX,
            block_id_regex=BLOCK_ID_REGEX,
        )
    )
    re_type = re.compile("Type: (Identity)")
    re_issuer = re.compile(
        "Issuer: ({pubkey_regex})\n".format(pubkey_regex=PUBKEY_REGEX)
    )
    re_unique_id = re.compile("UniqueID: ({uid_regex})\n".format(uid_regex=UID_REGEX))
    re_uid = re.compile("UID:([^\n]+)\n")
    re_meta_ts = re.compile(
        "META:TS:({block_id_regex})\n".format(block_id_regex=BLOCK_ID_REGEX)
    )
    re_block_id = re.compile(
        "Timestamp: ({block_id_regex})\n".format(block_id_regex=BLOCK_ID_REGEX)
    )

    re_idty_issuer = re.compile(
        "IdtyIssuer: ({pubkey_regex})\n".format(pubkey_regex=PUBKEY_REGEX)
    )
    re_idty_unique_id = re.compile(
        "IdtyUniqueID: ({uid_regex})\n".format(uid_regex=UID_REGEX)
    )
    re_idty_block_id = re.compile(
        "IdtyTimestamp: ({block_id_regex})\n".format(block_id_regex=BLOCK_ID_REGEX)
    )
    re_idty_signature = re.compile(
        "IdtySignature: ({signature_regex})\n".format(signature_regex=SIGNATURE_REGEX)
    )

    fields_parsers = {
        **Document.fields_parsers,
        **{
            "Type": re_type,
            "UniqueID": re_unique_id,
            "Issuer": re_issuer,
            "Timestamp": re_block_id,
            "IdtyIssuer": re_idty_issuer,
            "IdtyUniqueID": re_idty_unique_id,
            "IdtyTimestamp": re_idty_block_id,
            "IdtySignature": re_idty_signature,
        },
    }

    def __init__(
        self,
        pubkey: str,
        uid: str,
        block_id: BlockID,
        signing_key: SigningKey = None,
        version: int = VERSION,
        currency: str = G1_CURRENCY_CODENAME,
    ) -> None:
        """
        Create an identity document

        :param pubkey:  Public key of the account linked to the identity
        :param uid: Unique identifier
        :param block_id: BlockID instance
        :param signing_key: SigningKey instance to sign the document (default=None)
        :param version: Document version (default=identity.VERSION)
        :param currency: Currency codename (default=constants.CURRENCY_CODENAME_G1)
        """
        super().__init__(version, currency)

        self.pubkey = pubkey
        self.block_id = block_id
        self.uid = uid

        if signing_key is not None:
            self.sign(signing_key)

    @classmethod
    def from_inline(
        cls: Type[IdentityType],
        inline: str,
        version: int = VERSION,
        currency: str = G1_CURRENCY_CODENAME,
    ) -> IdentityType:
        """
        Return Identity instance from inline Identity string

        :param inline: Inline string of the Identity
        :param version: Document version (default=certification.VERSION)
        :param currency: Currency codename (default=constants.CURRENCY_CODENAME_G1)
        :return:
        """
        selfcert_data = Identity.re_inline.match(inline)
        if selfcert_data is None:
            raise MalformedDocumentError("Inline self certification")
        pubkey = selfcert_data.group(1)
        signature = selfcert_data.group(2)
        block_id = BlockID.from_str(selfcert_data.group(3))
        uid = selfcert_data.group(4)

        identity = cls(pubkey, uid, block_id, version=version, currency=currency)

        # return identity with signature
        identity.signature = signature
        return identity

    @classmethod
    def from_signed_raw(cls: Type[IdentityType], signed_raw: str) -> IdentityType:
        """
        Return Identity instance from a signed_raw string

        :param signed_raw: Signed raw document
        :return:
        """
        n = 0
        lines = signed_raw.splitlines(True)

        version = int(Identity.parse_field("Version", lines[n]))
        n += 1

        Identity.parse_field("Type", lines[n])
        n += 1

        currency = Identity.parse_field("Currency", lines[n])
        n += 1

        pubkey = Identity.parse_field("Issuer", lines[n])
        n += 1

        uid = Identity.parse_field("UniqueID", lines[n])
        n += 1

        block_id = BlockID.from_str(Identity.parse_field("Timestamp", lines[n]))
        n += 1

        signature = Identity.parse_field("Signature", lines[n])

        identity = cls(pubkey, uid, block_id, version=version, currency=currency)

        # return identity with signature
        identity.signature = signature
        return identity

    def raw(self) -> str:
        """
        Return a raw document of the Identity

        :return:
        """
        return """Version: {version}
Type: Identity
Currency: {currency}
Issuer: {pubkey}
UniqueID: {uid}
Timestamp: {block_id}
""".format(
            version=self.version,
            currency=self.currency,
            pubkey=self.pubkey,
            uid=self.uid,
            block_id=self.block_id,
        )

    def inline(self) -> str:
        """
        Return an inline string of the Identity

        :return:
        """
        return "{pubkey}:{signature}:{block_id}:{uid}".format(
            pubkey=self.pubkey,
            signature=self.signature,
            block_id=self.block_id,
            uid=self.uid,
        )

    @classmethod
    def from_certification_raw(
        cls: Type[IdentityType], certification_raw: str
    ) -> IdentityType:
        """
        Return Identity instance from certification_raw

        :param certification_raw: Certification raw format
        :return:
        """
        lines = certification_raw.splitlines(True)
        n = 0
        version = int(Identity.parse_field("Version", lines[n]))

        n += 2
        currency = Identity.parse_field("Currency", lines[n])

        n += 2
        issuer = Identity.parse_field("IdtyIssuer", lines[n])

        n += 1
        uid = Identity.parse_field("IdtyUniqueID", lines[n])

        n += 1
        block_id = BlockID.from_str(Identity.parse_field("IdtyTimestamp", lines[n]))

        n += 1
        signature = Identity.parse_field("IdtySignature", lines[n])

        identity = cls(issuer, uid, block_id, version=version, currency=currency)
        identity.signature = signature

        return identity

    @classmethod
    def from_revocation_raw(
        cls: Type[IdentityType], revocation_raw: str
    ) -> IdentityType:
        """
        Return Identity instance from revocation_raw

        :param revocation_raw: Revocation raw format
        :return:
        """
        lines = revocation_raw.splitlines(True)
        n = 0
        version = int(Identity.parse_field("Version", lines[n]))

        n += 2
        currency = Identity.parse_field("Currency", lines[n])

        n += 1
        issuer = Identity.parse_field("Issuer", lines[n])

        n += 1
        uid = Identity.parse_field("IdtyUniqueID", lines[n])

        n += 1
        block_id = BlockID.from_str(Identity.parse_field("IdtyTimestamp", lines[n]))

        n += 1
        signature = Identity.parse_field("IdtySignature", lines[n])

        identity = cls(issuer, uid, block_id, version=version, currency=currency)
        identity.signature = signature

        return identity

    @classmethod
    def from_bma_lookup_response(
        cls: Type[IdentityType],
        currency: str,
        pubkey: str,
        lookup_response: dict,
        version: int = VERSION,
    ) -> IdentityType:
        """
        Return Identity instance from bma.lookup request response

        :param currency: Currency codename
        :param pubkey: Requested identity pubkey
        :param lookup_response: Lookup request response
        :param version: Document version (default=identity.VERSION)
        :return:
        """
        identity = None
        # parse results
        for result in lookup_response["results"]:
            if result["pubkey"] == pubkey:
                uids = result["uids"]
                uid_data = uids[0]
                # capture data
                block_id = BlockID.from_str(uid_data["meta"]["timestamp"])
                uid = uid_data["uid"]  # type: str
                signature = uid_data["self"]  # type: str

                # return self-certification document
                identity = cls(
                    pubkey=pubkey,
                    uid=uid,
                    block_id=block_id,
                    version=version,
                    currency=currency,
                )
                identity.signature = signature

        if identity is None:
            raise Exception("Identity pubkey not found")

        return identity
