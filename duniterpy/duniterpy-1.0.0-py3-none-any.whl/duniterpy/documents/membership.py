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
)

# required to type hint cls in classmethod
from ..key import SigningKey
from .block_id import BlockID
from .document import Document, MalformedDocumentError

MembershipType = TypeVar("MembershipType", bound="Membership")

VERSION = 10


class Membership(Document):
    """
    .. note:: A membership document is specified by the following format :

        | Version: VERSION
        | Type: Membership
        | Currency: CURRENCY_NAME
        | Issuer: ISSUER
        | Block: NUMBER-HASH
        | Membership: MEMBERSHIP_TYPE
        | UserID: USER_ID
        | CertTS: CERTIFICATION_TS

    """

    # PUBLIC_KEY:SIGNATURE:NUMBER:HASH:TIMESTAMP:USER_ID
    re_inline = re.compile(
        "({pubkey_regex}):({signature_regex}):({ms_block_id_regex}):({identity_block_id_regex}):([^\n]+)\n".format(
            pubkey_regex=PUBKEY_REGEX,
            signature_regex=SIGNATURE_REGEX,
            ms_block_id_regex=BLOCK_ID_REGEX,
            identity_block_id_regex=BLOCK_ID_REGEX,
        )
    )
    re_type = re.compile("Type: (Membership)")
    re_issuer = re.compile(
        "Issuer: ({pubkey_regex})\n".format(pubkey_regex=PUBKEY_REGEX)
    )
    re_block = re.compile(
        "Block: ({block_id_regex})\n".format(block_id_regex=BLOCK_ID_REGEX)
    )
    re_membership_type = re.compile("Membership: (IN|OUT)")
    re_userid = re.compile("UserID: ([^\n]+)\n")
    re_certts = re.compile(
        "CertTS: ({block_id_regex})\n".format(block_id_regex=BLOCK_ID_REGEX)
    )

    fields_parsers = {
        **Document.fields_parsers,
        **{
            "Type": re_type,
            "Issuer": re_issuer,
            "Block": re_block,
            "Membership": re_membership_type,
            "UserID": re_userid,
            "CertTS": re_certts,
        },
    }

    def __init__(
        self,
        issuer: str,
        membership_block_id: BlockID,
        uid: str,
        identity_block_id: BlockID,
        signing_key: SigningKey = None,
        version: int = VERSION,
        currency: str = G1_CURRENCY_CODENAME,
        membership_type: str = "IN",
    ) -> None:
        """
        Create a membership document

        :param issuer: Public key of the issuer
        :param membership_block_id: BlockID of this membership
        :param uid: Unique identifier of the identity
        :param identity_block_id:  BlockID of the identity
        :param signing_key: SigningKey instance to sign the document (default=None)
        :param version: Document version (default=membership.VERSION)
        :param currency: Currency codename (default=constants.CURRENCY_CODENAME_G1)
        :param membership_type: "IN" or "OUT" to enter or quit the community. Default "IN"
        """
        super().__init__(version, currency)

        self.issuer = issuer
        self.membership_block_id = membership_block_id
        self.membership_type = membership_type
        self.uid = uid
        self.identity_block_id = identity_block_id

        if signing_key is not None:
            self.sign(signing_key)

    @classmethod
    def from_inline(
        cls: Type[MembershipType],
        inline: str,
        version: int = VERSION,
        currency: str = G1_CURRENCY_CODENAME,
        membership_type: str = "IN",
    ) -> MembershipType:
        """
        Return Membership instance from inline format

        :param inline: Inline string format
        :param version: Document version (default=membership.VERSION)
        :param currency: Currency codename (default=constants.CURRENCY_CODENAME_G1)
        :param membership_type: "IN" or "OUT" to enter or exit membership. Default "IN"
        :return:
        """
        data = Membership.re_inline.match(inline)
        if data is None:
            raise MalformedDocumentError("Inline membership ({0})".format(inline))
        issuer = data.group(1)
        signature = data.group(2)
        membership_block_id = BlockID.from_str(data.group(3))
        identity_block_id = BlockID.from_str(data.group(4))
        uid = data.group(5)
        membership = cls(
            issuer,
            membership_block_id,
            uid,
            identity_block_id,
            version=version,
            currency=currency,
            membership_type=membership_type,
        )

        # return membership with signature
        membership.signature = signature
        return membership

    @classmethod
    def from_signed_raw(cls: Type[MembershipType], signed_raw: str) -> MembershipType:
        """
        Return Membership instance from signed raw format

        :param signed_raw: Signed raw format string
        :return:
        """
        lines = signed_raw.splitlines(True)
        n = 0

        version = int(Membership.parse_field("Version", lines[n]))
        n += 1

        Membership.parse_field("Type", lines[n])
        n += 1

        currency = Membership.parse_field("Currency", lines[n])
        n += 1

        issuer = Membership.parse_field("Issuer", lines[n])
        n += 1

        membership_block_id = BlockID.from_str(
            Membership.parse_field("Block", lines[n])
        )
        n += 1

        membership_type = Membership.parse_field("Membership", lines[n])
        n += 1

        uid = Membership.parse_field("UserID", lines[n])
        n += 1

        identity_block_id = BlockID.from_str(Membership.parse_field("CertTS", lines[n]))
        n += 1

        signature = Membership.parse_field("Signature", lines[n])
        n += 1

        membership = cls(
            issuer,
            membership_block_id,
            uid,
            identity_block_id,
            version=version,
            currency=currency,
            membership_type=membership_type,
        )

        # return membership with signature
        membership.signature = signature
        return membership

    def raw(self) -> str:
        """
        Return signed raw format string of the Membership instance

        :return:
        """
        return """Version: {0}
Type: Membership
Currency: {1}
Issuer: {2}
Block: {3}
Membership: {4}
UserID: {5}
CertTS: {6}
""".format(
            self.version,
            self.currency,
            self.issuer,
            self.membership_block_id,
            self.membership_type,
            self.uid,
            self.identity_block_id,
        )

    def inline(self) -> str:
        """
        Return inline string format of the Membership instance
        :return:
        """
        return "{0}:{1}:{2}:{3}:{4}".format(
            self.issuer,
            self.signature,
            self.membership_block_id,
            self.identity_block_id,
            self.uid,
        )
