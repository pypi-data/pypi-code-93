# data is a list of dict
def max_length(data, key):
    maxVal = 0
    for item in data:
        n = len(str(item[key]))
        if maxVal < n:
            maxVal = n
    return maxVal if maxVal > len(key) else len(key)
