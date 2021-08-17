from bs4 import BeautifulSoup, Comment
from collections import Counter
import pyap
import re
import requests
from urllib.parse import urljoin

headers = {"User-Agent": "Mozilla/5.0"}


def visiableText(page):
    soup = BeautifulSoup(page, 'lxml')
    comm = soup.findAll(text=lambda text: isinstance(text, Comment))
    [c.extract() for c in comm]
    alltags = soup.findAll(text=True)
    visable_tags = [t for t in alltags if t.parent.name not in
                    ['style', 'script', 'script', 'img', 'head', 'title',
                        'meta', 'link', 'footer', 'base', 'applet', 'iframe', 'embed',
                        'nodembed', 'object', 'param', 'source', '[document]']]
    visible = '\n'.join([re.sub(r'[\t/]+', ' ', t) for t in visable_tags])
    visible = re.sub(r' +\n', '\n', visible)
    visible = re.sub(r'\n+', '\n', visible)
    return re.sub(r' +', ' ', visible)


def toDomain(link):
    return (re.sub(r'^(https?://)?(www\d?\.)?', '', link).split('/')+[''])[0].strip()


def parse(page, domain=''):
    result = {
        'title': '',
        'corpName': '',
        'contactLink': '',
        'aboutLink': '',
        'email': '',
        'phone': '',
        'mainAddress': '',
        'addresses': [],
        'facebook': '',
        'twitter': '',
        'instagram': '',
        'linkedin': '',
        'city': '',
        'region': '',
        'country': '',
        'postalCode': '',
        'addressLine': '',
        'meta': '',
        'innerLinks':'',
        'homepageText':'',
        'contactText': '',
        'aboutText': '',
        'innerLinksNum':0
    }
    soup = BeautifulSoup(page, 'lxml')
    vis = visiableText(page)
    result['homepageText'] = vis
    meta = soup.findAll('meta', {"name": "description", "content": True})
    if meta:
        result['meta'] = meta[0]['content']

    addresses = pyap.parse(vis, country='CA')
    addresses += pyap.parse(vis, country='US')
    addresses = [a for a in addresses if not re.findall(
        r'\band\b', str(a), re.I) and not re.findall(r'\bis\b', str(a), re.I)]
    addressesNoAnd = [a for a in addresses if not re.findall(
        r'\band\b', str(a), re.I)]
    if len(addressesNoAnd) > 1:
        addresses = addressesNoAnd
    allLinks = [s.get('href') for s in soup.select('a[href]')]
    allLinks = [s for s in allLinks if 'javascript' not in s and 'void' not in s]
    if allLinks:
        for social in ['facebook', 'twitter', 'instagram', 'linkedin']:
            result[social] = ([l for l in allLinks if social in l]+[''])[0]
        if not domain:
            domain = Counter([toDomain(
                l) for l in allLinks if 'facebook' not in l and 'twitter' not in l and 'linkedin' not in l]).most_common(1)[0][0]
        else:
            domain = toDomain(domain)

        # innerLinks = [f'http://{domain}'+s if s.startswith('/') else s for s in allLinks if s.startswith('/') or domain in s]
        innerLinks = [urljoin(
            f'http://{domain}', s) if 'http' not in s else s for s in allLinks if 'http' not in s or domain in s]
        result['contactLink'] = ([l for l in innerLinks if 'contact' in l.lower(
        ) or 'contato' in l.lower() or 'kontakt' in l.lower() or 'location' in l.lower()] + [''])[0]
        result['aboutLink'] = (
            [l for l in innerLinks if 'about' in l.lower()] + [''])[0]
        result['innerLinks'] = ';'.join(innerLinks)
        result['innerLinksNum'] = len(innerLinks)

    result['title'] = soup.find('title').text.replace(
        '\n', '').strip() if soup.find('title') else ''
    namepattern = r'\W?'.join([l for l in domain.split('.')[0]])

    result['email'] = ';'.join(set(re.findall(
        r'([a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+)', vis))).lower()
    result['phone'] = ';'.join(set(re.findall(
        r'(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})', vis)))

    if not addresses and result['aboutLink']:
        try:
            res = requests.get(result['aboutLink'],
                               timeout=15, headers=headers)
            resvis = visiableText(res.content)
            result['aboutText'] = resvis
            addresses = pyap.parse(resvis, country='CA')
            addresses += pyap.parse(resvis, country='US')
            addresses = [a for a in addresses if not re.findall(r'\band\b', str(a), re.I) and not re.findall(r'\bis\b', str(a), re.I)]
            addressesNoAnd = [a for a in addresses if not re.findall(
                r'\band\b', str(a), re.I)]
            if len(addressesNoAnd) > 1:
                addresses = addressesNoAnd
        except Exception as e:
            pass
    if not addresses and result['contactLink']:
        try:
            res = requests.get(result['contactLink'],
                               timeout=20, headers=headers)
            resvis = visiableText(res.content)
            result['contactText'] = resvis
            addresses = pyap.parse(resvis, country='CA')
            addresses += pyap.parse(resvis, country='US')
            addresses = [a for a in addresses if not re.findall(r'\band\b', str(a), re.I) and not re.findall(r'\bis\b', str(a), re.I)]

            addressesNoAnd = [a for a in addresses if not re.findall(
                r'\band\b', str(a), re.I)]
            if len(addressesNoAnd) > 1:
                addresses = addressesNoAnd
        except Exception as e:
            pass
    names = []
    if result['title'] and namepattern:
        try:
            names = re.findall(namepattern, result['title'], re.I)
        except:
            pass
    elif result['aboutLink'] and namepattern:
        try:
            aboutres = requests.get(
                result['aboutLink'], timeout=15, headers=headers)
            aboutvis = visiableText(aboutres.content)
            names = re.findall(namepattern, aboutvis, re.I)
        except:
            pass
    if names:
        result['corpName'] = sorted(
            names, key=lambda x: len(x.split(' ')), reverse=True)[0]
    if addresses:
        result['mainAddress'] = re.split(
            r'\band\b(?i)', str(addresses[-1]))[-1]
        result['addresses'] = addresses
    if result['mainAddress']:
        result['city'] = addresses[-1].city
        result['region'] = addresses[-1].region1
        result['country'] = addresses[-1].country_id
        result['postalCode'] = addresses[-1].postal_code
        result['addressLine'] = addresses[-1].full_street
    result['addresses'] = [str(a) for a in result['addresses']]
    return result


def standardScrape(url, parkingterms=[r'godaddy', r'domain is available for sale']):
    domain = toDomain(url)
    parkingpattern = re.compile('|'.join(parkingterms), re.I)
    try:
        res = requests.get('http://'+domain, timeout=15)
        statusCode = res.status_code
    except Exception as e:
        statusCode, webstatus = "time out", "Presumed Inactive"
        return {'statusCode':"time out","webstatus":"Presumed Inactive"}, b''

    if statusCode in [523, 503, 502, 500, 410, 409, 404]:
        return {'statusCode':statusCode,"webstatus":"inactive"}, b''
    else:
        webstatus = 'active'
        result = parse(res.content, domain=domain)
        result['redirectURL'] = toDomain(res.url)
        if re.findall(parkingpattern, result.get('homepageText','')):
            return {'statusCode':statusCode,"webstatus":"parking"}, b''
        result['statusCode'] = statusCode
        result['webstatus'] = webstatus
        return result, res.content

if __name__ == '__main__':
    # res = requests.get('http://keywebpmt.com', timeout=20, headers=headers)
    # result = parse(res.content)
    import kumihotools
    result,_ = standardScrape('adopttechnologies.com', parkingterms=kumihotools.parkingterms)
    # result, content = standardScrape('http://keywebpmt.com')
    print(result)