import os
from seckerwiki.util import file_contains_markers, replace_between_markers


"""
Table of contents generator
"""

TOC_START = "<!--BEGIN_TOC-->\n"
TOC_END = "<!--END_TOC-->\n"

def toc(cfg, args):
  """
  Generates a table of contents in every file that has the TOC_START and TOC_END markers.
  """
  
  excluded_dirs = cfg['toc-excluded-dirs']
  count = 0

  for root, dirs, files in os.walk(os.getcwd()):
    # filter out excluded dirs https://stackoverflow.com/questions/19859840/excluding-directories-in-os-walk
    dirs[:] = [d for d in dirs if d not in excluded_dirs]

    # filter to markdown files
    md_files = [file for file in files if file.endswith(".md")]

    for _file in md_files:
      file_path = os.path.join(root, _file)
      if file_contains_markers(file_path, TOC_START, TOC_END):
        toc = generate_toc(root, dirs, files)

        replace_between_markers(file_path, TOC_START, TOC_END, toc)

        count += 1

  print(f"Updated {count} files. Make sure to re-run `foam janitor` to update link compatibility.")

def generate_toc(root, subdirs, files):
  # Generate directory links. My standard is to have a "contents-page" with the same name (lowercased) of the directory it's contained in

  subdir_lines = []
  files_lines = []

  # Generate subdir links
  for subdir in subdirs:
    filename = subdir.lower() + ".md"
    if os.path.isfile(os.path.join(root, subdir, filename)):

      subdir_path = f"./{subdir}/{filename}"
      subdir_lines.append(f"[{subdir}]({subdir_path})")

  # generate file links
  for _file in files:
    if _file.endswith(".md"):
      files_lines.append(f"[{_file.replace('.md', '')}](./{_file})")

  return render_contents(subdir_lines, files_lines)

def render_contents(subdirs, pages):

  subdir_lines="\n".join([f"- {subdir}" for subdir in subdirs])
  pages_lines="\n".join([f"- {page}" for page in pages])

  toc = ""

  if subdirs:
    toc += "Subdirectories:\n"
    toc += subdir_lines + "\n\n"

  if pages:
    toc += "Pages:\n"
    toc += pages_lines + "\n"

  # render page
  return toc