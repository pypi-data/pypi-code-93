import os
from datetime import date
import sys
import getpass

from seckerwiki.util import bcolors, get_journal_key

def journal(cfg, args):
  if args.encrypt:
    encrypt_journal(cfg, args)
  elif args.decrypt:
    decrypt_journal(cfg, args)
  else:
    generate_note(cfg, args)


def generate_note(cfg, args):
  """
  Generate an empty note
  """
  today = date.today().isoformat()
  filename = '{0}.md'.format(today)
  text = '# Encrypted Note -  {0}\n\n - '.format(today)

  path = os.path.join(cfg['encrypted-journal-path'], filename)

  with open(path, 'a') as f:
    f.write(text)
    print("Generated Journal Entry: ", path)

def encrypt_journal(cfg, args):
  journal_dir = os.path.join(os.getcwd(), cfg['encrypted-journal-path'])

  # check if journal path exists
  if not os.path.isdir(journal_dir):
    print("Journal directory not found: {0}".format(journal_dir))
    return

  print("Encrypting Journal Entries...")
  for root, dirs, files in os.walk(journal_dir):
    for file in files:
      # only encrypt markdown files
      if not file.endswith(".md"):
        print("Skipping: {0}{1}{2}".format(bcolors.OKBLUE, file, bcolors.ENDC))
        continue

      print("Encrypting: {0}{1}{2}".format(bcolors.OKGREEN, file, bcolors.ENDC))
      os.system(
        "gpg -c --armor --batch --passphrase {0} {1}".format(get_journal_key(), os.path.join(root, file)))
      # delete the markdown file
      os.remove(os.path.join(root, file))


def decrypt_journal(cfg, args):
  path = os.path.join(os.getcwd(), cfg['encrypted-journal-path'], args.decrypt)

  # check if entry path exists
  if not os.path.isfile(path):
    print("Journal entry not found: {0}".format(path))
    return

  print("Decrypting Journal Entry: {0}{1}{2}".format(bcolors.OKGREEN, path, bcolors.ENDC), file=sys.stderr)
  return_value = os.system("gpg -d --armor --batch --passphrase {0} {1}".format(get_journal_key(), path))

  if (return_value >> 8) != 0:
    # decryption failed, ask for password
    password = getpass.getpass(prompt="Decryption failed. Manually enter password: ")

    os.system("gpg -d --armor --batch --passphrase {0} {1}".format(password, path))