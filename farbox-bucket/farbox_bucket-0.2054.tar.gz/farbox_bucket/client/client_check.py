#coding: utf8
from farbox_bucket.client.action import send_message as send_farbox_bucket_message


def check_farbox_bucket_from_client(node, private_key):
    try:
        reply = send_farbox_bucket_message(
            node=node,
            private_key=private_key,
            action='check',
            message=''
        )
        if reply and reply.get('code') == 200:
            return True
        else:
            return False
    except:
        return False