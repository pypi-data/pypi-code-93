"""Static utility functions."""
import sys
import xml.etree.ElementTree as ET


def binary_type(string):
    """Return binary_type of string."""
    if sys.version_info[0] == 2:
        return string

    return string.encode('utf-8')


def get_saml_aws_roles(assertion):
    """Get the AWS roles contained in a decoded SAML assertion.

    This returns a list of RoleARN, PrincipalARN (IdP) pairs.
    """
    # Parse the returned assertion and extract the authorized roles
    awsroles = []
    root = ET.fromstring(assertion)
    for saml2attribute in root.iter("{urn:oasis:names:tc:SAML:2.0:assertion}Attribute"):
        if saml2attribute.get("Name") == "https://aws.amazon.com/SAML/Attributes/Role":
            for saml2attributevalue in saml2attribute.iter(
                "{urn:oasis:names:tc:SAML:2.0:assertion}AttributeValue"
            ):
                awsroles.append(saml2attributevalue.text)

    for awsrole in awsroles:
        chunks = awsrole.split(",")
        if "saml-provider" in chunks[0]:
            newawsrole = chunks[1] + "," + chunks[0]
            index = awsroles.index(awsrole)
            awsroles.insert(index, newawsrole)
            awsroles.remove(awsrole)

    return awsroles