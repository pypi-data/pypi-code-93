class Sequences(object):
    def __init__(self, graph):
        startPoints = []
        endPoints = []
        nameList = graph.getAllNames()

        for name in nameList:
            v = graph.getVertex(name)
            if graph.isStart(v):
                startPoints.append(v)
            if graph.isEnd(v):
                endPoints.append(v)

        starters = [x.name for x in startPoints]
        enders = [x.name for x in endPoints]

        self.allThePaths = []

        for s in starters:
            for e in enders:
                pa = graph.find_all_paths(s, e)
                self.allThePaths = self.allThePaths + pa

    def number(self):
        return len(self.allThePaths)

    def get(self):
        return self.allThePaths
