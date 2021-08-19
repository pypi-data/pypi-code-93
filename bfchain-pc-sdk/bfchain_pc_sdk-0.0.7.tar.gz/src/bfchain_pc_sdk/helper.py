from util.helper import get_pk_sk_from_mnemonic_words, get_address


def get_user_from_secret(secret,prefix):
    pk, sk = get_pk_sk_from_mnemonic_words(secret)
    address = get_address(pk,prefix)
    return pk, sk, address
