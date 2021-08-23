import time
from pubsub import PubSub

c = {}

# begin
p = PubSub(c)
publisher = p.pub()

# xpub = p.create_topic('test_001')
# print(xpub)
# xsub = p.create_subscription('test_001', 'test_sub_001')
# print(xsub)
3

pid = p.send(
    publisher, {
        'topic': 'test001',
        'namespace': 'auth',
        'subname': 'auth_register',
        'delay': 1,
        'data': {
            'fullname': 'mas joko',
            'email': 'panas@gmail.com'
        }
    })
print('send pubsub:', pid)