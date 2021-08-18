import nltkma

def test_iterating_returns_an_iterator_ordered_by_frequency():
    samples = ['one', 'two', 'two']
    distribution = nltkma.FreqDist(samples)
    assert list(distribution) == ['two', 'one']
