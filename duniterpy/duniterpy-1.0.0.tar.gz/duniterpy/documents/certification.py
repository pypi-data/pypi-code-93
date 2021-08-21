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
from typing import Optional, Type, TypeVar, Union

from ..constants import (
    BLOCK_ID_REGEX,
    BLOCK_NUMBER_REGEX,
    G1_CURRENCY_CODENAME,
    PUBKEY_REGEX,
    SIGNATURE_REGEX,
)

# required to type hint cls in classmethod
from ..key import SigningKey
from .block_id import BlockID
from .document import Document, MalformedDocumentError
from .identity import Identity

CertificationType = TypeVar("CertificationType", bound="Certification")

VERSION = 10


class Certification(Document):
    """
    A document describing a certification.
    """

    re_inline = re.compile(
        "({certifier_regex}):({certified_regex}):({block_number_regex}):({signature_regex})\n".format(
            certifier_regex=PUBKEY_REGEX,
            certified_regex=PUBKEY_REGEX,
            block_number_regex=BLOCK_NUMBER_REGEX,
            signature_regex=SIGNATURE_REGEX,
        )
    )
    re_type = re.compile("Type: (Certification)")
    re_issuer = re.compile(
        "Issuer: ({pubkey_regex})\n".format(pubkey_regex=PUBKEY_REGEX)
    )
    re_cert_block_id = re.compile(
        "CertTimestamp: ({block_id_regex})\n".format(block_id_regex=BLOCK_ID_REGEX)
    )

    fields_parsers = {
        **Document.fields_parsers,
        **{"Type": re_type, "Issuer": re_issuer, "CertTimestamp": re_cert_block_id},
    }

    def __init__(
        self,
        pubkey_from: str,
        identity: Union[Identity, str],
        block_id: BlockID,
        signing_key: SigningKey = None,
        version: int = VERSION,
        currency: str = G1_CURRENCY_CODENAME,
    ) -> None:
        """
        Constructor

        :param pubkey_from: Pubkey of the certifier
        :param identity: Document instance of the certified identity or identity pubkey string
        :param block_id: Current BlockID instance
        :param signing_key: SigningKey instance to sign the document (default=None)
        :param version: Document version (default=certification.VERSION)
        :param currency: Currency codename (default=constants.CURRENCY_CODENAME_G1)
        """
        super().__init__(version, currency)
        self.pubkey_from = pubkey_from
        self.identity = identity if isinstance(identity, Identity) else None
        self.pubkey_to = identity.pubkey if isinstance(identity, Identity) else identity
        self.block_id = block_id

        if signing_key is not None:
            self.sign(signing_key)

    @classmethod
    def from_signed_raw(
        cls: Type[CertificationType], signed_raw: str
    ) -> CertificationType:
        """
        Return Certification instance from signed raw document

        :param signed_raw: Signed raw document
        :return:
        """
        n = 0
        lines = signed_raw.splitlines(True)

        version = int(Certification.parse_field("Version", lines[n]))
        n += 1

        Certification.parse_field("Type", lines[n])
        n += 1

        currency = Certification.parse_field("Currency", lines[n])
        n += 1

        pubkey_from = Certification.parse_field("Issuer", lines[n])
        n += 5

        block_id = BlockID.from_str(
            Certification.parse_field("CertTimestamp", lines[n])
        )
        n += 1

        signature = Certification.parse_field("Signature", lines[n])

        identity = Identity.from_certification_raw(signed_raw)

        certification = cls(
            pubkey_from, identity, block_id, version=version, currency=currency
        )

        # return certification with signature
        certification.signature = signature
        return certification

    @classmethod
    def from_inline(
        cls: Type[CertificationType],
        block_hash: Optional[str],
        inline: str,
        version: int = VERSION,
        currency: str = G1_CURRENCY_CODENAME,
    ) -> CertificationType:
        """
        Return Certification instance from inline document

        Only self.pubkey_to is populated.
        You must populate self.identity with an Identity instance to use raw/sign/signed_raw methods

        :param block_hash: Hash of the block
        :param inline: Inline document
        :param version: Document version (default=certification.VERSION)
        :param currency: Currency codename (default=constants.CURRENCY_CODENAME_G1)
        :return:
        """
        cert_data = Certification.re_inline.match(inline)
        if cert_data is None:
            raise MalformedDocumentError("Certification ({0})".format(inline))
        pubkey_from = cert_data.group(1)
        pubkey_to = cert_data.group(2)
        block_number = int(cert_data.group(3))
        if block_number == 0 or block_hash is None:
            block_id = BlockID.empty()
        else:
            block_id = BlockID(block_number, block_hash)

        signature = cert_data.group(4)
        certification = cls(
            pubkey_from, pubkey_to, block_id, version=version, currency=currency
        )

        # return certification with signature
        certification.signature = signature
        return certification

    def raw(self) -> str:
        """
        Return a raw document of the certification
        """
        if not isinstance(self.identity, Identity):
            raise MalformedDocumentError(
                "Can not return full certification document created from inline"
            )

        return """Version: {version}
Type: Certification
Currency: {currency}
Issuer: {issuer}
IdtyIssuer: {certified_pubkey}
IdtyUniqueID: {certified_uid}
IdtyTimestamp: {certified_block_id}
IdtySignature: {certified_signature}
CertTimestamp: {block_id}
""".format(
            version=self.version,
            currency=self.currency,
            issuer=self.pubkey_from,
            certified_pubkey=self.identity.pubkey,
            certified_uid=self.identity.uid,
            certified_block_id=self.identity.block_id,
            certified_signature=self.identity.signature,
            block_id=self.block_id,
        )

    def sign(self, key: SigningKey) -> None:
        """
        Sign the current document with the key for the certified Identity given

        :param key: Libnacl key instance
        """
        if not isinstance(self.identity, Identity):
            raise MalformedDocumentError(
                "Can not return full certification document created from inline"
            )
        super().sign(key)

    def signed_raw(self) -> str:
        """
        Return signed raw document of the certification for the certified Identity instance

        :return:
        """
        if not isinstance(self.identity, Identity):
            raise MalformedDocumentError(
                "Identity is not defined or properly defined. Can not create raw format"
            )
        if self.signature is None:
            raise MalformedDocumentError(
                "Signature is not defined, can not create signed raw format"
            )

        return f"{self.raw()}{self.signature}\n"

    def inline(self) -> str:
        """
        Return inline document string

        :return:
        """
        return "{0}:{1}:{2}:{3}".format(
            self.pubkey_from, self.pubkey_to, self.block_id.number, self.signature
        )
