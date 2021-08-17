import __main__
from datetime import date
from artify import utilities



def checkFileExists(filename):
    return __main__.os.path.exists(filename)

def append_file_content(filename, content):
    fullpath = __main__.os.path.join(__main__.path, filename)
    f = open(fullpath, "a+")
    f.write(content)
    f.close()


def create_file(filename, content):
    fullpath = __main__.os.path.join(__main__.path, filename)
    f = open(fullpath, "w+")
    f.write(content)
    f.close()


def update_changelog():
    chglogfname = "CHANGELOG.md"
    basetext = "# Change Log\n\nAll notable changes to this project will be documented in this file."
    release_date = date.today().strftime("%b-%d-%Y")
    current_version = utilities.get_current_application_version(__main__.path)
    added_list = "User can now login using Google Account"
    changed_list = "Authentication framework was updated from Oauth2 to KeyCloak 14"
    content = "\n\n============================\n\n[{}] - [{}] \n### Added\n- {}\n\n### Changed\n- {}!".format(current_version, release_date, added_list, changed_list)

    if checkFileExists(chglogfname):
        if __main__.debug:
            print("DEBUG: File CHANGELOG.md exist. Updating file")
        append_file_content(chglogfname, content)
    else:
        if __main__.debug:
            print("DEBUG: File CHANGELOG.md does not exist. Creating file")
        create_file(chglogfname, basetext)
        append_file_content(chglogfname, content)


