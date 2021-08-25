import pgpy
import json
import gnupg
import time
from .key_pgp import Key
from abc import ABC, abstractmethod
from s3i.exception import raise_error_from_s3ib_msg, S3IBMessageError


class Message(ABC):
    """This is the abstract base class of an S3I message. It provides all functions concerning the signature and the encryption of an S3I message.
    """

    def __init__(self, msg):
        """Constructor of the abstract class.

        :param msg: PGP message, if empty or false type, a new PGP message is created.
        :type msg: str, bytes, pgpy.pgp.PGPMessage
        """
        if isinstance(msg, str or bytes):
            self._pgpMsg = pgpy.PGPMessage.from_blob(msg)
        elif isinstance(msg, pgpy.pgp.PGPMessage):
            self._pgpMsg = msg
        else:
            self._pgpMsg = pgpy.PGPMessage.new(str(msg))

    @property
    def pgpMsg(self):
        """PGP message
        """
        return self._pgpMsg

    @pgpMsg.setter
    def pgpMsg(self, value):
        self._pgpMsg = value

    def sign(self, secKey):
        """This function signs the message with the given private key. The signing is done as described in RFC 4880.

        :param secKey: Private PGP Key with which the signature is done. This key should be the secret key of the sender. It should be the counter part of the public key which is deposited in the S3I Directory or some other known database.
        :type secKey: pgpy.PGPKey
        :return: The signed PGP message
        :rtype: pgpy.PGPMessage 
        """
        self.pgpMsg |= secKey.sign(self.pgpMsg)
        return self.pgpMsg

    def verify(self, pubKey):
        """This function verifies the signature of the mesage with the given public key. If the signature is valid for the given key the function returns True.

        :param pubKey: Public PGP Key with which the signature is verified. This key should be the public key of the sender.
        :type pubKey: pgpy.PGPKey
        :return: Can be compared directly as a boolean to determine whether or not the specified signature verified.
        :rtype: pgpy.types.SignatureVerification
        """
        verif = pubKey.verify(self.pgpMsg)
        return verif

    def encrypt(self, pubKey):
        """This function encrypts the message with the given public key. The encryption is done as described in RFC 4880.

        :param pubKey: List of public PGP Keys with which the enryption is done. These keys should be the public keys of the receivers, which can be found in the S3I Directory or some other shared database.
        :type pubKey: list of pgpy.PGPKey
        :return: The encrypted PGP message is returned.
        :rtype: pgpy.PGPMessage
        """

        def encrypt_mess(pubKey, message, cipher, sessionKey):
            enc_msg = pubKey.encrypt(message, cipher=cipher, sessionkey=sessionkey)
            return enc_msg

        cipher = pgpy.constants.SymmetricKeyAlgorithm.AES256
        sessionkey = cipher.gen_key()
        for i in pubKey:
            self.pgpMsg = encrypt_mess(i.key, self.pgpMsg, cipher, sessionkey)
        return self.pgpMsg

    def decrypt(self, secKey):
        """This function decrypts the message with the given private key. 

        :param secKey: The private key of the receiver.
        :type secKey: pgpy.PGPKey
        :return: The decrypted PGP message is returned.
        :rtype: pgpy.PGPMessage 
        """
        dec = secKey.decrypt(self.pgpMsg)
        self.pgpMsg = dec
        print(
            "[S3I]["
            + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            + "]: Decryption successful"
        )
        return dec

    def decryptAndVerify(self, secKey, fp, dir):
        """This function decrypts the message with the given private key and verifies the signature with the given public key. This function needs a gpg executable. If no gpg executable can be found the message is only decrypted but not verified. To install gpg on your computer go to https://gnupg.org/download/ and choose the right binary release for your operating system.

        :param secKey: The private key of the receiver.
        :type secKey: pgpy.PGPKey
        :param fp: Path to the home directory of the demo where a gpg folder is created.
        :type fp: str
        :param dir: An S3I Directory instance to look up the public key of the sender to verify the signature.
        :type dir: s3i.directory.Directory
        :return: The decrypted PGP message is returned. If the signature is not valid, the function returns None.
        :rtype: pgpy.PGPMessage 
        """
        try:
            gpg = gnupg.GPG(gnupghome=fp)
            import_result_sec = gpg.import_keys(secKey.key.__bytes__())
            decrypted_data = gpg.decrypt(self.pgpMsg.__bytes__())

            sender = json.loads(decrypted_data.data.decode("utf-8").replace("'", '"'))[
                "sender"
            ]
            key_blob = dir.getPublicKey(sender)
            pgpKey_pub = Key(key_str=key_blob)
            import_result_pub = gpg.import_keys(pgpKey_pub.key.__bytes__())

            decrypted_data = gpg.decrypt(self.pgpMsg.__bytes__())

            if decrypted_data.valid:
                print(
                    "[S3I]["
                    + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    + "]: The signature is valid."
                )
                print(
                    "[S3I]["
                    + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    + "]: Decryption successful"
                )
                self.msg = json.loads(
                    decrypted_data.data.decode("utf-8").replace("'", '"')
                )
                return decrypted_data.data
            else:
                return None
        except:
            print(
                "[S3I]["
                + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                + "]: No Gpg executable can be found. The signature can not be verified. But the message will be decrypted."
            )
            return self.decrypt(secKey=secKey.key)


class UserMessage(Message):
    # S3I-B user message template
    _msg = {
        "sender": "",
        "identifier": "",
        "receivers": [],
        "messageType": "userMessage",
        "replyToEndpoint": "",
        "attachments": [],
        "subject": "",
        "text": "",
    }

    def __init__(
            self,
            json_in=None,
            msg_blob=None,
            sender=None,
            identifier=None,
            receivers=None,
            subject=None,
            text=None,
            replyToEndpoint=None,
            attachments=None,
    ):
        """Constructor

        :param json: JSON-formatted data to initialize the user message
        :type json: dict, string
        :param msg_blob: PGP message to initialize the user message
        :type msg_blob: string, bytes
        :param sender: id of the sender
        :type sender: string
        :param identifier: id of the message
        :type identitifer: string
        :param receivers: id of the receiver
        :type receivers: list of strings
        :param replyToEndpoint: endpoint of the sender
        :type replyToEndpoint: string
        :param subject: subject of the message
        :type subject: string
        :param text: text body of the message
        :type text: string
        :param attachments: List of dicts. Every dict has two keys: "filename" with value type str and "data" with value type BASE64-encoded str
        :type attachments: list
        """

        super().__init__(msg=msg_blob)
        if isinstance(json_in, dict):
            for k, v in json_in.items():
                self.msg[k] = v
        elif isinstance(json_in, str):
            x = json.loads(json_in)  # TODO check if it is template-conform
            self.msg = x

        fields = {
            "sender": sender,
            "identifier": identifier,
            "receivers": receivers,
            "subject": subject,
            "text": text,
            "replyToEndpoint": replyToEndpoint,
            "attachments": attachments,
        }
        for (key, value) in fields.items():
            if value:
                self.msg[key] = value
        if any(fields.values()):
            self.pgpMsg = pgpy.PGPMessage.new(str(self.msg))

    @property
    def msg(self):
        """S3I-B user message template
        """
        return self._msg

    @msg.setter
    def msg(self, value):
        self._msg = value
        self.pgpMsg = pgpy.PGPMessage.new(str(self.msg))

    def fillUserMessage(
            self,
            senderUUID,
            receiverUUIDs,
            sender_endpoint,
            subject,
            text,
            msgUUID,
            attachments=None,
            attachments_json=None,
    ):
        """This function fills the user message with the given inputs.

        :param senderUUID: id of the sender
        :type senderUUID: string
        :param receiverUUID: id of the receiver
        :type receiverUUID: string
        :param sender_endpoint: endpoint of the sender
        :type sender_endpoint: string
        :param subject: subject of the message
        :type subject: string
        :param text: text body of the message
        :type text: string
        :param attachments: List of dicts. Every dict has two keys: "filename" with value type string and "data" with value type BASE64-encoded str
        :type attachments: list
        :param msgUUID: ID of the message (generated by client)
        :type msgUUID: string
        """

        self.msg["sender"] = senderUUID
        self.msg["identifier"] = msgUUID
        self.msg["receivers"] = receiverUUIDs
        self.msg["subject"] = subject
        self.msg["replyToEndpoint"] = sender_endpoint
        self.msg["text"] = text

        """
        add the input attachments (dict) to user message
        """
        if attachments is not None:
            len_attachments = len(attachments)
            self.msg["attachments"] = [
                {"filename": "", "data": ""} for i in range(len_attachments)
            ]
            for i in range(len_attachments):
                self.msg["attachments"][i]["filename"] = attachments[i]["filename"]
                self.msg["attachments"][i]["data"] = attachments[i]["data"]
        if attachments_json is not None:
            self.msg["attachments"] = attachments_json

        self.msg["messageType"] = "userMessage"
        raise_error_from_s3ib_msg(self.msg, S3IBMessageError)
        self.pgpMsg = pgpy.PGPMessage.new(str(self.msg))

    def convertPgpToMsg(self):
        """This function converts the PGP message format in the JSON-based S3I message format of a UserMessage.
        """
        json_msg = json.loads(self.pgpMsg.message.replace("'", '"'))
        self.fillUserMessage(
            senderUUID=json_msg["sender"],
            receiverUUIDs=json_msg["receivers"],
            sender_endpoint=json_msg["replyToEndpoint"],
            subject=json_msg["subject"],
            text=json_msg["text"],
            msgUUID=json_msg["identifier"],
            attachments_json=json_msg["attachments"],
        )


class ServiceRequest(Message):
    def __init__(self, json=None, msg_blob=None):
        """Constructor

        :param json: JSON-formatted data to initialize the service request
        :type json: dict, str
        :param msg_blob: PGP message to initialize the service request
        :type msg_blob: str, bytes
        """
        # S3I-B service request template
        self._msg = {
            "sender": "",
            "identifier": "",
            "receivers": [],
            "messageType": "serviceRequest",
            "replyToEndpoint": "",
            "serviceType": "",
            "parameters": {},
        }

        super().__init__(msg=msg_blob)
        if isinstance(json, dict):  # TODO check if it is template-conform
            for k, v in json.items():
                self.msg[k] = v
        elif isinstance(json, str):
            x = json.loads(json)
            self.msg = x

    @property
    def msg(self):
        """S3I-B service request template
        """
        return self._msg

    @msg.setter
    def msg(self, value):
        self._msg = value
        self.pgpMsg = pgpy.PGPMessage.new(str(self.msg))

    def fillServiceRequest(
            self,
            senderUUID,
            receiverUUIDs,
            sender_endpoint,
            serviceType,
            parameters,
            msgUUID,
    ):
        """This function fills the service request with the given inputs.

        :param senderUUID: id of the sender
        :type senderUUID: str
        :param receiverUUIDs: id of the receivers
        :type receiverUUIDs: list
        :param sender_endpoint: endpoint of the sender
        :type sender_endpoint: str
        :param serviceType: serviceType of the message
        :type serviceType: str
        :param parameters: parameters of the service request
        :type parameters: dict
        :param msgUUID: ID of the message (client-generated)
        :type msgUUID: str
        """

        self.msg["sender"] = senderUUID
        self.msg["identifier"] = msgUUID
        self.msg["receivers"] = receiverUUIDs
        self.msg["messageType"] = "serviceRequest"
        self.msg["replyToEndpoint"] = sender_endpoint
        self.msg["serviceType"] = serviceType

        if parameters is None:
            self.msg["parameters"] = ""
            print("[S3I]: Service request without parameters")

        else:
            self.msg["parameters"] = parameters
        raise_error_from_s3ib_msg(self.msg, S3IBMessageError)

    def convertPgpToMsg(self):
        """This function converts the PGP message format in the JSON-based S3I message format of a service request.
        """
        json_msg = json.loads(self.pgpMsg.message.replace("'", '"'))
        self.fillServiceRequest(
            senderUUID=json_msg["sender"],
            receiverUUIDs=json_msg["receivers"],
            sender_endpoint=json_msg["replyToEndpoint"],
            serviceType=json_msg["serviceType"],
            parameters=json_msg["parameters"],
            msgUUID=json_msg["identifier"],
        )


class ServiceReply(Message):
    def __init__(self, json=None, msg_blob=None):
        """Constructor

        :param json: JSON-formatted data to initialize the service reply
        :type json: dict, str
        :param msg_blob: PGP message to initialize the service reply
        :type msg_blob: str, bytes
        """
        # S3I-B service reply template
        self._msg = {
            "sender": "",
            "identifier": "",
            "receivers": [],
            "messageType": "serviceReply",
            "serviceType": "",
            "replyingToMessage": "",
            "results": {},
        }

        super().__init__(msg=msg_blob)
        if isinstance(json, dict):  # TODO check if it is template-conform
            for k, v in json.items():
                self.msg[k] = v
        elif isinstance(json, str):
            x = json.loads(json)
            self.msg = x

    @property
    def msg(self):
        """S3I-B service reply template
        """
        return self._msg

    @msg.setter
    def msg(self, value):
        self._msg = value
        self.pgpMsg = pgpy.PGPMessage.new(str(self.msg))

    def fillServiceReply(
            self, senderUUID, receiverUUIDs, serviceType, results, msgUUID, replyingToUUID
    ):
        """This function fills the service reply with the given inputs.

        :param senderUUID: id of the sender
        :type senderUUID: str
        :param receiverUUIDs: id of the receivers
        :type receiverUUIDs: list
        :param serviceType: serviceType of the message
        :type serviceType: str
        :param results: service results
        :type results: dict
        :param msgUUID: id of the message (client-generated)
        :type msgUUID: str
        :param replyingToUUID: id of the message this reply relates to
        :type replyingToUUID: str
        """

        self.msg["sender"] = senderUUID
        self.msg["identifier"] = msgUUID
        self.msg["receivers"] = receiverUUIDs
        self.msg["serviceType"] = serviceType
        self.msg["results"] = results
        self.msg["replyingToMessage"] = replyingToUUID
        raise_error_from_s3ib_msg(self.msg, S3IBMessageError)

    def convertPgpToMsg(self):
        """This function converts the PGP message format in the JSON-based S3I message format of a service reply.
        """
        json_msg = json.loads(self.pgpMsg.message.replace("'", '"'))
        self.fillServiceReply(
            senderUUID=json_msg["sender"],
            receiverUUIDs=json_msg["receivers"],
            replyingToUUID=json_msg["replyToEndpoint"],
            serviceType=json_msg["serviceType"],
            results=json_msg["results"],
            msgUUID=json_msg["identifier"],
        )


class GetValueRequest(Message):
    def __init__(self, json=None, msg_blob=None):
        """Constructor

        :param json: JSON-formatted data to initialize the get value request
        :type json: dict, str
        :param msg_blob: PGP message to initialize the get value request
        :type msg_blob: str, bytes
        """
        # S3I-B get value request template
        self._msg = {
            "sender": "",
            "identifier": "",
            "receivers": [""],
            "messageType": "getValueRequest",
            "replyToEndpoint": "",
            "attributePath": "",
        }
        super().__init__(msg=msg_blob)
        if isinstance(json, dict):  # TODO check if it is template-conform
            for k, v in json.items():
                self.msg[k] = v
        elif isinstance(json, str):
            x = json.loads(json)
            self.msg = x

    @property
    def msg(self):
        """S3I-B get value request template
        """
        return self._msg

    @msg.setter
    def msg(self, value):
        self._msg = value
        self.pgpMsg = pgpy.PGPMessage.new(str(self.msg))

    def fillGetValueRequest(
            self, senderUUID, receiverUUIDs: list, sender_endpoint, attributePath, msgUUID
    ):
        """This function fills the get value request with the given inputs.

        :param senderUUID: id of the sender
        :type senderUUID: str
        :param receiverUUIDs: id of the receivers
        :type receiverUUIDs: list
        :param sender_endpoint: endpoint of the sender
        :type sender_endpoint: str
        :param attributePath: path in the data model of the respective thing to get to the desired attribute
        :type attributePath: str
        :param msgUUID: ID of the message (client-generated)
        :type msgUUID: str
        """
        self.msg["sender"] = senderUUID
        self.msg["identifier"] = msgUUID
        self.msg["receivers"] = receiverUUIDs  # [0]["receiver"]
        self.msg["replyToEndpoint"] = sender_endpoint
        self.msg["attributePath"] = attributePath
        raise_error_from_s3ib_msg(self.msg, S3IBMessageError)

    def convertPgpToMsg(self):
        """This function converts the PGP message format in the JSON-based S3I message format of a get value request.
        """
        json_msg = json.loads(self.pgpMsg.message.replace("'", '"'))
        self.fillGetValueRequest(
            senderUUID=json_msg["sender"],
            receiverUUIDs=json_msg["receivers"],
            sender_endpoint=json_msg["replyToEndpoint"],
            attributePath=json_msg["attributePath"],
            msgUUID=json_msg["identifier"],
        )


class GetValueReply(Message):
    def __init__(self, json=None, msg_blob=None):
        """Constructor

        :param json: JSON-formatted data to initialize the get value reply
        :type json: dict, str
        :param msg_blob: PGP message to initialize the get value reply
        :type msg_blob: str, bytes
        """
        # S3I-B get value reply template
        self._msg = {
            "sender": "",
            "identifier": "",
            "receivers": [],
            "messageType": "getValueReply",
            "replyingToMessage": "",
            "value": {},
        }
        super().__init__(msg=msg_blob)
        if isinstance(json, dict):  # TODO check if it is template-conform
            for k, v in json.items():
                self.msg[k] = v
        elif isinstance(json, str):
            x = json.loads(json)
            self.msg = x

    @property
    def msg(self):
        """S3I-B get value reply template
        """
        return self._msg

    @msg.setter
    def msg(self, value):
        self._msg = value
        self.pgpMsg = pgpy.PGPMessage.new(str(self.msg))

    def fillGetValueReply(
            self, senderUUID, receiverUUIDs: list, results, msgUUID, replyingToUUID
    ):
        """This function fills the get value reply with the given inputs.

        :param senderUUID: id of the sender
        :type senderUUID: str
        :param receiverUUIDs: id of the receivers
        :type receiverUUIDs: list
        :param results: get value results
        :type results: dict
        :param msgUUID: id of the message (client-generated)
        :type msgUUID: str
        :param replyingToUUID: id of the message this reply relates to
        :type replyingToUUID: str
        """
        self.msg["sender"] = senderUUID
        self.msg["identifier"] = msgUUID
        self.msg["receivers"] = receiverUUIDs
        self.msg["replyingToMessage"] = replyingToUUID
        self.msg["value"] = results
        raise_error_from_s3ib_msg(self.msg, S3IBMessageError)

    def convertPgpToMsg(self):
        """This function converts the PGP message format in the JSON-based S3I message format of a get value reply.
        """
        json_msg = json.loads(self.pgpMsg.message.replace("'", '"'))
        self.fillGetValueReply(senderUUID=json_msg["sender"], receiverUUIDs=json_msg["receivers"],
                               replyingToUUID=json_msg["replyingToMessage"],
                               results=json_msg["value"], msgUUID=json_msg["identifier"])


class SetValueRequest(Message):
    def __init__(self, json=None, msg_blob=None):
        """Constructor

        :param json: JSON-formatted data to initialize the set value request
        :type json: dict, str
        :param msg_blob: PGP message to initialize the set value request
        :type msg_blob: str, bytes
        """
        # S3I-B set value request template
        self._msg = {
            "sender": "",
            "identifier": "",
            "receivers": [],
            "messageType": "setValueRequest",
            "replyToEndpoint": "",
            "attributePath": "",
            "newValue": 0
        }

        super().__init__(msg=msg_blob)
        if isinstance(json, dict):  # TODO check if it is template-conform
            for k, v in json.items():
                self.msg[k] = v
        elif isinstance(json, str):
            x = json.loads(json)
            self.msg = x

    @property
    def msg(self):
        """S3I-B set value request template
        """
        return self._msg

    @msg.setter
    def msg(self, value):
        self._msg = value
        self.pgpMsg = pgpy.PGPMessage.new(str(self.msg))

    def fillSetValueRequest(
            self,
            senderUUID,
            receiverUUIDs,
            sender_endpoint,
            attributePath,
            newValue,
            msgUUID,
    ):
        """This function fills the set value request with the given inputs.

        :param senderUUID: id of the sender
        :type senderUUID: str
        :param receiverUUIDs: id of the receivers
        :type receiverUUIDs: list
        :param sender_endpoint: endpoint of the sender
        :type sender_endpoint: str
        :param attributePath: attribute path
        :type attributePath: str
        :param newValue: new value
        :type newValue: any
        :param msgUUID: ID of the message (client-generated)
        :type msgUUID: str
        """

        self.msg["sender"] = senderUUID
        self.msg["identifier"] = msgUUID
        self.msg["receivers"] = receiverUUIDs
        self.msg["messageType"] = "setValueRequest"
        self.msg["replyToEndpoint"] = sender_endpoint
        self.msg["attributePath"] = attributePath
        self.msg["newValue"] = newValue

        raise_error_from_s3ib_msg(self.msg, S3IBMessageError)

    def convertPgpToMsg(self):
        """This function converts the PGP message format in the JSON-based S3I message format of a set value request.
        """
        json_msg = json.loads(self.pgpMsg.message.replace("'", '"'))
        self.fillServiceRequest(
            senderUUID=json_msg["sender"],
            receiverUUIDs=json_msg["receivers"],
            sender_endpoint=json_msg["replyToEndpoint"],
            attributePath=json_msg["attributePath"],
            newValue=json_msg["newValue"],
            msgUUID=json_msg["identifier"],
        )


class SetValueReply(Message):
    def __init__(self, json=None, msg_blob=None):
        """Constructor

        :param json: JSON-formatted data to initialize the set value reply
        :type json: dict, str
        :param msg_blob: PGP message to initialize the set value reply
        :type msg_blob: str, bytes
        """
        # S3I-B set value reply template
        self._msg = {
            "sender": "",
            "identifier": "",
            "receivers": [],
            "messageType": "setValueReply",
            "replyingToMessage": "",
            "ok": False,
        }

        super().__init__(msg=msg_blob)
        if isinstance(json, dict):  # TODO check if it is template-conform
            for k, v in json.items():
                self.msg[k] = v
        elif isinstance(json, str):
            x = json.loads(json)
            self.msg = x

    @property
    def msg(self):
        """S3I-B set value reply template
        """
        return self._msg

    @msg.setter
    def msg(self, value):
        self._msg = value
        self.pgpMsg = pgpy.PGPMessage.new(str(self.msg))

    def fillSetValueReply(
            self,
            senderUUID,
            receiverUUIDs,
            ok,
            replyingToUUID,
            msgUUID,
    ):
        """This function fills the set value reply with the given inputs.

        :param senderUUID: id of the sender
        :type senderUUID: str
        :param receiverUUIDs: id of the receivers
        :type receiverUUIDs: list
        :param replyingToUUID: reply to message
        :type replyingToUUID: str
        :param ok: indicates whether the value is set
        :type ok: str
        :param msgUUID: ID of the message (client-generated)
        :type msgUUID: str
        """

        self.msg["sender"] = senderUUID
        self.msg["identifier"] = msgUUID
        self.msg["receivers"] = receiverUUIDs
        self.msg["messageType"] = "setValueReply"
        self.msg["replyingToMessage"] = replyingToUUID
        self.msg["ok"] = ok

        raise_error_from_s3ib_msg(self.msg, S3IBMessageError)

    def convertPgpToMsg(self):
        """This function converts the PGP message format in the JSON-based S3I message format of a set value reply.
        """
        json_msg = json.loads(self.pgpMsg.message.replace("'", '"'))
        self.fillServiceRequest(
            senderUUID=json_msg["sender"],
            receiverUUIDs=json_msg["receivers"],
            sender_endpoint=json_msg["replyToEndpoint"],
            ok=json_msg["ok"],
            msgUUID=json_msg["identifier"],
        )


class EventSubscriptionRequest(Message):

    def __init__(self, json=None, msg_blob=None):
        """Constructor

        :param json: JSON-formatted data to initialize the event subscription request
        :type json: dict, str
        :param msg_blob: PGP message to initialize the event subscription request
        :type msg_blob: str, bytes
        """
        # S3I-B event subscription request template
        self._msg = {
            "sender": "",
            "identifier": "",
            "receivers": [],
            "messageType": "eventSubscriptionRequest",
            "replyToEndpoint": "",
            "RQL": ""
        }
        super().__init__(msg=msg_blob)
        if isinstance(json, dict):  # TODO check if it is template-conform
            for k, v in json.items():
                self.msg[k] = v
        elif isinstance(json, str):
            x = json.loads(json)
            self.msg = x

    @property
    def msg(self):
        """S3I-B event subscription request template
        """
        return self._msg

    @msg.setter
    def msg(self, value):
        self._msg = value
        self.pgpMsg = pgpy.PGPMessage.new(str(self.msg))

    def fillEventSubscriptionRequest(self, sender, receivers: list, msg_id, sender_endpoint, rql):
        """This function fills the event subscription request with the given inputs.

        :param sender: id of the sender
        :type sender: str
        :param receivers: id of the receivers
        :type receivers: list
        :param msg_id: id of the message (client-generated)
        :type msg_id: str
        :param sender_endpoint: endpoint of server that the message has been sent from
        :type sender_endpoint: str
        """
        self.msg["sender"] = sender
        self.msg["identifier"] = msg_id
        self.msg["receivers"] = receivers
        self.msg["replyToEndpoint"] = sender_endpoint
        self.msg["RQL"] = rql

    def convertPgpToMsg(self):
        """This function converts the PGP message format in the JSON-based S3I message format of a event subscription request.
        """
        json_msg = json.loads(self.pgpMsg.message.replace("'", '"'))
        self.fillEventSubscriptionRequest(sender=json_msg["sender"], receivers=json_msg["receivers"],
                                          msg_id=json_msg["identifier"], sender_endpoint=json_msg["replyToEndpoint"],
                                          rql=json_msg["RQL"])


class EventSubscriptionReply(Message):

    def __init__(self, json=None, msg_blob=None):
        """Constructor

        :param json: JSON-formatted data to initialize the event subscription reply
        :type json: dict, str
        :param msg_blob: PGP message to initialize the event subscription reply
        :type msg_blob: str, bytes
        """
        # S3I-B event subscription request template
        self._msg = {
            "sender": "",
            "identifier": "",
            "receivers": [],
            "messageType": "eventSubscriptionReply",
            "replyingToMessage": "",
            "subscription-id": "",
            "ok": bool
        }
        super().__init__(msg=msg_blob)
        if isinstance(json, dict):  # TODO check if it is template-conform
            for k, v in json.items():
                self.msg[k] = v
        elif isinstance(json, str):
            x = json.loads(json)
            self.msg = x

    @property
    def msg(self):
        """S3I-B event subscription reply template
        """
        return self._msg

    @msg.setter
    def msg(self, value):
        self._msg = value
        self.pgpMsg = pgpy.PGPMessage.new(str(self.msg))

    def fillEventSubscriptionReply(self, sender, receivers: list, msg_id, replying_to_message, subscription_id,
                                   status):
        """This function fills the event subscription request with the given inputs.

        :param sender: id of the sender
        :type sender: str
        :param receivers: id of the receivers
        :type receivers: list
        :param msg_id: id of the message (client-generated)
        :type msg_id: str
        :param replying_to_message: id of the message this reply relates to
        :type replying_to_message: str
        :param subscription_id: sub id
        :type subscription_id: str
        :param status: status of subscription
        :type status: bool
        """
        self.msg["sender"] = sender
        self.msg["identifier"] = msg_id
        self.msg["receivers"] = receivers
        self.msg["replyingToMessage"] = replying_to_message
        self.msg["subscription-id"] = subscription_id
        self.msg["ok"] = status

    def convertPgpToMsg(self):
        """This function converts the PGP message format in the JSON-based S3I message format of a event subscription reply.
        """
        json_msg = json.loads(self.pgpMsg.message.replace("'", '"'))
        self.fillEventSubscriptionRequest(sender=json_msg["sender"], receivers=json_msg["receivers"],
                                          msg_id=json_msg["identifier"],
                                          replying_to_message=json_msg["replyingToMessage"],
                                          subscription_id=json_msg["subscription-id"], status=json_msg["ok"])


class EventUnsubscriptionRequest(Message):

    def __init__(self, json=None, msg_blob=None):
        """Constructor

        :param json: JSON-formatted data to initialize the event unsubscribe request
        :type json: dict, str
        :param msg_blob: PGP message to initialize the event unsubscribe request
        :type msg_blob: str, bytes
        """
        # S3I-B event unsubscribe request template
        self._msg = {
            "sender": "",
            "identifier": "",
            "receivers": [],
            "messageType": "eventUnsubscriptionRequest",
            "replyToEndpoint": "",
            "subscription-id": ""
        }
        super().__init__(msg=msg_blob)
        if isinstance(json, dict):  # TODO check if it is template-conform
            for k, v in json.items():
                self.msg[k] = v
        elif isinstance(json, str):
            x = json.loads(json)
            self.msg = x

    @property
    def msg(self):
        """S3I-B event unsubscribe request template
        """
        return self._msg

    @msg.setter
    def msg(self, value):
        self._msg = value
        self.pgpMsg = pgpy.PGPMessage.new(str(self.msg))

    def fillEventUnsubscriptionRequest(self, sender, receivers: list, msg_id, sender_endpoint, sub_id):
        """This function fills the event unsubscribe request with the given inputs.

        :param sender: id of the sender
        :type sender: str
        :param receivers: id of the receivers
        :type receivers: list
        :param msg_id: id of the message (client-generated)
        :type msg_id: str
        :param sender_endpoint: id of the message this reply relates to
        :type sender_endpoint: str
        :param sub_id: event subscription id
        :type sub_id: str
        """
        self.msg["sender"] = sender
        self.msg["identifier"] = msg_id
        self.msg["receivers"] = receivers
        self.msg["replyToEndpoint"] = sender_endpoint
        self.msg["subscription-id"] = sub_id

    def convertPgpToMsg(self):
        """This function converts the PGP message format in the JSON-based S3I message format of a event unsubscribe reply.
        """
        json_msg = json.loads(self.pgpMsg.message.replace("'", '"'))
        self.fillEventSubscriptionRequest(sender=json_msg["sender"], receivers=json_msg["receivers"],
                                          msg_id=json_msg["identifier"], sender_endpoint=json_msg["replyToEndpoint"],
                                          sub_id=json_msg["subscription-id"])


class EventUnsubscriptionReply(Message):

    def __init__(self, json=None, msg_blob=None):
        """Constructor

        :param json: JSON-formatted data to initialize the event unsubscribe reply
        :type json: dict, str
        :param msg_blob: PGP message to initialize the event unsubscribe reply
        :type msg_blob: str, bytes
        """
        # S3I-B event unsubscribe reply template
        self._msg = {
            "sender": "",
            "identifier": "",
            "receivers": [],
            "messageType": "eventUnsubscriptionReply",
            "replyingToMessage": "",
            "subscription-id": "",
            "ok": bool
        }
        super().__init__(msg=msg_blob)
        if isinstance(json, dict):  # TODO check if it is template-conform
            for k, v in json.items():
                self.msg[k] = v
        elif isinstance(json, str):
            x = json.loads(json)
            self.msg = x

    @property
    def msg(self):
        """S3I-B event unsubscribe reply template
        """
        return self._msg

    @msg.setter
    def msg(self, value):
        self._msg = value
        self.pgpMsg = pgpy.PGPMessage.new(str(self.msg))

    def fillEventUnsubscriptionReply(self, sender, receivers: list, msg_id, replying_to_message, sub_id, status=bool):
        """This function fills the event unsubscription reply with the given inputs.

        :param sender: id of the sender
        :type sender: str
        :param receivers: id of the receivers
        :type receivers: list
        :param msg_id: id of the message (client-generated)
        :type msg_id: str
        :param replying_to_message: id of the message this reply relates to
        :type replying_to_message: str
        :param sub_id: event subscription id
        :type sub_id: str
        :param status: status of unsubscribe a event
        :type status: bool
        """
        self.msg["sender"] = sender
        self.msg["identifier"] = msg_id
        self.msg["receivers"] = receivers
        self.msg["replyToEndpoint"] = replying_to_message
        self.msg["subscription-id"] = sub_id
        self.msg["ok"] = status

    def convertPgpToMsg(self):
        """This function converts the PGP message format in the JSON-based S3I message format of a event unsubscribe reply.
        """
        json_msg = json.loads(self.pgpMsg.message.replace("'", '"'))
        self.fillEventSubscriptionRequest(sender=json_msg["sender"], receivers=json_msg["receivers"],
                                          msg_id=json_msg["identifier"],
                                          replying_to_message=json_msg["replyToEndpoint"],
                                          sub_id=json_msg["subscription-id"], status=json_msg["ok"])


class EventMessage(Message):
    def __init__(self, json=None, msg_blob=None):
        """Constructor

        :param json: JSON-formatted data to initialize the event message
        :type json: dict, str
        :param msg_blob: PGP message to initialize the event message
        :type msg_blob: str, bytes
        """
        # S3I-B event unsubscribe request template
        self._msg = {
            "sender": "",
            "identifier": "",
            "receivers": [],
            "messageType": "eventMessage",
            "subscription-id": "",
            "position": {
                "longtitude": "",
                "latitude": ""
            },
            "time": "",
            "content": ""
        }
        super().__init__(msg=msg_blob)
        if isinstance(json, dict):  # TODO check if it is template-conform
            for k, v in json.items():
                self.msg[k] = v
        elif isinstance(json, str):
            x = json.loads(json)
            self.msg = x

    @property
    def msg(self):
        """S3I-B event message template
        """
        return self._msg

    @msg.setter
    def msg(self, value):
        self._msg = value
        self.pgpMsg = pgpy.PGPMessage.new(str(self.msg))

    def fillEventMessage(self, sender, receivers: list, msg_id, sub_id, timestamp, content):
        """This function fills the event messages with the given inputs.

        :param sender: id of the sender
        :type sender: str
        :param receivers: id of the receivers
        :type receivers: list
        :param msg_id: id of the message (client-generated)
        :type msg_id: str
        :param sub_id: event subscription id
        :type sub_id: str
        :param timestamp: timestamp of current event
        :type timestamp: str
        :param content: content of event message
        :type content: str
        """
        self.msg["sender"] = sender
        self.msg["identifier"] = msg_id
        self.msg["receivers"] = receivers
        self.msg["subscription-id"] = sub_id
        self.msg["time"] = timestamp
        self.msg["content"] = content

    def convertPgpToMsg(self):
        """This function converts the PGP message format in the JSON-based S3I message format of a event message
        """
        json_msg = json.loads(self.pgpMsg.message.replace("'", '"'))
        self.fillEventMessage(sender=json_msg["sender"], receivers=json_msg["receivers"],
                              msg_id=json_msg["identifier"], sub_id=json_msg["subscription-id"],
                              timestamp=json_msg["time"], content=json_msg["content"])
