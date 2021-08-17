import math

def gatherInitialRawData(dataForBout, rawData):
  
  rawInitialData = []
  
  for param in rawData:
    if param in ['Heading', 'TailAngle_Raw', 'TailAngle_smoothed', 'Bend_Amplitude']:
      rawInitialData.append([val * (180 / math.pi) for val in dataForBout[param]])
    else:
      rawInitialData.append(dataForBout[param])
  
  return rawInitialData
