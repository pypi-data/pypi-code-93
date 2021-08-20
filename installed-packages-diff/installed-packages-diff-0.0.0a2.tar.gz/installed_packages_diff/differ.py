def _filter_diff(diffAB, aExcludes, bExcludes, includeEqual):
  filtered = {}
  for packageName, result in diffAB.items():
    excluded = packageName in aExcludes \
               or packageName in bExcludes \
               or result[0] in aExcludes \
               or result[1] in bExcludes
    if not excluded and (result[0] != result[1] or includeEqual):
      filtered[packageName] = result

  return filtered


def create_diff(listA, listB, *, aExcludes=None, bExcludes=None,
    includeEqual=False):
  aExcludes = aExcludes or []
  bExcludes = bExcludes or []

  mapA = {p.name: p for p in listA}
  mapB = {p.name: p for p in listB}
  diffAB = {}
  for packageName in mapA:
    packageA = mapA[packageName]
    packageB = mapB.get(packageName, None)
    diffAB[packageName] = [packageA.version,
                           packageB.version if packageB else "missing"]

  for packageName in mapB:
    if not packageName in diffAB:
      packageB = mapB[packageName]
      diffAB[packageName] = ["missing", packageB.version]

  return _filter_diff(diffAB, aExcludes, bExcludes, includeEqual)
