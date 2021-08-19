import re
import html
import enum
from contextlib import suppress
from collections import OrderedDict

from aionationstates.utils import (
    normalize, timestamp, unscramble_encoding, logger, banner_url, aobject,
    alist)
from aionationstates.session import Session, api_query, api_command
from aionationstates.shared import NationRegion, DispatchThumbnail
from aionationstates.ns_to_human import census_info
import aionationstates


__all__ = ('Policy', 'Nation', 'CensusScaleChange', 'IssueResult',
           'IssueOption', 'Issue', 'Nation', 'NationControl',
           'WAMembership')


class WAMembership(enum.Enum):
    """Nation's World Assembly status.

    Falsey when the nation doesn't hold membership.

    Attributes
    ----------
    MEMBER : :class:`WAMembership`
        The nation is a member of the World Assembly.
    DELEGATE : :class:`WAMembership`
        The nation is a World Assembly Delegate of one of the regions.
    NONMEMBER : :class:`WAMembership`
        The nation is not a member of the World Assembly.
    """
    MEMBER = 'WA Member'
    DELEGATE = 'WA Delegate'
    NONMEMBER = 'Non-member'

    def __bool__(self):
        return self is not self.NONMEMBER


class Policy:
    """One of nation's policies.

    Attributes
    ----------
    name : str
        Name of the policy.
    category : str
        Category of the policy.
    description : str
        Short description of the policy.
    banner : str
        URL of the policy picture.
    """

    def __init__(self, elem):
        self.name = elem.find('NAME').text
        self.category = elem.find('CAT').text
        self.description = elem.find('DESC').text
        self.banner = banner_url(elem.find('PIC').text)

    def __eq__(self, other):
        if type(self) is not type(other):
            return NotImplemented
        return self.name == other.name

    def __hash__(self):
        return hash((self.name,))

    def __repr__(self):
        return f'<Policy "{self.name}">'


class Nation(NationRegion, Session):
    """A class to interact with the NationStates Nation public API.

    Shards absent (incomplete):

    * **lastactivity** - There is no timestamp version, and the value
      is kind of useless anyways.
    * **govtpriority** - Use the :meth:`govt` shard.
    * **factbooks**, **dispatches**, **factbooklist** - Use the
      :meth:`dispatchlist` shard.
    * **income**, **poorest**, **richest** - Use :meth:`census` scales
      72, 73, and 74 respectively.  The :meth:`gdp` shard has been kept,
      as it appears to be slightly different from scale 76.

    Attributes
    ----------
    id : str
        The defining characteristic of a nation, its normalized name.
        No two nations share the same id, and no one id is shared by
        multiple nations.
    """
    def __eq__(self, other):
        # Nation('testlandia') == NationControl('testlandia, password='123')
        if not isinstance(other, Nation):
            return NotImplemented
        return self.id == other.id

    __hash__ = NationRegion.__hash__

    def _call_api(self, params, **kwargs):
        params['nation'] = self.id
        return super()._call_api(params, **kwargs)


    @property
    def url(self):
        """str: URL of the nation."""
        return f'https://www.nationstates.net/nation={self.id}'

    @api_query('name')
    async def name(self, root):
        """Name of the nation, for example 'Testlandia'.

        Returns
        -------
        an :class:`ApiQuery` of str
        """
        return root.find('NAME').text

    @api_query('type')
    async def type(self, root):
        """Type of the nation, for example 'Hive Mind'.

        Returns
        -------
        an :class:`ApiQuery` of str
        """
        return root.find('TYPE').text

    @api_query('fullname')
    async def fullname(self, root):
        """Full name of the nation, for example 'The Hive Mind of
        Testlandia'.

        Returns
        -------
        an :class:`ApiQuery` of str
        """
        return root.find('FULLNAME').text

    @api_query('motto')
    async def motto(self, root):
        """Motto of the nation.

        Returns
        -------
        an :class:`ApiQuery` of str
        """
        # mottos can be empty, apparently
        return unscramble_encoding(html.unescape(
            root.find('MOTTO').text or ''))

    @api_query('category')
    async def category(self, root):
        """Nation's World Assembly Category.

        Returns
        -------
        an :class:`ApiQuery` of str
        """
        return root.find('CATEGORY').text

    @api_query('region')
    async def region(self, root):
        """Region in which the nation resides.

        Returns
        -------
        an :class:`ApiQuery` of :class:`Region`
        """
        return aionationstates.Region(root.find('REGION').text)

    @api_query('animal')
    async def animal(self, root):
        """Nation's national animal.

        Returns
        -------
        an :class:`ApiQuery` of str
        """
        return root.find('ANIMAL').text

    @api_query('currency')
    async def currency(self, root):
        """Nation's national currency.

        Returns
        -------
        an :class:`ApiQuery` of str
        """
        return root.find('CURRENCY').text

    @api_query('demonym')
    async def demonym(self, root):
        """Nation's demonym, as an adjective.

        Example: Testlandish, as in 'I'm proud to be Testlandish.'

        Returns
        -------
        an :class:`ApiQuery` of str
        """
        return root.find('DEMONYM').text

    @api_query('demonym2')
    async def demonym2(self, root):
        """Nation's demonym, as a noun.

        Example: Testlandian, as in 'I'm a proud Testlandian.'

        Returns
        -------
        an :class:`ApiQuery` of str
        """
        return root.find('DEMONYM2').text

    @api_query('demonym2plural')
    async def demonym2plural(self, root):
        """Plural of the nation's noun demonym.

        Example: Testlandians, as in 'Here come the Testlandians!'

        Returns
        -------
        an :class:`ApiQuery` of str
        """
        return root.find('DEMONYM2PLURAL').text

    @api_query('flag')
    async def flag(self, root):
        """URL of the nation's flag.

        Returns
        -------
        an :class:`ApiQuery` of str
        """
        return root.find('FLAG').text

    @api_query('majorindustry')
    async def majorindustry(self, root):
        """The industry prioritized by the nation.

        Returns
        -------
        an :class:`ApiQuery` of str
        """
        return root.find('MAJORINDUSTRY').text

    @api_query('influence')
    async def influence(self, root):
        """An adjective describing nation's regional influence.

        Returns
        -------
        an :class:`ApiQuery` of str
        """
        return root.find('INFLUENCE').text

    @api_query('leader')
    async def leader(self, root):
        """Nation's leader.  Either set by the user or the default
        'Leader'.

        Returns
        -------
        an :class:`ApiQuery` of str
        """
        return root.find('LEADER').text

    @api_query('capital')
    async def capital(self, root):
        """Nation's capital. Either set by the user or the default
        '`name` City.'

        Returns
        -------
        an :class:`ApiQuery` of str
        """
        return root.find('CAPITAL').text

    @api_query('religion')
    async def religion(self, root):
        """Nation's main religion.  Either set by the user or the
        default 'a major religion.'

        Returns
        -------
        an :class:`ApiQuery` of str
        """
        return root.find('RELIGION').text

    @api_query('admirable')
    async def admirable(self, root):
        """One of the nation's qualities, at random.

        Example: 'environmentally stunning'

        Returns
        -------
        an :class:`ApiQuery` of str
        """
        return root.find('ADMIRABLE').text

    @api_query('animaltrait')
    async def animaltrait(self, root):
        """Short characteristic of the nation's national animal.

        Example: 'frolics freely in the nation's sparkling oceans'

        Returns
        -------
        an :class:`ApiQuery` of str
        """
        return root.find('ANIMALTRAIT').text

    @api_query('crime')
    async def crime(self, root):
        """A sentence describing the nation's crime levels.

        Example: 'Crime is totally unknown, thanks to a very
        well-funded police force and progressive social policies in
        education and welfare.'

        Returns
        -------
        an :class:`ApiQuery` of str
        """
        return root.find('CRIME').text

    @api_query('govtdesc')
    async def govtdesc(self, root):
        """A couple of sentences describing the nation's government.

        Example: 'It is difficult to tell where the omnipresent
        government stops and the rest of society begins, but it
        juggles the competing demands of Defense, Environment, and
        Healthcare. It meets to discuss matters of state in the
        capital city of Test City.'

        Returns
        -------
        an :class:`ApiQuery` of str
        """
        return root.find('GOVTDESC').text

    @api_query('industrydesc')
    async def industrydesc(self, root):
        """A couple of sentences describing the nation's economy,
        industry, and average income.

        Example: 'The strong Testlandish economy, worth a remarkable
        2,212 trillion denarii a year, is driven almost entirely by
        government activity. The industrial sector, which is extremely
        specialized, is mostly made up of the Arms Manufacturing
        industry, with major contributions from Book Publishing.
        Average income is 73,510 denarii, with the richest citizens
        earning 6.0 times as much as the poorest.'

        Returns
        -------
        an :class:`ApiQuery` of str
        """
        return root.find('INDUSTRYDESC').text

    @api_query('notable')
    async def notable(self, root):
        """A few of nation's peculiarities, at random.

        Example: 'museums and concert halls, multi-spousal wedding
        ceremonies, and devotion to social welfare'

        Returns
        -------
        an :class:`ApiQuery` of str
        """
        return root.find('NOTABLE').text

    @api_query('sensibilities')
    async def sensibilities(self, root):
        """A couple of adjectives describing the nation's citizens.

        Example: 'compassionate, devout'

        Returns
        -------
        an :class:`ApiQuery` of str
        """
        return root.find('SENSIBILITIES').text

    @api_query('population')
    async def population(self, root):
        """Nation's population, in millions.

        Returns
        -------
        an :class:`ApiQuery` of int
        """
        return int(root.find('POPULATION').text)

    @api_query('gdp')
    async def gdp(self, root):
        """Nation's gross domestic product.

        Returns
        -------
        an :class:`ApiQuery` of int
        """
        return int(root.find('GDP').text)

    @api_query('foundedtime')
    async def founded(self, root):
        """When the nation was founded.

        ``1970-01-01 00:00`` for nations founded in Antiquity.

        Returns
        -------
        an :class:`ApiQuery` of a naive UTC :class:`datetime.datetime`
        """
        return timestamp(root.find('FOUNDEDTIME').text)

    @api_query('firstlogin')
    async def firstlogin(self, root):
        """When the nation was first logged into.

        ``1970-01-01 00:00`` for nations first logged into during
        Antiquity.

        Returns
        -------
        an :class:`ApiQuery` of a naive UTC :class:`datetime.datetime`
        """
        return timestamp(root.find('FIRSTLOGIN').text)

    @api_query('lastlogin')
    async def lastlogin(self, root):
        """When the nation was last logged into.

        Returns
        -------
        an :class:`ApiQuery` of a naive UTC :class:`datetime.datetime`
        """
        return timestamp(root.find('LASTLOGIN').text)

    @api_query('wa')
    async def wa(self, root):
        """Whether the nation is a member of the World Assembly or not.

        Returns
        -------
        an :class:`ApiQuery` of :class:`WAMembership`
        """
        return WAMembership(root.find('UNSTATUS').text)

    def tgcanrecruit(self, region=None):
        """Whether the nation will receive a recruitment telegram.

        Useful in conjunction with the Telegrams API.

        Parameters
        ----------
        region : str
            Name of the region you are recruiting for.

        Returns
        -------
        an :class:`ApiQuery` of bool
        """
        params = {'from': normalize(region)} if region is not None else {}
        @api_query('tgcanrecruit', **params)
        async def result(_, root):
            return bool(int(root.find('TGCANRECRUIT').text))
        return result(self)

    @api_query('freedom')
    async def freedom(self, root):
        """Nation's `Freedoms`: three basic indicators of the nation's
        Civil Rights, Economy, and Political Freedom, as expressive
        adjectives.

        Returns
        -------
        an :class:`ApiQuery` of :class:`collections.OrderedDict` with \
        keys and values of str
            Keys being, in order: ``Civil Rights``, ``Economy``, and
            ``Political Freedom``.
        """
        elem = root.find('FREEDOM')
        result = OrderedDict()

        result['Civil Rights'] = elem.find('CIVILRIGHTS').text
        result['Economy'] = elem.find('ECONOMY').text
        result['Political Freedom'] = elem.find('POLITICALFREEDOM').text
        return result

    @api_query('freedomscores')
    async def freedomscores(self, root):
        """Nation's `Freedoms`: three basic indicators of the nation's
        Civil Rights, Economy, and Political Freedom, as percentages.

        Returns
        -------
        an :class:`ApiQuery` of :class:`collections.OrderedDict` with \
        keys of str and values of int
            Keys being, in order: ``Civil Rights``, ``Economy``, and
            ``Political Freedom``.
        """
        elem = root.find('FREEDOMSCORES')
        result = OrderedDict()

        result['Civil Rights'] = int(elem.find('CIVILRIGHTS').text)
        result['Economy'] = int(elem.find('ECONOMY').text)
        result['Political Freedom'] = int(elem.find('POLITICALFREEDOM').text)
        return result

    @api_query('govt')
    async def govt(self, root):
        """Nation's government expenditure, as percentages.

        Returns
        -------
        an :class:`ApiQuery` of :class:`collections.OrderedDict` with \
        keys of str and values of float
            Keys being, in order: ``Administration``, ``Defense``,
            ``Education``, ``Environment``, ``Healthcare``, ``Industry``,
            ``International Aid``, ``Law & Order``, ``Public Transport``,
            ``Social Policy``, ``Spirituality``, and ``Welfare``.
        """
        elem = root.find('GOVT')
        result = OrderedDict()

        result['Administration'] = float(elem.find('ADMINISTRATION').text)
        result['Defense'] = float(elem.find('DEFENCE').text)  # match the web UI
        result['Education'] = float(elem.find('EDUCATION').text)
        result['Environment'] = float(elem.find('ENVIRONMENT').text)
        result['Healthcare'] = float(elem.find('HEALTHCARE').text)
        result['Industry'] = float(elem.find('COMMERCE').text)  # Don't ask
        result['International Aid'] = float(elem.find('INTERNATIONALAID').text)
        result['Law & Order'] = float(elem.find('LAWANDORDER').text)
        result['Public Transport'] = float(elem.find('PUBLICTRANSPORT').text)
        result['Social Policy'] = float(elem.find('SOCIALEQUALITY').text)  # Shh
        result['Spirituality'] = float(elem.find('SPIRITUALITY').text)
        result['Welfare'] = float(elem.find('WELFARE').text)
        return result

    @api_query('sectors')
    async def sectors(self, root):
        """Components of the nation's economy, as percentages.

        Returns
        -------
        an :class:`ApiQuery` of :class:`collections.OrderedDict` with \
        keys of str and values of float
            Keys being, in order: ``Black Market (estimated)``, ``Government``,
            ``Private Industry``, and ``State-Owned Industry``.
        """
        elem = root.find('SECTORS')
        result = OrderedDict()

        result['Black Market (estimated)'] = float(elem.find('BLACKMARKET').text)
        result['Government'] = float(elem.find('GOVERNMENT').text)
        result['Private Industry'] = float(elem.find('INDUSTRY').text)
        result['State-Owned Industry'] = float(elem.find('PUBLIC').text)
        return result

    @api_query('deaths')
    async def deaths(self, root):
        """Causes of death in the nation, as percentages.

        Returns
        -------
        an :class:`ApiQuery` of dict with keys of str and values of float
        """
        return {
            elem.get('type'): float(elem.text)
            for elem in root.find('DEATHS')
        }

    @api_query('endorsements')
    async def endorsements(self, root):
        """Regional neighbours endorsing the nation.

        Returns
        -------
        an :class:`ApiQuery` of a list of :class:`Nation`
        """
        text = root.find('ENDORSEMENTS').text
        return [Nation(name) for name in text.split(',')] if text else []

    @api_query('legislation')
    async def legislation(self, root):
        """Effects of the most recently passed legislation.

        May contain HTML elements and character references.

        Returns
        -------
        an :class:`ApiQuery` of a list of str
        """
        return [elem.text for elem in root.find('LEGISLATION')]

    @api_query('dispatchlist')
    async def dispatchlist(self, root):
        """Nation's published dispatches.

        Returns
        -------
        an :class:`ApiQuery` of a list of :class:`DispatchThumbnail`
        """
        return [
            DispatchThumbnail._from_elem(elem)
            for elem in root.find('DISPATCHLIST')
        ]

    @api_query('policies')
    async def policies(self, root):
        """Nation's policies.

        Returns
        -------
        an :class:`ApiQuery` of a list of :class:`Policy`
        """
        return [
            Policy(elem)
            for elem in root.find('POLICIES')
        ]

    def verify(self, checksum, *, token=None):
        """Interface to the `NationStates Verification API
        <https://www.nationstates.net/pages/api.html#verification>`_.

        Parameters
        ----------
        checksum : str
            The user-supplied verification code.  Expires if the nation
            logs out, if it performs a significant in-game action such
            as moving regions or endorsing another nation, and after it
            is successfully verified.
        token : str
            A token specific to your service and the nation being verified.

        Returns
        -------
        an :class:`ApiQuery` of bool
        """
        params = {'a': 'verify', 'checksum': checksum}
        if token:
            params['token'] = token
        # Needed so that we get output in xml, as opposed to
        # plain text. It doesn't actually matter what the
        # q param is, it's just important that it's not empty.
        @api_query('i_need_the_output_in_xml', **params)
        async def result(self, root):
            return bool(int(root.find('VERIFY').text))
        return result(self)

    def verification_url(self, *, token=None):
        """URL the user needs to follow in order to get the
        verification code for the nation.

        Parameters
        ----------
        token : str
            A token specific to your service and the nation being verified.

        Returns
        -------
        str
        """
        if token:
            return ('https://www.nationstates.net/'
                    f'page=verify_login?token={token}')
        return f'https://www.nationstates.net/page=verify_login'

    @api_query('banners')
    async def banners(self, root):
        """Nation's visible banners.  If the user has set a primary
        banner, it will be the first element in the list.

        Returns
        -------
        an :class:`ApiQuery` of a list of str
            URLs of the banner pictures.
        """
        return [
            banner_url(elem.text)
            for elem in root.find('BANNERS')
        ]

    def _get_macros_expander(self):
        # The only three macros present in the banner names:
        query = self.demonym() + self.name() + self.religion()
        query_result = None

        async def expand_macros(line):
            nonlocal query_result
            if '@@' in line:
                if query_result is None:
                    # Only request macros data if we need it
                    query_result = await query
                return (
                    line
                    .replace('@@DEMONYM@@', query_result[0])
                    .replace('@@NAME@@', query_result[1])
                    .replace('@@FAITH@@', query_result[2])
                )
            return line

        return expand_macros

    async def description(self):
        """Nation's full description, as seen on its in-game page.

        Returns
        -------
        an awaitable of str
        """
        resp = await self._call_web(f'nation={self.id}')
        return html.unescape(
            re.search(
                '<div class="nationsummary">(.+?)<p class="nationranktext">',
                resp.text,
                flags=re.DOTALL
            )
            .group(1)
            .replace('\n', '')
            .replace('</p>', '')
            .replace('<p>', '\n\n')
            .strip()
        )


# Issue outcome processing:

async def reclassifications(elem, census, expand_macros):
    if elem is not None:
        census = {scale.info.id: scale for scale in census[:3]}
        for sub_elem in elem:
            before = sub_elem.find('FROM').text
            after = sub_elem.find('TO').text
            reclassification_type = sub_elem.get('type')
            if reclassification_type == 'govt':
                yield await expand_macros(
                    f'@@NAME@@ was reclassified from {before} to {after}')
            else:
                scale = census[int(reclassification_type)]
                changed = 'rose' if scale.change > 0 else 'fell'
                yield await expand_macros(
                    f'@@NAME@@\'s {scale.info.title}'
                    f' {changed} from {before} to {after}')


class CensusScaleChange:
    """Change in one of the World Census scales of a nation

    Attributes
    ---------
    info : :class:`ScaleInfo`
        Static information about the scale.
    score : float
        The scale score, after the change.
    change : float
        Change of the score.
    pchange : float
        The semi-user-friendly percentage change NationStates shows by default.
    """

    def __init__(self, elem):
        self.info = census_info[int(elem.get('id'))]
        self.score = float(elem.find('SCORE').text)
        self.change = float(elem.find('CHANGE').text)
        self.pchange = float(elem.find('PCHANGE').text)


class IssueResult(aobject):
    """Outcome of an issue.

    Attributes
    ----------
    effect_line : str or None
        The issue effect line.  Not a sentence, mind you -- it's
        uncapitalized and does not end with a period.  ``None`` if the
        issue was dismissed.
    census : list of :class:`CensusScaleChange`
        Changes in census scores of the nation.
    banners : list of :class:`Banner`
        The banners unlocked by answering the issue.
    new_policies : list of :class:`Policy`
        Policies introduced.
    removed_policies : list of :class:`Policy`
        Policies removed.
    reclassifications : list of str
        All WA Category and Freedoms reclassifications listed, such as
        'Testlandia's Civil Rights fell from Very Good to Good',
        'Testlandia was reclassified from Inoffensive Centrist Democracy
        to Democratic Socialists', etc..
    headlines : list of str
        Newspaper headlines.
    """
    async def __init__(self, elem, expand_macros):
        with suppress(AttributeError):
            error = elem.find('ERROR').text
            if error == 'Invalid choice.':
                raise ValueError('invalid option')
            elif error == 'Issue already processed!':
                # I know it may not be obvious, but that's exactly
                # what NS is trying to say here.
                raise ValueError('invalid issue')
        assert elem.find('OK').text == '1'  # honestly no idea

        self.effect_line = elem.findtext('DESC')
        self.census = [
            CensusScaleChange(sub_elem) for sub_elem
            in elem.find('RANKINGS') or ()
        ]

        banners_elem = elem.find('UNLOCKS')
        if banners_elem:
            self.banners = await aionationstates.world.banner(
                *[sub_elem.text for sub_elem in banners_elem],
                _expand_macros=expand_macros
            )
        else:
            self.banners = []

        self.new_policies = [
            Policy(sub_elem) for sub_elem
            in elem.find('NEW_POLICIES') or ()
        ]
        self.removed_policies = [
            Policy(sub_elem) for sub_elem
            in elem.find('REMOVED_POLICIES') or ()
        ]

        self.reclassifications = await alist(
            reclassifications(elem.find('RECLASSIFICATIONS'),
                              self.census, expand_macros)
        )
        self.headlines = [
            # There are occasionally trailing spaces in headlines.
            sub_elem.text.strip() for sub_elem
            in elem.find('HEADLINES') or ()
        ]


# Unsolved issues:

class IssueOption:
    """An option of an issue.

    Attributes
    ----------
    text : str
        The option text.  May contain HTML elements and character references.
    """

    def __init__(self, elem, issue):
        self._issue = issue
        self._id = int(elem.get('id'))
        self.text = unscramble_encoding(elem.text)

    def accept(self):
        """Accept the option.

        Returns
        -------
        an awaitable of :class:`IssueResult`
        """
        return self._issue._nation._accept_issue(self._issue.id, self._id)

    def __repr__(self):
        return f'<Option {self._id} of issue #{self._issue.id}>'


class Issue:
    """An issue.

    Attributes
    ----------
    id : int
        The issue id.
    title : str
        The issue title.  May contain HTML elements and character references.
    text : str
        The issue text.  May contain HTML elements and character references.
    author : str
        Author of the issue, usually the name of a nation.
    editor : str
        Author of the issue, usually the name of a nation.
    options : list of :class:`IssueOption`
        Issue options.
    banners : str
        URLs of issue banners.
    """

    def __init__(self, elem, nation):
        self._nation = nation
        self.id = int(elem.get('id'))
        self.title = elem.find('TITLE').text
        self.text = unscramble_encoding(elem.find('TEXT').text)
        self.author = elem.findtext('AUTHOR')
        self.editor = elem.findtext('EDITOR')
        self.options = [
            IssueOption(sub_elem, self)
            for sub_elem in elem.findall('OPTION')
        ]
        def issue_banners(elem):
            for x in range(1, 10):  # Should be more than enough.
                try:
                    yield banner_url(elem.find(f'PIC{x}').text)
                except AttributeError:
                    break
        self.banners = list(issue_banners(elem))

    def dismiss(self):
        """Dismiss the issue.

        Returns
        -------
        an awaitable of :class:`IssueResult`
        """
        return self._nation._accept_issue(self.id, -1)

    def __eq__(self, other):
        if type(self) is not type(other):
            return NotImplemented
        return (
            self.id == other.id
            and self._nation == other._nation
        )

    def __hash__(self):
        return hash((self.id, self._nation))

    def __repr__(self):
        return f'<Issue #{self.id}>'


class NationControl(Nation):
    """Interface to the NationStates private Nation API.  Subclasses
    :class:`Nation`.

    Credentials are not checked upon initialization, you will only know
    if you've made a mistake after you try to make the first request.
    """
    def __init__(self, name, autologin='', password=''):
        if not password and not autologin:
            raise ValueError('No password or autologin supplied')
        self.password = password
        self.autologin = autologin
        # Weird things happen if the supplied pin doesn't follow the format
        self.pin = '0000000000'
        super().__init__(name)

    async def _base_call_api(self, method, **kwargs):
        headers = {
            'X-Password': self.password,
            'X-Autologin': self.autologin,
            'X-Pin': self.pin
        }
        resp = await super()._base_call_api(method, headers=headers, **kwargs)
        with suppress(KeyError):
            self.pin = resp.headers['X-Pin']
            logger.info(f'Updating pin for {self.id} from API header')
            self.autologin = resp.headers['X-Autologin']
            logger.info(f'Setting autologin for {self.id} from API header')
        return resp

    async def _call_web(self, path, method='GET', **kwargs):
        if not self.autologin:
            # Obtain autologin in case only password was provided
            await self._call_api({'nation': self.id, 'q': 'nextissue'})
        cookies = {
            # Will not work with unescaped equals sign
            'autologin': self.id + '%3D' + self.autologin,
            'pin': self.pin
        }
        resp = await super()._call_web(path, method=method,
                                       cookies=cookies, **kwargs)
        with suppress(KeyError):
            self.pin = resp.cookies['pin'].value
            logger.info(f'Updating pin for {self.id} from web cookie')
        return resp

    async def _call_api_command(self, data, **kwargs):
        data['nation'] = self.id
        return await self._base_call_api('POST', data=data, **kwargs)

    # End of authenticated session handling

    @api_query('issues')
    async def issues(self, root):
        """Issues the nation currently faces.

        Returns
        -------
        an :class:`ApiQuery` of a list of :class:`Issue`
        """
        return [Issue(elem, self) for elem in root.find('ISSUES')]

    def _accept_issue(self, issue_id, option_id):
        @api_command('issue', issue=str(issue_id), option=str(option_id))
        async def result(_, root):
            return await IssueResult(
                root.find('ISSUE'), self._get_macros_expander())
        return result(self)
