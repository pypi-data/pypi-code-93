from tracardi_key_counter.service.key_counter import KeyCounter

c = KeyCounter({"d": 1})
c.count('a')
c.count('b')
c.count(['a', 'c'])

print(c.counts)
