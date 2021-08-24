# -*- coding: utf-8 -*-

import base64
from Crypto.Cipher import Blowfish

# Funcao para encriptar de drcriptogravar dados
class Criptografia(object):
    def __init__(self, secret_key, id, salt):
        secret_key = secret_key[:11] + secret_key[-12:]
        id = str(id).ljust(10, 'x')
        salt = salt[:23]
        self.chave = '%s%s%s' % (secret_key, id, salt)

    def encriptar(self, string):
        """Encripta um código qualquer usando uma chave dinâmica."""
        encryption_object = Blowfish.new(self.chave)
        padding = ''
        if (len(string) % 8) != 0:
            padding = 'x' * (8 - (len(string) % 8))
        return base64.b64encode(encryption_object.encrypt(string + padding))

    def decriptar(self, string):
        """Decripta um código qualquer usando uma chave dinâmica."""
        encryption_object = Blowfish.new(self.chave)
        return encryption_object.decrypt(base64.b64decode(string)).rstrip('x')


# Este modulo existe pra facilitar a criptografia
# quando existe terceiros no meio, por exemplo,
# fazer login via token
"""
import java.math.BigInteger;
import java.security.Key;

import javax.crypto.Cipher;
import javax.crypto.spec.SecretKeySpec;
import sun.misc.BASE64Encoder;

public class HelloWorld {

    public static void main(String[] args) throws Exception {
        String s = "udlei@nati.biz";
        Cipher cipher = Cipher.getInstance("Blowfish/ECB/PKCS5Padding");
        Key key = new SecretKeySpec("85b72cf920150730".getBytes(), "Blowfish");
        cipher.init(Cipher.ENCRYPT_MODE, key);
        byte[] enc_bytes = cipher.doFinal(s.getBytes());
        String encode = new String(new BASE64Encoder().encode(enc_bytes));
        System.out.println("Base64Encoder: " + encode);
    }

}
"""
class CriptografiaComTerceiros(object):
    # Chave SEMPRE com 16 caracteres
    def __init__(self, chave):
        self.chave = chave

    def encriptar(self, string):
        key = self.chave
        c1  = Blowfish.new(key, Blowfish.MODE_ECB)
        packedString = self.PKCS5Padding(string)
        return base64.b64encode(c1.encrypt(packedString))

    def decriptar(self, string):
        key = self.chave
        c1  = Blowfish.new(key, Blowfish.MODE_ECB)
        r1 = c1.decrypt(base64.b64decode(string))
        r1 = r1.replace('\x00','').replace('\x01','').replace('\x02','').replace('\x03','').replace('\x04','')
        r1 = r1.replace('\x05','').replace('\x06','').replace('\x07','').replace('\x08','').replace('\x09','')
        return r1

    def PKCS5Padding(self,string):
        byteNum = len(string)
        packingLength = 8 - byteNum % 8
        appendage = chr(packingLength) * packingLength
        return string + appendage