import os
import subprocess
from seckerwiki.util import bcolors

def stats(cfg, args):
  """
  Print some useless/useful information about the wiki, for showing off purposes
  """

  commit_count = int(subprocess.check_output(['git', 'rev-list', '--all', '--count']))

  loc_map = {}
  
  for root, dirs, files in os.walk(os.getcwd()):
    for _file in [f for f in files if f.endswith(".md")]:
      path = os.path.join(root, _file)
      with open(path, 'r') as f_in:
        loc_map[path] = sum(1 for line in f_in if line.strip())

  total_lines = sum(loc_map.values())
  largest_files = "\n".join(f"    {f}" for f in sorted(loc_map, key=loc_map.get, reverse=True)[:3])

  output = f"""
{bcolors.BOLD}Wiki Stats:{bcolors.ENDC}
  {bcolors.OKGREEN}Commits made: {bcolors.ENDC} {commit_count}
  {bcolors.OKGREEN}Total Lines: {bcolors.ENDC} {total_lines:,}
  {bcolors.OKGREEN}Largest files: {bcolors.ENDC} 
{largest_files}
  """

  print(output)