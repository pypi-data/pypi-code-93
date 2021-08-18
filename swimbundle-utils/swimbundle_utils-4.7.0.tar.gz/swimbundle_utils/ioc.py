# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import itertools
import re
import ipaddress
import iocextract
from builtins import str
import json
import os
from ioc_finder import find_iocs
import urllib.parse
from ioc_finder import (parse_domain_names,parse_email_addresses,parse_xmpp_addresses,
                        parse_complete_email_addresses,prepare_text,parse_cves,parse_urls,parse_asns,
                        parse_md5s,parse_sha1s,parse_ssdeeps,parse_sha256s,parse_registry_key_paths,
                        parse_tlp_labels,parse_google_adsense_ids,parse_google_analytics_ids,
                        parse_imphashes_,parse_ipv4_addresses,parse_ipv6_addresses,
                        parse_bitcoin_addresses,parse_mac_addresses,parse_user_agents,parse_phone_numbers,
                        parse_sha512s,parse_authentihashes_,ioc_grammars,parse_ipv4_cidrs)

from typing import List,Dict
from pyparsing import ParseResults


# need this here, and to use. Otherwise if the
# IOC_Parser.IOC_TYPES is equal to this, the IOC TYPER
# unit tests will fail. WIll update the IOC TYPER to identity
# the newly added types in a future release.
_IOC_TYPES = ['urls',
              'xmpp_addresses',
              'email_addresses',
              'email_addresses_complete',
              'ipv4_cidrs',
              'imphashes',
              'authentihashes',
              'domains',
              'ipv4s',
              'ipv6s',
              'sha512s',
              'sha256s',
              'sha1s',
              'md5s',
              'ssdeeps',
              'asns',
              'cves',
              'registry_key_paths',
              'google_adsense_publisher_ids',
              'google_analytics_tracker_ids',
              'bitcoin_addresses',
              'monero_addresses',
              'mac_addresses',
              'user_agents',
              'phone_numbers',
              'tlp_labels']



# need to define these locally. Tried importing from ioc finder package itself
# but it won't allow that to occur.
def _remove_items(items: List[str], text: str) -> str:
    """Remove each item from the text."""
    for item in items:
        text = text.replace(item, ' ')
    return text

def _remove_xmpp_local_part(xmpp_addresses: List, text: str) -> str:
    """Remove the local part of each xmpp_address from the text."""
    for address in xmpp_addresses:
        text = text.replace(address.split('@')[0] + '@', ' ')

    return text

def _remove_url_domain_name(urls: List, text) -> str:
    """Remove the domain name of each url from the text."""
    for url in urls:
        parsed_url = ioc_grammars.scheme_less_url.parseString(url)
        text = text.replace(parsed_url.url_authority, ' ')
    return text

def _remove_url_paths(urls: List, text: str) -> str:
    """Remove the path of each url from the text."""
    for url in urls:
        parsed_url = ioc_grammars.scheme_less_url.parseString(url)
        url_path = urllib.parse.unquote_plus(parsed_url.url_path)

        is_cidr_range = parse_ipv4_cidrs(str(url))
        # if the 'url' has a URL path and is not a cidr range, remove the url_path
        if not is_cidr_range and len(url_path) > 1:
            text = text.replace(url_path, ' ')
    return text

def _percent_decode_url(urls: List, text: str) -> str:
    for url in urls:
        text = text.replace(url, urllib.parse.unquote_plus(url))
    return text

def _deduplicate(indicator_list: List) -> List:
    """Deduplicate the list of observables."""
    return list(set(indicator_list))

def _listify(indicator_list: ParseResults) -> List:
    """Convert the multi-dimensional list into a one-dimensional list with empty entries and duplicates removed."""
    return _deduplicate([indicator[0] for indicator in indicator_list if indicator[0]])

def parse_monero_addresses(text):
    """."""
    monero_addresses = ioc_grammars.monero_address.searchString(text)
    return _listify(monero_addresses)


def find_iocs(  # noqa: CCR001 pylint: disable=R0912,R0915
    text: str,
    *,
    parse_domain_from_url: bool = True,
    parse_from_url_path: bool = True,
    parse_domain_from_email_address: bool = True,
    parse_address_from_cidr: bool = True,
    parse_domain_name_from_xmpp_address: bool = True,
    parse_urls_without_scheme: bool = True,
    parse_imphashes: bool = True,
    parse_authentihashes: bool = True,
) -> Dict[str, List]:
    """Find observables in the given text."""
    iocs = dict()

    text = prepare_text(text)
    # keep a copy of the original text - some items should be parsed from the original text
    original_text = text

    # urls
    iocs['urls'] = parse_urls(text, parse_urls_without_scheme=parse_urls_without_scheme)
    if not parse_domain_from_url and not parse_from_url_path:
        text = _remove_items(iocs['urls'], text)
    elif not parse_domain_from_url:
        text = _percent_decode_url(iocs['urls'], text)
        text = _remove_url_domain_name(iocs['urls'], text)
    elif not parse_from_url_path:
        text = _percent_decode_url(iocs['urls'], text)
        text = _remove_url_paths(iocs['urls'], text)
    else:
        text = _percent_decode_url(iocs['urls'], text)

    # xmpp addresses
    iocs['xmpp_addresses'] = parse_xmpp_addresses(text)
    if not parse_domain_name_from_xmpp_address:
        text = _remove_items(iocs['xmpp_addresses'], text)
    # even if we want to parse domain names from the xmpp_address,
    # we don't want them also being caught as email addresses so we'll remove everything before the `@`
    else:
        text = _remove_xmpp_local_part(iocs['xmpp_addresses'], text)

    # complete email addresses
    iocs['email_addresses_complete'] = parse_complete_email_addresses(text)
    # simple email addresses
    iocs['email_addresses'] = parse_email_addresses(text)
    if not parse_domain_from_email_address:
        text = _remove_items(iocs['email_addresses_complete'], text)
        text = _remove_items(iocs['email_addresses'], text)
    # after parsing the email addresses, we need to remove the
    # '[IPv6:' bit from any of the email addresses so that ipv6 addresses are not extraneously parsed
    text = _remove_items(['[IPv6:'], text)

    # cidr ranges
    iocs['ipv4_cidrs'] = parse_ipv4_cidrs(text)
    if not parse_address_from_cidr:
        text = _remove_items(iocs['ipv4_cidrs'], text)

    # remove URLs that are also ipv4_cidrs (see https://github.com/fhightower/ioc-finder/issues/91)
    if parse_urls_without_scheme:
        for cidr in iocs['ipv4_cidrs']:
            if cidr in iocs['urls']:
                iocs['urls'].remove(cidr)

    # file hashes
    if parse_imphashes:
        iocs['imphashes'] = parse_imphashes_(text)
        # remove the imphashes so they are not also parsed as md5s
        text = _remove_items(iocs['imphashes'], text)

    if parse_authentihashes:
        iocs['authentihashes'] = parse_authentihashes_(text)
        # remove the authentihashes so they are not also parsed as sha256s
        text = _remove_items(iocs['authentihashes'], text)

    # domains
    iocs['domains'] = parse_domain_names(text)

    # ip addresses
    iocs['ipv4s'] = parse_ipv4_addresses(text)
    iocs['ipv6s'] = parse_ipv6_addresses(text)

    # file hashes
    iocs['sha512s'] = parse_sha512s(text)
    iocs['sha256s'] = parse_sha256s(text)
    iocs['sha1s'] = parse_sha1s(text)
    iocs['md5s'] = parse_md5s(text)
    iocs['ssdeeps'] = parse_ssdeeps(text)

    # misc
    iocs['asns'] = parse_asns(text)
    iocs['cves'] = parse_cves(original_text)
    iocs['registry_key_paths'] = parse_registry_key_paths(text)
    iocs['google_adsense_publisher_ids'] = parse_google_adsense_ids(text)
    iocs['google_analytics_tracker_ids'] = parse_google_analytics_ids(text)
    iocs['bitcoin_addresses'] = parse_bitcoin_addresses(text)
    iocs['monero_addresses'] = parse_monero_addresses(text)
    iocs['mac_addresses'] = parse_mac_addresses(text)
    iocs['user_agents'] = parse_user_agents(text)
    iocs['phone_numbers'] = parse_phone_numbers(text)
    iocs['tlp_labels'] = parse_tlp_labels(original_text)

    return iocs


class IOCParser(object):

    @staticmethod
    def unravel(value, wrap_chars):
        to_return = []
        for i in range(0, len(wrap_chars)):
            wrapping_char = wrap_chars[i]
            re_str = r"\{start}([^<>\[\]\(\)]*)\{end}".format(start=wrapping_char[0], end=wrapping_char[1])
            match = re.compile(re_str)
            match = match.findall(value)
            if match:
                to_return.extend(match)
            else:
                continue

        to_return.append(value)
        return to_return

    def possible_entries(self, entry):
        # Text that might wrap an IOC, in format <start txt>, <end txt>
        # So for example "(10.20.32.123)" -> "10.20.32.123"

        wrapping_chars = [  # Will be recursed on, so only add static regex
            ("(", ")"),
            ("<", ">"),
            (";", ";"),
            ("[", "]"),
            ("-", "-"),
            ('"', '"')
        ]

        sub_entries = self.unravel(entry, wrapping_chars)

        wrapping_txts = [
            (";", ";"),
            ("href=\"", "\""),
            ("alt=\"", "\""),
            ("<", ">,"),
        ]

        poss = []
        poss.extend(sub_entries)
        poss.append(entry)

        sub_strings = re.split("[<>]", entry)
        poss.extend(sub_strings)

        for start_txt, end_txt in wrapping_txts:
            starts_w = entry.startswith(start_txt)
            ends_w = entry.endswith(end_txt)
            if starts_w:
                poss.append(entry[len(start_txt):])
            if ends_w:
                poss.append(entry[:-len(end_txt)])
            if starts_w and ends_w:
                poss.insert(0, entry[len(start_txt):-len(end_txt)])  # Insert to beginning because of stripping

        return poss

    def parse_iocs(self, text, defang=False, whitelist_regex=''):
        ioc_typer = IOCTyper()
        # emails will often enforce strict line limits, so IOCs can be split in half by a newline.
        # remove all linebreaks to avoid this issue.
        text2 = re.sub("[\n\r]+", "", text)
        text_chunks = set()
        for text_input in [text, text2]:
            split_text = re.split(r"(\n| )", text_input)
            split_text = map(lambda x: x.strip("\r\t\n "), split_text)
            split_text = filter(lambda x: len(x) > 2, split_text)  # Strip out single chars
            text_chunks.update(split_text)

        entries = []

        for entry in text_chunks:
            # Each entry might not be split correctly, try some combinations
            for pos in self.possible_entries(entry):
                typ = ioc_typer.type_ioc(pos)
                # This is catching wrong domains and email addresses.
                # The ioc_finder does a perfect job here so removing it from our custom searches.
                if typ not in ["unknown", "domain", "email"]:
                    entries.append((pos, typ))

        # iocextract can find iocs that have been defanged.  They are refanged and added to the correct type.
        # Patched: iocextract has bug in yara regex for long strings causing exponential back string matches.
        # This chain call is the same as extract_iocs except yara is removed.  We tried doing a timeout on
        # the call that searched for yara, but the timeout wrapper wasn't windows compatible.
        iocs = set(itertools.chain(
            iocextract.extract_urls(text, refang=True, strip=False),
            iocextract.extract_ips(text, refang=True),
            iocextract.extract_emails(text, refang=True),
            iocextract.extract_hashes(text),
        ))

        for ioc in iocs:
            typ = ioc_typer.type_ioc(ioc)
            entries.append((ioc, typ))
            for pos in self.possible_entries(ioc):
                typ = ioc_typer.type_ioc(pos)
                if typ != "unknown":
                    entries.append((pos, typ))

        result = IOCTyper.build_empty_ioc_dict()

        for entry, typ in entries:
            result[typ].append(entry)

        # Append domains from URLs to the domains result
        cleaned_urls = [re.sub("https?(://)?", "", urllib.parse.unquote(u)) for u in result["url"]]  # Strip schema
        cleaned_urls = [re.sub("[/?].*", "", u) for u in cleaned_urls]  # Strip excess /'s

        domain_validator = DomainIOC()
        for cleaned_url in cleaned_urls:
            if domain_validator.run(cleaned_url, check_tld=False):
                result["domain"].append(cleaned_url)

        # compare iocs found using ioc finder
        _find_iocs = dict()

        for key in _IOC_TYPES:
            _find_iocs[key] = []

        # extend
        _found_iocs = find_iocs(text=urllib.parse.unquote(text))

        # combined urls, if found urls from find_ioc are valid
        # by using the ioc typer. Then add valid urls
        url_list = []
        for ioc in _found_iocs['urls']:
            typ = ioc_typer.type_ioc(ioc)
            if typ == "url":
                url_list.append(ioc)
        # add valid urls
        _found_iocs['url'] = url_list

        for key in _IOC_TYPES:
            # Have to fix bug in ioc-finder package for domains. Need to unquote url for it to catch all IOCs
            # According to DeepDive we should not return the unqouted URL for research purposes.
            # Therefore we inherit the single function and pass the unquoted text manually.
            if key == 'domains':
                _found_iocs['domains'] = parse_domain_names(urllib.parse.unquote(text))
            # the main function for find_iocs defangs text and misses an email that has a trailing comma.
            # Both of these bugs have been reported.
            elif key == 'email_addresses':
                _found_iocs['email_addresses'] = parse_email_addresses(text)
            else:
                _find_iocs[key].extend(_found_iocs[key])

        # normalize keys
        _find_iocs['email'] = _found_iocs['email_addresses']
        _find_iocs['domain'] = _found_iocs['domains']
        _find_iocs['sha256'] = _found_iocs['sha256s']
        _find_iocs['sha1'] = _found_iocs['sha1s']
        _find_iocs['md5'] = _found_iocs['md5s']
        _find_iocs['ssdeep'] = _found_iocs['ssdeeps']
        _find_iocs['sha512'] = _found_iocs['sha512s']

        # The reason urls aren't added is because
        # there would be duplicates or very similar entries found
        # i.e. "https://www.secureworks.com/blog/malware-lingers-with-bits",
        #      "https://www.secureworks.com/blog/malware-lingers-with-bits)."

        # remove keys, since they've been normalized and renamed.
        pop_keys = ['ssdeeps', "md5s", 'sha512s', "sha256s", "sha1s",
                    "domains", "urls", "email_addresses",
                    'ipv4s', 'ipv6s']

        for key in _find_iocs.copy().keys():
            if key in pop_keys:
                _find_iocs.pop(key)

        # extend nested lists or dictionaries with nested lists with same key
        for k, v in _find_iocs.items():
            if k in result:
                result[k].extend(v)
            else:
                result[k] = v


        # remove duplicates
        for k, v in result.items():
            result[k] = list(set(v))


        # Clear results based on whitelist
        if whitelist_regex:
            for ioc_typ in IOCTyper.IOC_TYPES:
                ioc_list = []
                for ioc in result[ioc_typ]:
                    if re.findall(whitelist_regex, ioc):
                        pass  # Found match, don't add to list
                    else:
                        ioc_list.append(ioc)
                result[ioc_typ] = ioc_list
        if defang:
            result = self.defang_results(result)
        return result

    @staticmethod
    def defang_results(results):
        defangable = ['domain', 'ipv4_private', 'ipv4_public', 'url']
        new_results = {}
        for key, value in results.items():
            if key in defangable:
                new_value = []
                for ioc in value:
                    new_value.append(iocextract.defang(ioc))
                new_results[key] = new_value
        results.update(new_results)
        return results


class IOCTyper(object):
    # Order of this list determines the detection order, DO NOT CHANGE
    # Add new types to the top of this list
    IOC_TYPES = [
        'ssdeep',
        'sha256',
        'sha1',
        'md5',
        'email',
        'ipv4_public',
        'ipv4_private',
        'ipv6_public',
        'ipv6_private',
        'domain',
        'filename',
        'url',
        'unknown'
    ]

    COMMON_FILETYPES = ['3dm', '3ds', '3g2', '3gp', '7z', 'accdb', 'ai', 'aif', 'apk', 'app', 'asf', 'asp',
                        'aspx', 'avi', 'b', 'bak', 'bat', 'bin', 'bmp', 'c', 'cab', 'cbr', 'cer', 'cfg',
                        'cfm', 'cgi', 'class', 'cpl', 'cpp', 'crdownload', 'crx', 'cs', 'csr', 'css',
                        'csv', 'cue', 'cur', 'dat', 'db', 'dbf', 'dcr', 'dds', 'deb', 'dem', 'deskthemepack',
                        'dll', 'dmg', 'dmp', 'doc', 'docm', 'docx', 'download', 'drv', 'dtd', 'dwg', 'dxf',
                        'eps', 'exe', 'fla', 'flv', 'fnt', 'fon', 'gadget', 'gam', 'ged', 'gif', 'gpx', 'gz',
                        'h', 'hqx', 'htm', 'html', 'icns', 'ico', 'ics', 'iff', 'indd', 'ini', 'iso', 'jar',
                        'java', 'jpeg', 'jpg', 'js', 'json', 'jsp', 'key', 'keychain', 'kml', 'kmz', 'lnk',
                        'log', 'lua', 'm', 'm3u', 'm4a', 'm4v', 'max', 'mdb', 'mdf', 'mid', 'mim', 'mov',
                        'mp3', 'mp4', 'mpa', 'mpeg', 'mpg', 'msg', 'msi', 'nes', 'obj', 'odt', 'otf',
                        'pages', 'part', 'pct', 'pdb', 'pdf', 'php', 'pkg', 'pl', 'plugin', 'png', 'pps',
                        'ppt', 'pptx', 'prf', 'ps', 'psd', 'pspimage', 'py', 'rar', 'rm', 'rom', 'rpm',
                        'rss', 'rtf', 'sav', 'sdf', 'sh', 'sitx', 'sln', 'sql', 'srt', 'svg', 'swf', 'swift',
                        'sys', 'tar', 'tax2016', 'tax2017', 'tex', 'tga', 'thm', 'tif', 'tiff', 'tmp',
                        'toast', 'torrent', 'ttf', 'txt', 'uue', 'vb', 'vcd', 'vcf', 'vcxproj', 'vob', 'wav',
                        'wma', 'wmv', 'wpd', 'wps', 'wsf', 'xcodeproj', 'xhtml', 'xlr', 'xls', 'xlsx',
                        'xlsm', 'xml', 'yuv', 'zip', 'zipx', 'webm', 'flac', 'numbers']

    URL_REGEX_COMPILED = re.compile(r"""^                                    #beginning of line
(?P<proto>https?:\/\/)               #protocol                http://
(
(?P<domain>(([\u007E-\uFFFFFF\w-]+[.])+[\u007E-\uFFFFFF\w-]{2,}))
|
(?P<ipv4>(?:(?:\b|\.)(?:2(?:5[0-5]|[0-4]\d)|1?\d?\d)){4})
|
(\[?
(?P<ipv6>(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])))
\]?)
)
(?P<port>:\d{1,5})?
\/?                                    #domain                    www.google.co.uk
(?P<directory>(?<=\/)([{}%|~\/!?A-Za-z0-9_.-]+)(?=\/))?                    #directory    /var/www/html/apps
\/?                                    #final directory slash    /
(?P<filename>([^?<>"]+))?                #filename                index.php
                                    #query marker            ?
(?P<query>\?[^\s"<>]*)?                        #query text                cmd=login_submit&id=1#cnx=2.123
$                                    #end of line""", re.VERBOSE | re.UNICODE)

    FILE_REGEX = r'^(?!.*[\\/:*"<>|])[\w !@#$%^&*()+=\[\]{}\'"-]+(\.[\w -]+)?$'

    def __init__(self):
        self.ioc_patterns = {
            'ipv4_public': IPv4PublicIOC(),
            'ipv4_private': IPv4PrivateIOC(),
            'ipv6_public': IPv6PublicIOC(),
            'ipv6_private': IPv6PrivateIOC(),

            'url': URLIOC(self),
            'email': RegexIOC(r'^[\w%+.-]+@[A-Za-z0-9.-]+\.[a-z]{2,}$'),
            'md5': RegexIOC(r'^[a-fA-F0-9]{32}$'),
            'sha1': RegexIOC(r'^[a-fA-F0-9]{40}$'),
            'sha256': RegexIOC(r'^[a-fA-F0-9]{64}$'),
            'ssdeep': RegexIOC(r'^([1-9]\d*)(?!:\d\d($|:)):([\w+0-9\/]+):([\w+0-9\/]+)$'),
            'filename': FilenameIOC(IOCTyper.FILE_REGEX),
            'domain': DomainIOC(),
            'unknown': AnyIOC()
        }

        self.tld_patterns = {
            'validSLD': re.compile(r'^[a-z0-9-]+$', re.IGNORECASE),
            'validTLD': re.compile(r'^[a-z]{2,64}$'),
            'tld': re.compile(r'^\.[a-z]{2,}$')
        }

    @staticmethod
    def build_empty_ioc_dict():
        iocs = {}
        for ioc in IOCTyper.IOC_TYPES:
            iocs[ioc] = []

        return iocs

    def is_ip(self, value):
        versions = ["4", "6"]
        p_levels = ["public", "private"]
        for v in versions:
            for p_level in p_levels:
                if self.ioc_patterns["ipv{}_{}".format(v, p_level)].run(value):
                    return True
        return False

    def type_ioc(self, ioc):
        for pat_name in IOCTyper.IOC_TYPES:
            if self.ioc_patterns[pat_name].run(ioc):
                return pat_name


class IOCObj(object):
    def run(self, value):
        raise NotImplementedError


class AnyIOC(IOCObj):  # Always returns true
    def run(self, value):
        return True


class RegexIOC(object):
    def __init__(self, regex, re_flags=0):
        """
        :param regex: Regex String to match a value against
        """
        self.regex = re.compile(regex, re_flags)

    def run(self, value):
        return bool(self.regex.search(value))


class URLIOC(IOCObj):
    def __init__(self, typer):
        self.typer = typer

    def run(self, value):
        match = IOCTyper.URL_REGEX_COMPILED.search(value)
        if match and len(match.group()) == len(value):
            return True
        return False


class FilenameIOC(IOCObj):
    def __init__(self, regex):
        self.regex = re.compile(regex)

    def run(self, value):
        match = self.regex.search(value)
        if match and self.is_filename(match.group()):
            return True
        return False

    @staticmethod
    def is_filename(fn):

        extension = ".".join(fn.split(".")[-1:])
        if extension == fn:
            return False

        if extension in IOCTyper.COMMON_FILETYPES:
            return True
        else:
            return False


class DomainIOC(IOCObj):
    NUMERIC_NOT_A_DOMAIN = numeric_only = re.compile(r'^([0-9]+\.)+[0-9]+$')
    GENERAL_DOMAIN = re.compile(r'(([\u007E-\uFFFFFF\w-]+[.])+[\u007E-\uFFFFFF\w-]{2,})', re.UNICODE)
    with open(os.path.join(os.path.dirname(__file__), 'data/tld_list.json'), 'r') as f:
        COMMON_TLDS = json.load(f)

    def ends_with_tld(self, domain):
        for tld in self.COMMON_TLDS:
            if domain.split('.')[-1].lower() == tld.lower():
                return True
        return False

    def run(self, value, check_tld=True):
        value = urllib.parse.unquote(value)
        match = self.GENERAL_DOMAIN.search(value)
        if match and len(match.group()) == len(value):
            bad_match = self.NUMERIC_NOT_A_DOMAIN.search(value)
            if not bad_match or len(bad_match.group()) != len(value):
                if check_tld:
                    if self.ends_with_tld(value):
                        return True
                else:
                    return True

        return False


class IPIOC(IOCObj):
    def privacy_valid(self, value):
        # Return true if the value is private otherwise false if public
        ipaddr = ipaddress.ip_address(str(value))
        if ipaddr.is_private == self.is_private():
            return True
        else:
            return False

    def is_private(self):
        # Return true if the ioc typer is for private ips only else false for public
        raise NotImplementedError

    def ip_ver(self):
        # Return ip version, either 4 or 6
        raise NotImplementedError

    def ioc_name(self):
        # Returns one of ipv6_private, ipv6_public, ipv4_public, ipv4_private
        name = "ipv{}".format(self.ip_ver())
        name += "_{}".format("private" if self.is_private() else "public")
        return name

    def get_regex(self):
        raise NotImplementedError

    def __init__(self):
        self.regex = re.compile(self.get_regex())

    def run(self, value):
        match = self.regex.search(value)
        result = False

        try:
            ipaddress.ip_address(str(value))  # Try parsing IP
        except ValueError:
            return False

        if match:
            result = True and self.privacy_valid(value)

        return result


class IPv4PublicIOC(IPIOC):
    def get_regex(self):
        return r'^(?:(?:\b|\.)(?:2(?:5[0-5]|[0-4]\d)|1?\d?\d)){4}$'

    # Keeping regex in case it becomes useful
    #         # Class A
    #         r'^10\.(2([0-5]{2})|2[0-9]{1}|1?\d?\d)\.(2([0-5]{2})|2[0-9]{1}|1?\d?\d)\.(2([0-5]{2})|2[0-9]{1}|1?\d?\d)$',
    #         # Class B
    #         r'^172\.(3([01])|1[6-9]|2\d)\.(2([0-5]{2})|2[0-9]{1}|1?\d?\d)\.(2([0-5]{2})|2[0-9]{1}|1?\d?\d)$',
    #         # Class C
    #         r'^192\.168\.(2([0-5]{2})|2[0-9]{1}|1?\d?\d)\.(2([0-5]{2})|2[0-9]{1}|1?\d?\d)$',
    #     ]

    def is_private(self):
        return False

    def ip_ver(self):
        return "4"


class IPv4PrivateIOC(IPv4PublicIOC):
    def is_private(self):
        return True


class IPv6PublicIOC(IPIOC):
    def get_regex(self):
        return r'^(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))$'

    def is_private(self):
        return False

    def ip_ver(self):
        return "6"


class IPv6PrivateIOC(IPv6PublicIOC):
    def is_private(self):
        return True
