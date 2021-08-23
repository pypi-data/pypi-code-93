import os
import subprocess
from PyInquirer import prompt

# Commit command
def commit(cfg, args):
  """
  Commit the files
  args:
  -y : don't confirm
  """

  def convert(line):
    """
    Convert line into a tuple of (root folder, filename)
    """
    line = str(line.decode('utf-8'))
    path = line.split(os.sep)
    root = path[0] if len(path) > 0 else ""
    filename = path[-1]
    return (root, filename)

  # run git diff command
  # if changed more than 3 files, list folders instead
  output = subprocess.run(['git', 'diff', '--name-only', 'HEAD'], stdout=subprocess.PIPE).stdout.splitlines()
  changed = list(map(convert, output))

  if not changed:
    print("No files detected")
    return

  # Make a message using the filenames. If its too long,
  # Set the commit title to the root folders, then the commit description to each of the files changed
  message = " ".join([pair[1] for pair in changed])
  if len(message) > 50:
    message = " ".join(set([pair[0] for pair in changed])) + "\n\n" + "\n".join([pair[1] for pair in changed])

  print("Committing with messsage: \n{0}".format(message))

  confirm = [
    {
      'name': 'confirm',
      'message': 'commit?',
      'type': 'confirm',
      'default': True
    }
  ]

  # Prompt for confirmation
  if not args.y and not prompt(confirm)['confirm']:
    return

  # make the commit
  os.system("git commit -am \"{0}\"".format(message))


def sync(cfg, args):
  """
  git pull and git push
  """
  print("Syncing...")

  # Forcefully encrypt the journal
  # print("Encrypting Journal...")
  # encrypt_journal(None)

  os.system("git pull -r && git push")


# Log command
def log(cfg, args):
  os.system(
    "git log --graph --pretty=\"%Cred%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%cr) %C(bold blue)<%an>%Creset\" --abbrev-commit")
