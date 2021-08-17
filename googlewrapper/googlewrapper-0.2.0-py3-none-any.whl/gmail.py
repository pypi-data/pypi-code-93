import smtplib
from email.mime.text import MIMEText
from pathlib import Path


def email(subject, message, sender, config_file):
    recp = pull_recp()
    # check config file
    if "email" not in config_file.sections():
        raise Exception("Verify 'email' is a section in your config file")
    send(subject, message, recp, sender, config_file)


def send(subject, message, recipients, sender, config_file):
    """
    Sends an email using a gmail account

    Authenticate through a config file you will need an email section
    with then an email and pwd element

    ::Variables::

    subject: str: subject of email message

    message: list: the body of the email,
                    spaces each list element on a new line

    recipients: list: emails that to receive the email

    sender: str: formated as email

    config_file: config file formatted as:

        {'email':
         { 'email' : 'example@email.com', 'pwd' : password123 }
         }

        create this config file using
        configparser or make_config (custom module)
        and pass it in to authenticate
        it is recommended to use an APP PASSWORD found here:
            https://myaccount.google.com/security

    1) Create the body of the message
    2) Read in the credentials
    3) Set up the smtp connnection and login
    4) Send and close the connection
    """
    # 1
    email_txt = MIMEText("\n".join(message))
    email_txt["Subject"] = subject
    email_txt["From"] = sender
    email_txt["To"] = "\n".join(recipients)

    # 2
    email = config_file["email"]["email"]
    pwd = config_file["email"]["pwd"]

    # 3
    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.ehlo()
    server.login(email, pwd)

    # 4
    server.sendmail(sender, recipients, email_txt.as_string())
    server.close()


def pull_recp(file_path="recipients.txt"):
    """
    pulls the recipients of the email from the given filepath
    defaults to recipients1.txt
    """
    rpath = Path(file_path)
    if rpath.exists():
        rec = rpath.read_text()
    else:
        rpath.touch()
        rec = add_recp(file_path)

    if "\n" in rec:
        return rec.split("\n")
    elif isinstance(rec, str):
        return [rec]


def add_recp(file_path="recipients.txt"):
    rpath = Path(file_path)
    rec = rpath.read_text()
    if rec != "":
        print("Current Recipients")
        for x in rec.split("\n"):
            print(x)

    while True:
        rec += input("Email: ") + "\n"
        if (not rec) or rec == "":
            break
        more = input("Another Email [y/n]: ")
        if (not more) or more[0].lower() != "y":
            break

    rpath.write_text(rec[:-1])
    return rec


def example():
    from custompython.make_config import read

    def do_something():
        pass

    try:
        do_something()
        msg = "SUCCESS"
    except ValueError:
        msg = "ERROR"
    config = read()
    send("SOMETHING TEST", [msg], "example@email.com", "sender@email.com", config)
