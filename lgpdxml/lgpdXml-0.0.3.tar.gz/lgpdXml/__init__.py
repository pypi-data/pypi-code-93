def find(text,tagIni,tagEnd):
  ini = 0
  end = 0
  val = []
  for x in range(text.count(tagIni)):
    if  x == 0:
      ini = text.find(tagIni) + len(tagIni)
      end = text.find(tagEnd,ini)
      val.append(text[ini:end])
    else:
      ini = text.find(tagIni,ini) + len(tagIni)
      end = text.find(tagEnd,ini)
      val.append(text[ini:end])

  if len(val) > 0:
    return val
  elif len(val) == 1:
    return val[0]
  else:
    pass

def replace(text,newtext,tagIni,oldtext,tagEnd):
  return text.replace(tagIni+oldtext+tagEnd,tagIni+newtext+tagEnd)
