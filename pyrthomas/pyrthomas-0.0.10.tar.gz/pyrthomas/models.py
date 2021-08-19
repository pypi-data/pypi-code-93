class Node(object):
    min = 0
    max = 0
    id = ''

    def __init__(self, node_id, node_min=0, node_max=0):
        self.id = node_id
        self.min = node_min
        self.max = node_max


class Edge(object):
    source = ''
    target = ''
    weight = 0

    def __init__(self, source, target, weight):
        self.target = target
        self.source = source
        self.weight = weight
