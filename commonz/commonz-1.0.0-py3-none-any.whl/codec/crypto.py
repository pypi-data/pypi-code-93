#!/usr/bin/env python3
#coding: utf-8
### 1st line allows to execute this script by typing only its name in terminal, with no need to precede it with the python command
### 2nd line declaring source code charset should be not necessary but for exemple pydoc request it



__doc__ = "provide encryption and decryption"#information describing the purpose of this module
__status__ = "Development"#should be one of 'Prototype' 'Development' 'Production' 'Deprecated' 'Release'
__version__ = "1.0.0"# version number,date or about last modification made compared to the previous version
__license__ = "public domain"# ref to an official existing License
__date__ = "2019"#started creation date / year month day
__author__ = "N-zo syslog@laposte.net"#the creator origin of this prog,
__maintainer__ = "Nzo"#person who curently makes improvements, replacing the author
__credits__ = []#passed mainteners and any other helpers
__contact__ = "syslog@laposte.net"# current contact adress for more info about this file



### import the required modules

import rsa # available in Debian repository
from rsa import bigfile # rsa v4.0 droped the bigfile module, because insecure

from Crypto import Cipher
from Crypto import Random



### DES
### is no longer effective
### is inadequate and should not be used in important systems anymore,


### AES 
### is an symmetric key algorithm. Meaning encryption and decryption are done with the same key
### is a 128-block cipher algorithm. The data is divided into chunks of fixed 128 bits length.
### is faster than RSA
### is not currently susceptible to 'known-plaintext_attacks'(KPA).

### keys must be either 16, 24, or 32 bytes long
AES_SMALL_KEY_SIZE = 16
AES_BIG_KEY_SIZE = 32

### modes of operation
#AES_MODE=Cipher.AES.MODE_ECB # basic weak mode. Each block is encrypted independently of any other block.
#AES_MODE=Cipher.AES.MODE_CBC # extra recording of Initialization Vector(iv) is mandatory
#AES_MODE=Cipher.AES.MODE_CTR # many others values are mandatory
#AES_MODE=Cipher.AES.MODE_CFB # extra recording of Initialization Vector(iv) is mandatory
#AES_MODE=Cipher.AES.MODE_OFB # extra recording of Initialization Vector(iv) is mandatory
AES_MODE=Cipher.AES.MODE_OPENPGP # Initialization Vector(iv) is recorded inside the encrypted file

AES_ENC_IV_SIZE=16 #it must be 16 bytes long for encryption
AES_DEC_IV_SIZE=18 #it must be 18 bytes for decryption 

AES_BLOCKS_SIZE=16 # AES has a fixed data block size of 16 bytes.


### RSA 
### is an asymmetric key algorithm. Meaning, it uses 2 different keys for encryption and decryption. 
### is stream cipher algorithm. Meaning, entire data is encrypted at once,
### is more computationally intensive than AES and much slower.
### is mainly used to encrypt small amounts of data.

### key size in bits, must be at least 1024, but 2048 is recommended. The FIPS standard only defines 1024, 2048 and 3072.
RSA_SMALL_KEY_SIZE = 1024
RSA_BIG_KEY_SIZE = 2048

RSA_ASCII_FORMAT='PEM' # The PEM is Base64 encoded ASCII format, its the most common format
RSA_BIN_FORMAT='DER' # The DER is the binary format 



def rsa_get_key(keysize,format):
	"""get rsa key"""
	pubkey, privkey =rsa.newkeys(keysize) # key size in bits
	pub_pass = pubkey.save_pkcs1(format)
	priv_pass = privkey.save_pkcs1(format)
	#(cryptkey,decryptkey)
	return (pub_pass,priv_pass)

def rsa_crypt_file(inputfile,outputfile,pub_key,format):
	"""rsa file encryption"""
	key=rsa.PublicKey.load_pkcs1(pub_key,format)
	with open(inputfile, 'rb') as infile, open(outputfile, 'wb') as outfile:
		rsa.bigfile.encrypt_bigfile(infile, outfile, key)

def rsa_decrypt_file(inputfile,outputfile,priv_key,format):
	"""rsa file decryption"""
	key=rsa.PrivateKey.load_pkcs1(priv_key,format)
	with open(inputfile, 'rb') as infile, open(outputfile, 'wb') as outfile:
		rsa.bigfile.decrypt_bigfile(infile,outfile, key)



def aes_get_key(keysize):
	"""get aes key"""
	key= Random.get_random_bytes(keysize)
	return key
	
def aes_crypt_file(inputfile,outputfile,key,blocks_qantum):
	"""aes file encryption"""
	iv = Random.get_random_bytes(AES_ENC_IV_SIZE) 
	encryptor = Cipher.AES.new( key , AES_MODE, iv )
	with open(inputfile,'rb') as infile , open(outputfile,'wb') as outfile :
		bloksize=AES_BLOCKS_SIZE*blocks_qantum
		inputdata=True
		while inputdata :
			inputdata = infile.read(bloksize)
			outputdata = encryptor.encrypt(inputdata)
			outfile.write( outputdata )

def aes_decrypt_file(inputfile,outputfile,key,blocks_qantum):
	"""aes file decryption"""
	with open(inputfile,'rb') as infile , open(outputfile,'wb') as outfile :
		iv = infile.read(AES_DEC_IV_SIZE)
		decryptor = Cipher.AES.new( key , AES_MODE, iv )
		bloksize=AES_BLOCKS_SIZE*blocks_qantum
		inputdata=True
		while inputdata :
			inputdata = infile.read(bloksize)
			outputdata = decryptor.decrypt(inputdata)
			outfile.write( outputdata )

