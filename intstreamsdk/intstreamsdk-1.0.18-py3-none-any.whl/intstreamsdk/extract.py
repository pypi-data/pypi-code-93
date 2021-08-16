import iocextract
import tldextract


def extract_urls(text):
    text = text.replace(",", ", ")
    return iocextract.extract_urls(text, refang=True)


def extract_domains(text, tld_file=None):
    """
    #todo(aj) add param to point at tld file
    :param text:
    :return:
    """
    domains = []
    text = text.replace(",", ", ")
    # extract urls.
    urls = iocextract.extract_urls(text, refang=True)
    urls_no_refang = iocextract.extract_urls(text)
    # extract domains from urls
    for i in urls:
        ext = tldextract.extract(i)
        if ext[2] != "":
            rejoin = '.'.join(ext[:2])
            domains.append(rejoin + "." + ext[2])
    # remove urls
    for i in urls_no_refang:
        text.replace(i, " ")
    # remove www.
    final = []
    for i in domains:
        if i[0:4] == "www.":
            i = i[4:]
        final.append(i)
    return final


def extract_ipv4(text):
    return [i for i in iocextract.extract_ipv4s(text, refang=True)]


def extract_ipv6(text):
    return [i for i in iocextract.extract_ipv6s(text)]


def extract_md5(text):
    return [i for i in iocextract.extract_md5_hashes(text)]


def extract_emails(text):
    return [i for i in iocextract.extract_emails(text, refang=True)]


def extract_sha1(text):
    return [i for i in iocextract.extract_sha1_hashes(text)]


def extract_sha256(text):
    return [i for i in iocextract.extract_sha256_hashes(text)]


def extract_all(text):
    data = {}
    data["sha256"] = [i for i in extract_sha256(text)]
    data["sha1"] = [i for i in extract_sha1(text)]
    data["md5"] = [i for i in extract_md5(text)]
    data["ipv6"] = [i for i in extract_ipv6(text)]
    data["ipv4"] = [i for i in extract_ipv4(text)]
    data["domain"] = [i for i in extract_domains(text)]
    data["email"] = [i for i in extract_emails(text)]
    data["url"] = [i for i in extract_urls(text)]
    return data



