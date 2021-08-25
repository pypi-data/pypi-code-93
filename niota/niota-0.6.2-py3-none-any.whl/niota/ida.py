from datetime import datetime
import hashlib
import json
import logging
import sys

import ipfshttpclient
from iota import TryteString

from .core import NumbersIOTA


logger = logging.getLogger(__name__)
niota = NumbersIOTA()


def parse_json(fname):
    with open(fname, "r", encoding='utf-8') as data_file:
        data = json.load(data_file)

    return data


# create cid
def create_cid(filepath, ipfs):
    cid = ipfs.add(filepath)['Hash']

    return cid


def create_tag(cid):
    cid_tryte = TryteString.from_unicode(cid)[0:24]
    tag = "NBS" + str(cid_tryte)

    return tag


def create_update_tag(input_tag):
    tag_length = len(input_tag)
    if tag_length < 27:
        extra = 27 - tag_length
        extra_value = extra * "9"
        tag = input_tag + extra_value
    else:
        tag = input_tag
    return tag


def create_ida_message(
        ida_cid='',
        ida_mid='',
        ida_sha256sum='',
        service_message=''):
    timestamp = int(datetime.now().timestamp())

    return {
        'timestamp': timestamp,
        'ida_cid': ida_cid,
        'ida_mid': ida_mid,
        'ida_sha256sum': ida_sha256sum,
        'service_message': service_message,
    }


def create_ida_transaction(
        ida_cid='',
        ida_mid='',
        ida_sha256sum='',
        provider='NUMBERSPROTOCOL',
        service_message=''):

    tag = create_tag(ida_cid)
    message = create_ida_message(
        ida_cid=ida_cid,
        ida_mid=ida_mid,
        ida_sha256sum=ida_sha256sum,
        service_message=service_message)
    value = 0
    full_add = niota.propose_transaction(
        tag, message, value=value, provider=provider)
    transaction_hash = full_add[-81:]
    logger.info("Transaction sent to the tangle!")
    logger.info(full_add)
    logger.info("Transaction Hash")
    logger.info(transaction_hash)
    logger.info("TAG")
    logger.info(tag)

    return {
        'tag': tag,
        'transaction': transaction_hash,
        'cid': ida_cid,
    }


def create_record_transaction(
        tag='',
        ida_cid='',
        ida_mid='',
        ida_sha256sum='',
        provider='NUMBERSPROTOCOL',
        service_message=''):

    message = create_ida_message(
        ida_cid=ida_cid,
        ida_mid=ida_mid,
        ida_sha256sum=ida_sha256sum,
        service_message=service_message)
    value = 0
    full_add = niota.propose_transaction(
        tag, message, value=value, provider=provider)
    transaction_hash = full_add[-81:]
    logger.info("Transaction sent to the tangle!")
    logger.info(full_add)
    logger.info("Transaction Hash")
    logger.info(transaction_hash)
    logger.info("TAG")
    logger.info(tag)

    return {
        'tag': tag,
        'transaction': transaction_hash,
        'cid': ida_cid,
    }


def create_transaction_from_json(json_file):
    _json_data = parse_json(json_file)
    json_data = json.dumps(_json_data, sort_keys=True).encode('utf-8')
    json_hash = hashlib.sha256(json_data).hexdigest()

    ipfs = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001')
    cid = create_cid(json_file, ipfs)

    return create_ida_transaction(
        ida_cid=cid,
        ida_sha256sum=json_hash,
        provider='NUMBERSIDA',
        service_message='creation transaction')


def create_update_transaction_from_json(json_file, input_tag):
    _json_data = parse_json(json_file)
    json_data = json.dumps(_json_data, sort_keys=True).encode('utf-8')
    json_hash = hashlib.sha256(json_data).hexdigest()

    ipfs = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001')
    cid = create_cid(json_file, ipfs)

    return create_record_transaction(
        tag=input_tag,
        ida_cid=cid,
        ida_sha256sum=json_hash,
        provider='NUMBERSIDA',
        service_message='update transaction')


def search(input_tag):
    hash_list = []
    transaction = niota.get_tranaction_by_tag(input_tag)
    # if only one transaction hash
    # print(transaction.hash)

    # if more than one transaction hash per tag
    for i in transaction:
        print(i.hash)
        hash_list.append(i.hash)

    # return transaction.hash
    return hash_list


def main():
    action = sys.argv[1]
    assert action in ['--first', '--update', '--search'], \
        'Action is not one of --first, --udpdate or --search: ' + action

    if action == '--first':
        filename = sys.argv[2]
        create_transaction_from_json(filename)

    elif action == '--update':
        filename = sys.argv[2]
        input_tag = sys.argv[3]

        tag = create_update_tag(input_tag)
        create_update_transaction_from_json(filename, tag)

    elif action == '--search':
        tag = sys.argv[2]

        search(tag)


if __name__ == "__main__":
    main()
