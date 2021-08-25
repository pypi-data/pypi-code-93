#!/usr/bin/python3

import argparse
import json
import logging

import ipfshttpclient

from niota import ipfs
from niota import NumbersIOTA


logger = logging.getLogger(__name__)
niota = NumbersIOTA()


def load_config(config_filepath='iota_config.json'):
    with open(config_filepath) as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cid', '-c', required=True, help='Image CID')
    args = parser.parse_args()

    logger.info('Note: This tool requires a local IPFS daemon.')
    logger.info('Image CID: ' + args.cid)

    # Init
    niota_instance = niota.NumbersIOTA()
    ipfs_http_client = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001')

    # Transaction
    config = load_config()
    transaction_url = ipfs.create_transaction(
        niota_instance,
        ipfs_http_client,
        args.cid,
        config['sender_peer_id'],
        config['receiver_address'],
        config['receiver_public_key'],
        config['tag'],
    )
    logger.info('Transaction URL: {}'.format(transaction_url))


if __name__ == "__main__":
    main()
