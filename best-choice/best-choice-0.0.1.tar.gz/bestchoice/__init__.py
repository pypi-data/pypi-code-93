from itertools import combinations

class Generate:

  table = []
  results = []

  def __init__(self,data):
    self.data = data
    self.start()

  def start(self):
    for x in range(1,len(self.data)+1):
      kit = combinations(self.data, x)
      for y in kit:
        self.__class__.table.append(list(y))
    return self.__class__.table
  
  def list_all(self):
    return self.__class__.table

  def list_results(self,columns):
    vrest = []
    self.columns = columns 
    vdata = self.__class__.table
    self.__class__.results = []
    for x in vdata:
      vlist = str(vdata.index(x))
      for y in range(len(columns)):
        vlist += ','+str(sum(row[columns[y]] for row in x))
      self.__class__.results.append([int(z) for z in vlist.split(',')])
    return self.__class__.results

  def list_best(self,columns,filters):
    self.list_results(columns)
    best = self.__class__.results
    for a,b,c in filters:
      for x in range(len(best)):
        if b == '<':
          best = [item for item in best if item[:][a] < c]
        elif b == '<=':
          best = [item for item in best if item[:][a] <= c]
        elif b == '>':
          best = [item for item in best if item[:][a] > c]
        elif b == '>=':
          best = [item for item in best if item[:][a] >= c]
        elif b == '==':
          best = [item for item in best if item[:][a] == c]
        elif b == '!=':
          best = [item for item in best if item[:][a] != c]
    return best
