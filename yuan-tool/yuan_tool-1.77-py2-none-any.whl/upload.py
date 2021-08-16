import re
import json
import requests
import urllib.parse
import base64
import sys
import hashlib
from .difinition import GITHUB_REPORT_OAUTH_TOKEN


def dataToStdout(data, bold=False):
    """
    Writes text to the stdout (console) stream
    """

    sys.stdout.write(data)

    try:
        sys.stdout.flush()
    except IOError:
        pass

    return


def createGithubIssue(errMsg, excMsg):
    _ = re.sub(r"'[^']+'", "''", excMsg)
    _ = re.sub(r"\s+line \d+", "", _)
    _ = re.sub(r'File ".+?/(\w+\.py)', r"\g<1>", _)
    _ = re.sub(r".+\Z", "", _)
    _ = re.sub(r"(Unicode[^:]*Error:).+", r"\g<1>", _)
    _ = re.sub(r"= _", "= ", _)
    errMsg = re.sub("cookie: .*", 'cookie: *', errMsg, flags=re.I | re.S)

    key = hashlib.md5(_.encode()).hexdigest()[:8]

    msg = "\ndo you want to automatically create a new (anonymized) issue "
    msg += "with the unhandled exception information at "
    msg += "the official Github repository? [y/N] "
    try:
        choice = input(msg)
    except:
        choice = 'n'
    if choice.lower() != 'y':
        return False

    try:
        req = requests.get("https://api.github.com/search/issues?q={}".format(
            urllib.parse.quote("repo:w-digital-scanner/w13scan Unhandled exception (#{})".format(key))))
    except Exception as e:
        return False
    _ = json.loads(req.text)
    try:
        duplicate = _["total_count"] > 0
        closed = duplicate and _["items"][0]["state"] == "closed"
        if duplicate:
            warnMsg = "issue seems to be already reported"
            if closed:
                warnMsg += " and resolved. Please update to the latest "
            dataToStdout('\r' + "[x] {}".format(warnMsg) + '\n\r')
            return False
    except KeyError:
        return False
    data = {
        "title": "Unhandled exception (#{})".format(key),
        "body": "```\n%s\n```\n```\n%s\n```" % (errMsg, excMsg),
        "labels": ["bug"]
    }

    headers = {
        "Authorization": "token {}".format(base64.b64decode(GITHUB_REPORT_OAUTH_TOKEN.encode()).decode())
    }
    try:
        r = requests.post("https://api.github.com/repos/w-digital-scanner/w13scan/issues", data=json.dumps(data),
                          headers=headers)
    except Exception as e:
        return False
    issueUrl = re.search(r"https://github\.com/w-digital-scanner/w13scan/issues/\d+", r.text)
    if issueUrl:
        infoMsg = "created Github issue can been found at the address '%s'" % issueUrl.group(0)
        dataToStdout('\r' + "[*] {}".format(infoMsg) + '\n\r')
        return True
    return False