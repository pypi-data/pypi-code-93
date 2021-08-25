from base64 import b64decode, b64encode
from datetime import datetime
import json

from Crypto import Random
from Crypto.Cipher import PKCS1_v1_5
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
import magic


def cid_decrypt(encrypted_cid, private_key):
    key = RSA.importKey(b64decode(private_key))
    dsize = SHA.digest_size
    sentinel = Random.new().read(15 + dsize)
    cipher = PKCS1_v1_5.new(key)
    message = cipher.decrypt(b64decode(encrypted_cid), sentinel)
    return message


def cid_encrypt(cid, public_key):
    pubkey = RSA.importKey(b64decode(public_key))
    cipher = PKCS1_v1_5.new(pubkey)

    # without padding digest
    message = b64encode(cipher.encrypt(cid.encode('utf-8')))

    # with padding digest
    # h = SHA.new(cid.encode('utf-8'))
    # print(h.digest())
    # message = b64encode(cipher.encrypt((cid).encode('utf-8') + h.digest()))

    return message


# Utils

def create_lite_metadata_from_cid(cid, ipfs):
    content_buffer = ipfs.cat(cid)

    mime_type = magic.from_buffer(content_buffer, mime=True)
    size_in_bytes = len(content_buffer)
    file_name = '{name}.{ext}'.format(
        name=int(datetime.now().timestamp()),
        ext=mime_type.split('/')[1]
    )

    return [{
        'cid': cid,
        'filename': file_name,
        'mimeType': mime_type,
        'size': size_in_bytes
    }]


def create_lite_metadata_from_file(filepath, ipfs):
    cid = ipfs.add(filepath)['Hash']
    return create_lite_metadata_from_cid(cid, ipfs)


def add_metadata_to_ipfs(
        ipfs_http_client,
        metadata,
        metadata_filepath='/tmp/metadata.json'):
    with open(metadata_filepath, 'w') as f:
        json.dump(metadata, f)
    cid = ipfs_http_client.add(metadata_filepath)['Hash']
    return cid


def create_transaction(
        niota,
        ipfs_http_client,
        cid,
        sender_peer_id,
        receiver_address,
        receiver_public_key,
        tag):
    metadata = create_lite_metadata_from_cid(cid, ipfs_http_client)
    meta_cid = add_metadata_to_ipfs(ipfs_http_client, metadata)
    message = {
        'pid': sender_peer_id,
        'cid': cid_encrypt(meta_cid, receiver_public_key).decode('utf-8')
    }
    return niota.propose_transaction(
        tag,
        message,
        value=0,
        address=receiver_address)
