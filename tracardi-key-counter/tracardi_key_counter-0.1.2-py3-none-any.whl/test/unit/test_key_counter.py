from tracardi_key_counter.service.key_counter import KeyCounter


def test_key_counter():
    c = KeyCounter({"d": 1})
    c.count('a')
    c.count('b')
    c.count(['a', 'c'])

    result = c.counts

    assert result == {'d': 1, 'a': 2, 'b': 1, 'c': 1}
