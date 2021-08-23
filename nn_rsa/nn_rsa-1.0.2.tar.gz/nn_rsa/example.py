import nn_rsa

#生成公钥和私钥
#nn_rsa.NnRsa.create_key()

#传入文件名前缀，生成公钥和私钥存到文件里面
# nn_rsa.NnRsa.create_key(file_name_prefix='sky')


public_key = """
-----BEGIN RSA PUBLIC KEY-----
MIGJAoGBAL0964+AlfwZfe2u2fa9xyanYz+qzQHZrd0PWOefzWc0t7TZHTzsyexC
E44urJhd02Gwju1FeuS5TBSP27UyWOxbORQWbdHl3qjXZJ24L+1eA/CIUzOeJNvG
0syAWk6L887faMa9e0jkL8P3B0jsVkB7Y9d8q8vQolsHvvj5DS/PAgMBAAE=
-----END RSA PUBLIC KEY-----
"""
private_key = """
-----BEGIN RSA PRIVATE KEY-----
MIICYAIBAAKBgQC9PeuPgJX8GX3trtn2vccmp2M/qs0B2a3dD1jnn81nNLe02R08
7MnsQhOOLqyYXdNhsI7tRXrkuUwUj9u1MljsWzkUFm3R5d6o12SduC/tXgPwiFMz
niTbxtLMgFpOi/PO32jGvXtI5C/D9wdI7FZAe2PXfKvL0KJbB774+Q0vzwIDAQAB
AoGAUXjyDFMIv4NeEtEfZ7omnj6cXRG0tyI3Vx+/X+ENtmwc1xBOJSewezWrY6A2
kFZ8pec0cXRjR0t7NLMGSPXahxaQv6wU58rOeLhjCxhyN9bh+0jechbayjcOFq0A
CqeWVoLTMCJoKM4pqhTrMdZByQktLGwXRXhRq01Ja963W+kCRQDDSTwNi5NRdyny
bHPh2h+NsPAub0XlLkluiN6Vv0MGGg/nNyYBic2ZvMulBkACN7Gw/Jat54OfotWU
m23apdkrRhK9XQI9APgToSxk9G9ERr/Y+xVhnvXmY1dgOak3+hhugKCiho8JRrEw
j9uFel3VjGZ9Ri4kcOPWp5k8R4rl13WjGwJEP3LS5R+9LJHH+jDMccv5xoJ/dsbG
cdDZIOWtVAABWcEr+5aKbaOFPnb9v09Jiq7nt7ZJipUWyc4REKhzR7/s0EeDHS0C
PG53VzrMjagKUDLXrR7dRIqdF7ltyN9YZM6CTla5aI/DAq6eQEDxVAb6s7VjrV+Y
rIhYKnNqyzTHmkTw5wJFALDOgGTdgDQO7evWPY50gngczYP9MnEsBxHpBxdoPUqg
Thpj6P3Edw6iB1WzXxQqvho+bVTFaeaI0kvZk9UiVdGr+Mwm
-----END RSA PRIVATE KEY-----
"""

#加密/解密一起

# t1 = nn_rsa.NnRsa(private_key=private_key, public_key=public_key)
# miwen = t1.encrypt("森哥说多少个山东高速感受感受是的感受到公司给的谁告诉告诉告诉哥哥哥42山东高速")  # 加密
# mingwen = t1.decrypt(miwen)  # 解密

#只解密
# t2 = nn_rsa.NnRsa(private_key=private_key)
# miwen = "LrcQVAgjA7yD6+Kvh50ztWlLoefBVOBDrcpaL9uStsjAphqvPXncVHVktPkzuILkMnteutGFMNcwgRdy3ZifcC5rRtlbeJI94w7cSVgN1anU9O1Qx0du8A4r0TrvSQUTYhrz/L3+YhC0P6UmAkpRfM7WHOL8Okzs6rfPNhhAfJY="
# mingwen = t2.decrypt(miwen)  # 解密

#只加密
# t3 = nn_rsa.NnRsa(public_key=public_key)
# mingwen = "加密测试"
# miwen = t3.encrypt(mingwen)  # 加密



