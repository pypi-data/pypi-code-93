
import jwt
import time
public_key = '''-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDPN91AYRu5++yPvL1H1auWZFTh
L+rH9Aa3rDvChZKtPfVetvBsqf0DF0uraGGnyOzaXHvIVYYNWQYgI6YO8e8U3pOP
+qcUb+U22blkhXNo8x48uQkGrLMWO4Ppi5SMMiCsNXPSfpANpZ9E7301WSJdRQLj
XU0E2qmggJ2AwjRGNwIDAQAB
-----END PUBLIC KEY-----'''


def verifyToken(token):
    result = jwt.decode(token, public_key, algorithms='RS256')
    if result['exp'] - int(time.time()) < 0:
        raise Exception('token 已过期，请重新申请')
    if result.get('type', '') != 'SDK':
        raise Exception('token 错误，请使用正确的 token')
    return result
