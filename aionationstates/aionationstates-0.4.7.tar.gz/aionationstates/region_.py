import re
import enum
import html
from itertools import count
from asyncio import sleep
from contextlib import suppress
from functools import reduce, total_ordering
from operator import or_

from aionationstates.utils import (
    timestamp, unscramble_encoding, DataClassWithId)
from aionationstates.session import Session, api_query
from aionationstates.shared import CensusRanks, NationRegion, Poll
import aionationstates


__all__ = ('Embassies', 'Authority', 'Officer', 'EmbassyPostingRights',
           'PostStatus', 'Post', 'Region')


class Embassies:
    """Embassies of a region.

    Attributes
    ----------
    active : list of :class:`Region`
        Normal, alive embassies.
    closing : list of :class:`Region`
        Embassies the demolition of which has been initiated, but did
        not yet finish.
    pending : list of :class:`Region`
        Embassies the creation of which has been initiated, but did not
        yet finish.
    invited : list of :class:`Region`
        Embassy invitations that have not yet been processed.
    rejected : list of :class:`Region`
        Embassy invitations that have been denied.
    """

    def __init__(self, elem):
        # I know I'm iterating through them five times; I don't care.
        self.active = [aionationstates.Region(sub_elem.text)
                       for sub_elem in elem
                       if sub_elem.get('type') is None]
        self.closing = [aionationstates.Region(sub_elem.text)
                        for sub_elem in elem
                        if sub_elem.get('type') == 'closing']
        self.pending = [aionationstates.Region(sub_elem.text)
                        for sub_elem in elem
                        if sub_elem.get('type') == 'pending']
        self.invited = [aionationstates.Region(sub_elem.text)
                        for sub_elem in elem
                        if sub_elem.get('type') == 'invited']
        self.rejected = [aionationstates.Region(sub_elem.text)
                         for sub_elem in elem
                         if sub_elem.get('type') == 'rejected']


class Authority(enum.Flag):
    """Authority of a Regional Officer, Delegate, or Founder.

    Attributes
    ----------
    X = EXECUTIVE : :class:`Authority`
        Can appoint/dismiss Officers and set their authority.
    W = WORLD_ASSEMBLY : :class:`Authority`
        Can approve World Assembly proposals.
    A = APPEARANCE : :class:`Authority`
        Can modify the World Factbook Entry, Flag, and Tags, and pin
        Dispatches.
    B = BORDER_CONTROL : :class:`Authority`
        Can eject/ban/unban nations and set/modify/remove the region
        password.
    C = COMMUNICATIONS : :class:`Authority`
        Can send region-wide telegrams without stamps, compose Welcome
        telegrams, suppress & unsuppress posts on the Regional Message
        Board, and control who can recruit for the region.
    E = EMBASSIES : :class:`Authority`
        Can open/close embassies with other regions and modify embassy
        posting privileges.
    P = POLLS : :class:`Authority`
        Can create polls.
    """
    EXECUTIVE      = X = enum.auto()
    WORLD_ASSEMBLY = W = enum.auto()
    APPEARANCE     = A = enum.auto()
    BORDER_CONTROL = B = enum.auto()
    COMMUNICATIONS = C = enum.auto()
    EMBASSIES      = E = enum.auto()
    POLLS          = P = enum.auto()

    @classmethod
    def _from_ns(cls, string):
        """This is the only sane way I could find to make Flag enums
        work with individual characters as flags."""
        return reduce(or_, (cls[char] for char in string))

    @classmethod
    def _from_happening(cls, text):
        names = re.findall('<i .+?></i>(.+?)(?: and|,|$)', text)
        return reduce(
            or_,
            (cls[name.upper().replace(' ', '_')] for name in names),
            cls(0)
        )


class Officer:
    """A Regional Officer.

    Attributes
    ----------
    nation : :class:`Nation`
        Officer's nation.
    office : str
        The (user-specified) office held by the officer.
    authority : :class:`Authority`
        Officer's authority.
    appointed_at : naive UTC :class:`datetime.datetime`
        When the officer got appointed.
    appointed_by : :class:`Nation`
        The nation that appointed the officer.
    """

    def __init__(self, elem):
        self.nation = aionationstates.Nation(elem.find('NATION').text)
        self.office = elem.findtext('OFFICE')
        self.authority = Authority._from_ns(elem.find('AUTHORITY').text)
        self.appointed_at = timestamp(elem.find('TIME').text)
        self.appointed_by = aionationstates.Nation(elem.find('BY').text)


@total_ordering
class EmbassyPostingRights(enum.Enum):
    """Who out of embassy regions' residents can post on the Regional
    Message Board.

    Can be compared and ordered.

    Attributes
    ----------
    NOBODY : :class:`EmbassyPostingRights`
        No members of the embassy regions can post.
    DELEGATES_AND_FOUNDERS : :class:`EmbassyPostingRights`
        Only the Founders and WA Delegates of embassy regions can post.
    COMMUNICATIONS_OFFICERS : :class:`EmbassyPostingRights`
        Only Regional Officers of embassy regions with the
        Communications authority can post.
    OFFICERS : :class:`EmbassyPostingRights`
        All Regional Officers of embassy regions can post.
    EVERYBODY : :class:`EmbassyPostingRights`
        All members of embassy regions can post.
    """
    NOBODY = 1
    DELEGATES_AND_FOUNDERS = 2
    COMMUNICATIONS_OFFICERS = 3
    OFFICERS = 4
    EVERYBODY = 5

    @classmethod
    def _from_ns(cls, string):
        values = {
            '0': 1,  # The reason I have to do all this nonsense.
            'con': 2,
            'com': 3,
            'off': 4,
            'all': 5,
        }
        return cls(values[string])

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented


class PostStatus(enum.Enum):
    """Status of a post on a Regional Message Board.

    Attributes
    ----------
    NORMAL : :class:`PostStatus`
        A regular post.
    SUPPRESSED : :class:`PostStatus`
        The post got suppressed by a regional officer.
    DELETED : :class:`PostStatus`
        The post got deleted by its author.
    MODERATED : :class:`PostStatus`
        The post got suppressed by a game moderator.
    """
    NORMAL = 0
    SUPPRESSED = 1
    DELETED = 2
    MODERATED = 9

    @property
    def viewable(self):
        """bool: Whether the post content can still be accessed.
        Shortcut for ``PostStatus.NORMAL or PostStatus.SUPPRESSED``.
        """
        return self.value in (0, 1)


class Post(DataClassWithId):
    """A post on a Regional Message Board.

    Attributes
    ----------
    id : int
        The unique id of the post.
    timestamp : naive UTC :class:`datetime.datetime`
        When the post was put up.
    author : :class:`Nation`
        The author nation.
    status : :class:`PostStatus`
        Status of the post.
    text : str
        The post text.
    likers : list of :class:`Nation`
        Nations that liked the post.
    suppressor : :class:`Nation` or None
        Nation that suppressed the post.  ``None`` if the post has not
        been suppressed or has been suppressed by moderators.
    """

    def __init__(self, elem):
        self.id = int(elem.get('id'))
        self.timestamp = timestamp(elem.find('TIMESTAMP').text)
        self.author = aionationstates.Nation(elem.find('NATION').text)
        self.status = PostStatus(int(elem.find('STATUS').text))
        self.text = unscramble_encoding(html.unescape(elem.find('MESSAGE').text))

        likers = elem.findtext('LIKERS')
        if likers:
            self.likers = [aionationstates.Nation(name) for name
                           in likers.split(':')]
        else:
            self.likers = []

        suppressor_str = elem.findtext('SUPPRESSOR')
        if suppressor_str in ('!mod', None):
            self.suppressor = None
        else:
            self.suppressor = aionationstates.Nation(suppressor_str)

    @property
    def url(self):
        """str: Link to the post."""
        return f'https://www.nationstates.net/page=rmb/postid={self.id}'

    def quote(self, text=None):
        """Quote this post.

        Parameters
        ----------
        text : str
            Text to quote.  Defaults to the whole text of the post.

        Returns
        -------
        str
            A NationStates bbCode quote of the post.
        """
        text = text or re.sub(r'\[quote=.+?\[/quote\]', '',
                              self.text, flags=re.DOTALL
                              ).strip('\n')
        return f'[quote={self.author.id};{self.id}]{text}[/quote]'


class Region(CensusRanks, NationRegion, Session):
    """A class to interact with the NationStates Region API.

    Attributes
    ----------
    id : str
        The defining characteristic of a region, its normalized name.
        No two regions share the same id, and no one id is shared by
        multiple regions.
    """
    def _call_api(self, params, *args, **kwargs):
        params['region'] = self.id
        return super()._call_api(*args, params=params, **kwargs)

    @property
    def url(self):
        """str: URL of the region."""
        return f'https://www.nationstates.net/region={self.id}'

    @api_query('name')
    async def name(self, root):
        """Name of the region, with proper capitalization.

        Returns
        -------
        an :class:`ApiQuery` of str
        """
        return root.find('NAME').text

    @api_query('flag')
    async def flag(self, root):
        """URL of the region's flag.

        Returns
        -------
        an :class:`ApiQuery` of str
        """
        return root.find('FLAG').text

    @api_query('factbook')
    async def factbook(self, root):
        """Region's World Factbook Entry.

        Returns
        -------
        an :class:`ApiQuery` of str
        """
        # This lib might have been a mistake, but the line below
        # definitely isn't.
        return html.unescape(html.unescape(root.find('FACTBOOK').text))

    @api_query('power')
    async def power(self, root):
        """An adjective describing region's power on the interregional
        scene.

        Returns
        -------
        an :class:`ApiQuery` of str
        """
        return root.find('POWER').text

    @api_query('delegatevotes')
    async def delegatevotes(self, root):
        """Number of the votes in the World Assembly the region's
        Delegate has.

        Equal to the number of endorsements they have received.

        Returns
        -------
        an :class:`ApiQuery` of int
        """
        return int(root.find('DELEGATEVOTES').text)

    @api_query('numnations')
    async def numnations(self, root):
        """The number of nations in the region.

        Returns
        -------
        an :class:`ApiQuery` of int
        """
        return int(root.find('NUMNATIONS').text)

    @api_query('foundedtime')
    async def founded(self, root):
        """When the region was founded.

        Returns
        -------
        an :class:`ApiQuery` of a naive UTC :class:`datetime.datetime`
        """
        return timestamp(root.find('FOUNDEDTIME'))

    @api_query('nations')
    async def nations(self, root):
        """All the nations in the region.

        Returns
        -------
        an :class:`ApiQuery` of a list of :class:`Nation` objects
        """
        text = root.find('NATIONS').text
        return ([aionationstates.Nation(n) for n in text.split(':')]
                if text else [])

    @api_query('embassies')
    async def embassies(self, root):
        """Embassies the region has.

        Returns
        -------
        an :class:`ApiQuery` of :class:`Embassies`
        """
        return Embassies(root.find('EMBASSIES'))

    @api_query('embassyrmb')
    async def embassyrmb(self, root):
        """Posting rights for members the of embassy regions.

        Returns
        -------
        an :class:`ApiQuery` of :class:`EmbassyPostingRights`
        """
        return EmbassyPostingRights._from_ns(root.find('EMBASSYRMB').text)

    @api_query('delegate')
    async def delegate(self, root):
        """Regional World Assembly Delegate.

        Returns
        -------
        an :class:`ApiQuery` of :class:`Nation`
        an :class:`ApiQuery` of None
            If the region has no delegate.
        """
        nation = root.find('DELEGATE').text
        if nation == '0':
            return None
        return aionationstates.Nation(nation)

    @api_query('delegateauth')
    async def delegateauth(self, root):
        """Regional World Assembly Delegate's authority.  Always set,
        no matter if the region has a delegate or not.

        Returns
        -------
        an :class:`ApiQuery` of :class:`Authority`
        """
        return Authority._from_ns(root.find('DELEGATEAUTH').text)

    @api_query('founder')
    async def founder(self, root):
        """Regional Founder.  Returned even if the nation has ceased to
        exist.

        Returns
        -------
        an :class:`ApiQuery` of :class:`Nation`
        an :class:`ApiQuery` of None
          If the region is Game-Created and doesn't have a founder.
        """
        nation = root.find('FOUNDER').text
        if nation == '0':
            return None
        return aionationstates.Nation(nation)

    @api_query('founderauth')
    async def founderauth(self, root):
        """Regional Founder's authority.  Always set,
        no matter if the region has a founder or not.

        Returns
        -------
        an :class:`ApiQuery` of :class:`Authority`
        """
        return Authority._from_ns(root.find('FOUNDERAUTH').text)

    @api_query('officers')
    async def officers(self, root):
        """Regional Officers.  Does not include the Founder or
        the Delegate, unless they have additional titles as Officers.

        In the correct order.

        Returns
        -------
        an :class:`ApiQuery` of a list of :class:`Officer`
        """
        officers = sorted(
            root.find('OFFICERS'),
            # I struggle to say what else this tag would be useful for.
            key=lambda elem: int(elem.find('ORDER').text)
        )
        return [Officer(elem) for elem in officers]

    @api_query('tags')
    async def tags(self, root):
        """Tags the region has.

        Returns
        -------
        an :class:`ApiQuery` of a list of str
        """
        return [elem.text for elem in root.find('TAGS')]

    @api_query('poll')
    async def poll(self, root):
        """The poll currently running in the region.

        Returns
        -------
        an :class:`ApiQuery` of :class:`Poll`
        an :class:`ApiQuery` of None
            If no poll is currently running.
        """
        elem = root.find('POLL')
        return Poll(elem) if elem else None

    # Messages interface:

    def _get_messages(self, *, limit=100, offset=0, fromid=None):
        params = {'limit': str(limit), 'offset': str(offset)}
        if fromid is not None:
            params['fromid'] = str(fromid)

        @api_query('messages', **params)
        async def result(_, root):
            return [Post(elem) for elem in root.find('MESSAGES')]
        return result(self)

    async def messages(self):
        """Iterate through RMB posts from newest to oldest.

        Returns
        -------
        an asynchronous generator that yields :class:`Post`
        """
        # Messages may be posted on the RMB while the generator is running.
        oldest_id_seen = float('inf')
        for offset in count(step=100):
            posts_bunch = await self._get_messages(offset=offset)
            for post in reversed(posts_bunch):
                if post.id < oldest_id_seen:
                    yield post
            oldest_id_seen = posts_bunch[0].id
            if len(posts_bunch) < 100:
                break

    async def new_messages(self, poll_period=30, *, fromid=None):
        """New messages on the Regional Message Board::

            tnp = region('The North Pacific')
            async for post in tnp.new_messages():
                # Your processing code here
                print(post.text)  # As an example

        Guarantees that:

        * Every post is generated from the moment the generator is started;
        * No post is generated more than once;
        * Posts are generated in order from oldest to newest.

        Parameters
        ----------
        poll_period : int
            How long to wait between requesting the next bunch of
            posts, in seconds.  Ignored while catching up to the end
            of the Message Board, meaning that no matter how long of a
            period you set you will never encounter a situation where
            posts are made faster than the generator can deliver them.

            Note that, regardless of the ``poll_period`` you set, all
            of the code in your loop body still has to execute (possibly
            several times) before a new bunch of posts can be
            requested.  Consider wrapping your post-processing code
            in a coroutine and launching it as a task from the loop body
            if you suspect this might be an issue.
        fromid : int
            Request posts starting with the one with this id, as
            as opposed to the last one at the time.  Useful if you
            need to avoid losing posts between restarts.  Set to `1`
            to request the entire RMB history chronologically.

        Returns
        -------
        an asynchronous generator that yields :class:`Post`
        """
        if fromid is not None:
            # fromid of 0 gets ignored by NS
            fromid = 1 if fromid == 0 else fromid
        else:
            try:
                # We only need the posts from this point forwards
                fromid = (await self._get_messages(limit=1))[0].id + 1
            except IndexError:
                # Empty RMB
                fromid = 1
            # Sleep before the loop body to avoid wasting the first request.
            # We only want to apply this "optimization" if fromid was not
            # specified, as only then we know for sure we're at the end of the
            # RMB.
            await sleep(poll_period)

        while True:
            posts = await self._get_messages(fromid=fromid)

            with suppress(IndexError):
                fromid = posts[-1].id + 1

            for post in posts:
                yield post

            if len(posts) < 100:
                await sleep(poll_period)

    # TODO: history
