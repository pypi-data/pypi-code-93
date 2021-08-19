# -*- coding: utf-8 -*-
"""
pubmed-central-mapper:
    A Python Library that map PubMed Central XML to Python object
"""
import re
import json
import logging
from os import scandir
from datetime import date, datetime
from os.path import isdir, exists

import click
import requests
from lxml import etree
from rich.progress import track


logger = logging.getLogger('pubmed-central-mapper')

DATE_FMT = '%Y-%m-%d'


class empty:  # noqa
    pass


def remove_namespace(tree):
    """
    remove namespace of a tree
    Args:
        tree: lxml.etree._ElementTree object
    Returns:
        lxml.etree._Element without namespace
    """
    for element in tree.iter():
        try:
            element.tag = etree.QName(element).localname
        except ValueError:  # omit Invalid input tag of type
            continue
    etree.cleanup_namespaces(tree)
    return tree


def get_inner_html(element, strip=True):
    texts = []
    if element.text:
        texts.append(element.text)
    for child in element.getchildren():
        texts.append(etree.tostring(child, encoding=str))
    if element.tail:
        texts.append(element.tail)
    text = ''.join(texts)
    if strip:
        text = text.strip()
    return text


class BaseParser(object):
    def __init__(self, element):
        self.element = element

    @staticmethod
    def get_first(lst, default=empty):
        if (len(lst) == 0) and (default == empty):
            raise IndexError("can't index empty list")
        return lst[0] if lst else default

    def parse(self):
        raise NotImplemented(
            f'{self.__class__.__name__}.parse not implemented.'
        )


class Id(object):
    def __init__(self, value, type):  # noqa
        self.value = value
        self.type = type

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        if not isinstance(other, Id):
            raise NotImplemented(
                f'compare between {self.__class__.__name__} and '
                f'{other.__class__.__class__} not implemented.'
            )
        return (self.value == other.value) and (self.type == other.type)

    def __repr__(self):
        return f'<{self.__class__.__name__}({self.value})>'

    @classmethod
    def from_dict(cls, dct):
        return cls(**dct)

    def to_dict(self):
        return {
            'value': self.value,
            'type': self.type
        }


class PublisherParser(BaseParser):
    def parse(self):
        name = self.get_first(self.element.xpath(
            './publisher-name/text()'
        ))
        loc = self.get_first(self.element.xpath(
            './publisher-loc/text()'
        ), None)  # noqa
        return Publisher(name=name, loc=loc)


class Publisher(object):
    def __init__(self, name, loc):
        self.name = name
        self.loc = loc

    def __repr__(self):
        return f'<Publisher({self.name})>'

    @classmethod
    def from_dict(cls, dct):
        return cls(**dct)

    def to_dict(self):
        return {
            'name': self.name,
            'loc': self.loc
        }


class JournalIdParser(BaseParser):
    def parse(self):
        return JournalId(
            value=self.element.text,
            type=self.element.get('journal-id-type')
        )


class JournalId(Id):
    """Journal ID"""


class IssnParser(BaseParser):
    def parse(self):
        return Issn(
            value=self.element.text,
            type=self.element.get('pub-type')
        )


class Issn(Id):
    """ISSN"""


class JournalParser(BaseParser):
    def parse_ids(self):
        return [
            JournalIdParser(
                element
            ).parse() for element in self.element.xpath(
                './journal-id'
            )
        ]

    def parse_title(self):
        title = self.get_first(
            self.element.xpath('./journal-title/text()'), None  # noqa
        )
        if not title:
            title = self.get_first(self.element.xpath(
                './journal-title-group/journal-title/text()'
            ))
        return title

    def parse_issns(self):
        return [
            IssnParser(
                element
            ).parse() for element in self.element.xpath(
                './issn'
            )
        ]

    def parse_publisher(self):
        element = self.get_first(
            self.element.xpath('./publisher'),
            None  # noqa
        )
        return None if element is None else PublisherParser(element).parse()

    def parse(self):
        ids = self.parse_ids()
        title = self.parse_title()
        issns = self.parse_issns()
        publisher = self.parse_publisher()
        return Journal(
            ids=ids,
            title=title,
            issns=issns,
            publisher=publisher
        )


class Journal(object):
    def __init__(self, ids, title, issns, publisher):
        self.ids = ids
        self.title = title
        self.issns = issns
        self.publisher = publisher

    def __repr__(self):
        return f'<Journal({self.title})>'

    @classmethod
    def from_dict(cls, dct):
        ids = [
            JournalId.from_dict(id_dct) for id_dct in dct['ids']
        ]
        title = dct['title']
        issns = [
            Issn.from_dict(issn_dct) for issn_dct in dct['issns']
        ]
        publisher = Publisher.from_dict(dct['publisher']) if dct['publisher'] else None
        return cls(
            ids=ids,
            title=title,
            issns=issns,
            publisher=publisher
        )

    def to_dict(self):
        return {
            'ids': [id.to_dict() for id in self.ids],  # noqa
            'title': self.title,
            'issns': [issn.to_dict() for issn in self.issns],
            'publisher': self.publisher.to_dict() if self.publisher else None
        }


class ArticleIdParser(BaseParser):
    def parse(self):
        return ArticleId(
            value=self.element.text,
            type=self.element.get('pub-id-type')
        )


class ArticleId(Id):
    """Article ID"""


class AffParser(BaseParser):
    def parse(self):
        element = self.get_first(self.element.xpath('./label'), None)  # noqa
        title = self.element.text if element is None else element.tail
        return Aff(title=title)


class Aff(object):
    def __init__(self, title):
        self.title = title

    def __repr__(self):
        return f'<Affiliation({self.title})>'

    def __hash__(self):
        return hash(self.title)

    def __eq__(self, other):
        return self.title == other.title

    @classmethod
    def from_dict(cls, dct):
        return cls(**dct)

    def to_dict(self):
        return {
            'title': self.title
        }


class AuthorParser(BaseParser):
    def __init__(self, element, affs):
        super().__init__(element)
        self.affs = affs

    def parse(self):
        type = self.element.get('contrib-type')  # noqa
        surname = self.get_first(self.element.xpath('./name/surname/text()'))
        given_names = self.get_first(
            self.element.xpath('./name/given-names/text()'), None  # noqa
        )
        affs = []
        for rid in self.element.xpath(
            './xref/@rid'
        ):
            if rid in affs:
                affs.append(affs[rid])
        email = self.get_first(
            self.element.xpath('./email/text()'), None  # noqa
        )
        if email is None:
            email = self.get_first(
                self.element.xpath('./address/email/text()'), None  # noqa
            )
        return Author(
            type=type,
            surname=surname,
            given_names=given_names,
            affs=affs,
            email=email
        )


class Author(object):
    def __init__(self, type, surname, given_names, affs, email):  # noqa
        self.type = type
        self.surname = surname
        self.given_names = given_names
        self.affs = affs
        self.email = email

    def __repr__(self):
        return f'<Author({self.surname} {self.given_names})>'

    @classmethod
    def from_dict(cls, dct):
        type = dct['type']  # noqa
        surname = dct['surname']
        given_names = dct['given_names']
        affs = [
            Aff.from_dict(aff_dct) for aff_dct in dct['affs']
        ]
        email = dct['email']
        return cls(
            type=type,
            surname=surname,
            given_names=given_names,
            affs=affs,
            email=email
        )

    def to_dict(self):
        return {
            'type': self.type,
            'surname': self.surname,
            'given_names': self.given_names,
            'affs': [aff.to_dict() for aff in self.affs],
            'email': self.email
        }


class PubDateParser(BaseParser):
    def parse(self):
        year = int(self.get_first(self.element.xpath(
            './year/text()'
        )))
        month = int(self.get_first(
            self.element.xpath('./month/text()'), 1  # noqa
        ))
        day = int(self.get_first(
            self.element.xpath('./day/text()'), 1  # noqa
        ))
        type = self.element.get('pub-type')  # noqa
        return PubDate(
            value=date(year, month, day),
            type=type
        )


class PubDate(object):
    def __init__(self, value, type):  # noqa
        self.value = value
        self.type = type

    def __repr__(self):
        return f'<PubDate({self.value})>'

    @classmethod
    def from_dict(cls, dct):
        value = datetime.strptime(dct['value'], DATE_FMT).date()
        type = dct['type']  # noqa
        return cls(
            value=value,
            type=type
        )

    def to_dict(self):
        return {
            'value': self.value.strftime(DATE_FMT),
            'type': self.type
        }


class ArticleParser(BaseParser):
    def parse_journal(self):
        return JournalParser(self.get_first(
            self.element.xpath('./front/journal-meta')
        )).parse()

    def parse_ids(self):
        return [
            ArticleIdParser(
                element
            ).parse() for element in self.element.xpath(
                './front/article-meta/article-id'
            )
        ]

    def parse_authors(self):
        affs = {
            element.get('id'): AffParser(
                element
            ).parse() for element in self.element.xpath(
                './front/article-meta/aff'
            )
        }
        authors = []
        for element in self.element.xpath(
                './front/article-meta/contrib-group/contrib'
        ):
            if element.xpath('./name/surname'):
                authors.append(AuthorParser(element, affs).parse())
        return authors

    def parse_pub_dates(self):
        return [
            PubDateParser(
                element
            ).parse() for element in self.element.xpath(
                './front/article-meta/pub-date'
            )
        ]

    def parse_volume(self):
        return self.get_first(self.element.xpath(
            './front/article-meta/volume/text()'
        ), None)  # noqa

    def parse_issue(self):
        return self.get_first(self.element.xpath(
            './front/article-meta/issue/text()'
        ), None)  # noqa

    def parse_title(self):
        element = self.get_first(self.element.xpath(
            './front/article-meta/title-group/article-title'
        ), None)  # noqa
        return None if element is None else element.text

    def parse_abstract(self):
        element = self.get_first(self.element.xpath(
            './front/article-meta/abstract'
        ), None)  # noqa
        return None if element is None else get_inner_html(element)

    def parse_keywords(self):
        return self.element.xpath(
            './front/article-meta/kwd-group/kwd/text()'
        )

    def parse_fulltext(self):
        element = self.get_first(
            self.element.xpath('./body'), None  # noqa
        )
        return None if element is None else get_inner_html(element)

    def parse(self):
        journal = self.parse_journal()
        ids = self.parse_ids()
        authors = self.parse_authors()
        pub_dates = self.parse_pub_dates()
        volume = self.parse_volume()
        issue = self.parse_issue()
        title = self.parse_title()
        abstract = self.parse_abstract()
        keywords = self.parse_keywords()
        fulltext = self.parse_fulltext()
        return Article(
            journal=journal, ids=ids, authors=authors,
            pub_dates=pub_dates, volume=volume, issue=issue,
            title=title, abstract=abstract, keywords=keywords, fulltext=fulltext
        )


class Article(object):
    def __init__(
        self,
        journal,
        ids,
        authors,
        pub_dates,
        volume,
        issue,
        title,
        abstract,
        keywords,
        fulltext
    ):
        self.journal = journal
        self.ids = ids
        self.authors = authors
        self.pub_dates = pub_dates
        self.volume = volume
        self.issue = issue
        self.title = title
        self.abstract = abstract
        self.keywords = keywords
        self.fulltext = fulltext

    def __repr__(self):
        return f'<Article({self.title})>'

    @classmethod
    def from_element(cls, element):
        return ArticleParser(element).parse()

    @classmethod
    def get_element_from_string(cls, string):
        element = remove_namespace(etree.fromstring(
            string,
            parser=etree.XMLParser(huge_tree=True)
        ))
        return element.xpath('./article')[0] if element.tag == 'pmc-articleset' else element

    @classmethod
    def from_file(cls, file):
        with open(file, 'rb') as fp:
            string = fp.read()
        return cls.from_element(cls.get_element_from_string(
            string
        ))

    @classmethod
    def from_dict(cls, dct):
        journal = Journal.from_dict(dct['journal'])
        ids = [
            ArticleId.from_dict(id_dct) for id_dct in dct['ids']
        ]
        authors = [
            Author.from_dict(author_dct) for author_dct in dct['authors']
        ]
        pub_dates = [
            PubDate.from_dict(pub_date_dct) for pub_date_dct in dct['pub_dates']
        ]
        volume = dct['volume']
        issue = dct['issue']
        title = dct['title']
        abstract = dct['abstract']
        keywords = dct['keywords']
        fulltext = dct['fulltext']
        return cls(
            journal=journal, ids=ids, authors=authors,
            pub_dates=pub_dates, volume=volume, issue=issue,
            title=title, abstract=abstract, keywords=keywords, fulltext=fulltext
        )

    @classmethod
    def from_pmc_id(cls, pmc_id):
        url = ('https://eutils.ncbi.nlm.nih.gov/entrez'
               '/eutils/efetch.fcgi?db=pmc&id=%s&retmode=xml') % pmc_id
        res = requests.get(url)
        element = cls.get_element_from_string(res.text)
        return cls.from_element(element.xpath('./article')[0])

    def to_dict(self):
        return {
            'journal': self.journal.to_dict(),
            'ids': [id.to_dict() for id in self.ids],  # noqa
            'authors': [author.to_dict() for author in self.authors],
            'pub_dates': [pub_date.to_dict() for pub_date in self.pub_dates],
            'volume': self.volume,
            'issue': self.issue,
            'title': self.title,
            'abstract': self.abstract,
            'keywords': self.keywords,
            'fulltext': self.fulltext
        }


@click.command()
@click.option(
    '-i', '--input', default='.', show_default=True,
    help='input for parse, can be PMC ID, file, or directory.'
)
@click.option(
    '-p', '--pretty', is_flag=True,
    help='write pretty json to outfile'
)
@click.option(
    '-o', '--outfile',
    default='pmc.jl', show_default=True,
    type=click.Path(exists=False),
    help='output file'
)
def main(input, pretty, outfile):  # noqa
    # dump article object to json
    def dumps(article):
        return json.dumps(
            article.to_dict(),
            indent=4 if pretty else None
        )

    # get all xml files of a directory
    def get_files(root):
        files = []
        for file_or_dir in scandir(root):
            if file_or_dir.is_file():  # noqa
                if file_or_dir.path.endswith('xml'):  # noqa
                    files.append(file_or_dir.path)  # noqa
                continue
            for file in get_files(file_or_dir.path):  # noqa
                files.append(file)
        return files

    # input is PMC ID
    if re.search(r'PMC\d+', input):
        article = Article.from_pmc_id(input)
        with open(outfile, 'w') as fp:
            fp.write(dumps(article) + '\n')
        return 0

    # input is directory
    if isdir(input):
        with open(outfile, 'w') as fp:
            files = get_files(input)
            for file in track(files, description='Parsing...'):
                try:
                    article = Article.from_file(file)
                    fp.write(dumps(article) + '\n')
                except Exception as exc:
                    logger.exception(exc)
        return 0

    # input is file
    if not exists(input):
        raise click.UsageError(f'file {input} not exists.')
    article = Article.from_file(input)
    with open(outfile, 'w') as fp:
        fp.write(dumps(article) + '\n')
    return 0


if __name__ == '__main__':
    main()
