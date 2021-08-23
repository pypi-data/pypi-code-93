def print_diff(serverA, serverB, installed_packages_diff, *, file=None):
  print(f"\n= {serverA} {serverB} =", file=file)
  for (packageName, versionA, versionB) in installed_packages_diff:
    print(f"{packageName:40s} {versionA:40s} {versionB:40s}",
          file=file)
