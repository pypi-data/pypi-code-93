def _filter_diff(diffAB: list, aExcludes, bExcludes, includeEqual):
  filtered = []
  for (packageName, versionA, versionB) in diffAB:
    excluded = packageName in aExcludes \
               or packageName in bExcludes \
               or versionA in aExcludes \
               or versionB in bExcludes
    if not excluded and (versionA != versionB or includeEqual):
      filtered.append((packageName, versionA, versionB))

  return filtered


def _to_package_map(packageList):
  packageMap = {}
  for package in packageList:
    versions = packageMap.get(package.name, [])
    versions.append(package.version)
    packageMap[package.name] = versions
  return packageMap


def create_diff(listA, listB, *, aExcludes=None, bExcludes=None,
                includeEqual=False):
  aExcludes = aExcludes or []
  bExcludes = bExcludes or []

  mapA = _to_package_map(listA)
  mapB = _to_package_map(listB)
  diff = []
  for packageName in mapA:
    versionsA = mapA[packageName]
    versionsB = mapB.get(packageName, [])
    if len(versionsA) == 1 and len(versionsB):
      diff.append((packageName, versionsA[0], versionsB[0]))
    else:
      for versionA in versionsA:
        if versionA in versionsB:
          diff.append((packageName, versionA, versionA))
          versionsB.remove(versionA)
        elif not versionA in versionsB:
          diff.append((packageName, versionA, "missing"))
      for versionB in versionsB:
        if not versionB in versionsA:
          diff.append((packageName, "missing", versionB))
  for packageName in mapB:
    if packageName not in mapA:
      for versionB in mapB[packageName]:
        diff.append((packageName, "missing", versionB))

  return _filter_diff(diff, aExcludes, bExcludes, includeEqual)
