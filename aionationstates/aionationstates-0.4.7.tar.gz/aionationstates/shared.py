"""Shared data classes and API shards."""

# TODO: wabadges

import html
from collections import namedtuple
from contextlib import suppress
from itertools import count

from aionationstates.session import api_query
from aionationstates.utils import (
    timestamp, unscramble_encoding, DataClassWithId, normalize)
from aionationstates.ns_to_human import census_info
import aionationstates


__all__ = ('PollOption', 'Poll', 'DispatchThumbnail', 'Dispatch',
           'CensusScaleCurrent', 'CensusPoint', 'CensusScaleHistory',
           'Zombie', 'ArchivedHappening', 'CensusRank')


# Shared data classes:

class PollOption:
    """An option in a poll.

    Attributes
    ----------
    text : str
        Text of the option.
    voters : list of :class:`Nation`
        Nations that picked this option.
    """

    def __init__(self, elem):
        # Troublesome characters are cut from option texts, so
        # unscrambling is not necessary.
        self.text = html.unescape(elem.findtext('OPTIONTEXT'))

        voters = elem.findtext('VOTERS')
        if voters:
            self.voters = [aionationstates.Nation(voter)
                           for voter in voters.split(':')]
        else:
            self.voters = []


class Poll(DataClassWithId):
    """A regional poll.

    Attributes
    ----------
    id : int
        The poll id.
    title : str
        The poll title.
    text : str or None
        The poll text.
    region : :class:`Region`
        Region the poll was posted in.
    author : :class:`Nation`
        Nation that posted the poll.
    options : list of :class:`PollOption`
        The poll options.
    """

    def __init__(self, elem):
        self.id = int(elem.get('id'))
        # Troublesome characters are cut from poll titles and texts, so
        # unscrambling is not necessary.
        self.title = html.unescape(elem.findtext('TITLE'))

        text = elem.findtext('TEXT')
        if text:
            self.text = html.unescape(text)
        else:
            self.text = None

        self.region = aionationstates.Region(elem.find('REGION').text)
        self.author = aionationstates.Nation(elem.find('AUTHOR').text)
        self.start = timestamp(elem.find('START').text)
        self.stop = timestamp(elem.find('STOP').text)
        self.options = [PollOption(option_elem)
                        for option_elem in elem.find('OPTIONS')]


class DispatchThumbnail(DataClassWithId):
    """A dispatch `thumbnail`, missing text.

    Attributes
    ----------
    id : int
        The dispatch id.
    title : str
        The dispatch title.
    author : :class:`Nation`
        Nation that posted the dispatch.
    category : str
        The dispatch category.
    subcategory : str
        The dispatch subcategory.
    views : int
        Number of times the dispatch got viewed.
    score : int
        Number of votes the dispatch received.
    created : naive UTC :class:`datetime.datetime`
        When the dispatch was created.
    edited : naive UTC :class:`datetime.datetime`
        When the dispatch last got edited.  Equal to ``created`` for
        dispatches that were never edited.
    """
    def __init__(self, **kwargs):
        for name, value in kwargs.items():
            setattr(self, name, value)

    def _update_from_elem(self, elem):
        self.id = int(elem.get('id'))
        self.title = unscramble_encoding(
            html.unescape(elem.find('TITLE').text))
        self.author = aionationstates.Nation(elem.find('AUTHOR').text)
        self.category = elem.find('CATEGORY').text
        self.subcategory = elem.find('SUBCATEGORY').text
        self.views = int(elem.find('VIEWS').text)
        self.score = int(elem.find('SCORE').text)

        created = int(elem.find('CREATED').text)
        # Otherwise it's 0 for dispatches that were never edited
        edited = int(elem.find('EDITED').text) or created
        self.created = timestamp(created)
        self.edited = timestamp(edited)

    @classmethod
    def _from_elem(cls, elem):
        self = cls()
        self._update_from_elem(elem)
        return self

    def full(self):
        """Request the full dispatch (with text).

        Returns
        -------
        an :class:`ApiQuery` of :class:`Dispatch`
        """
        return aionationstates.world.dispatch(self.id)

    def __eq__(self, other):
        # <DispatchThumbnail id=X> == <Dispatch id=X>
        if not isinstance(other, DispatchThumbnail):
            return NotImplemented
        return self.id == other.id

    __hash__ = DataClassWithId.__hash__


class Dispatch(DispatchThumbnail):
    """A full dispatch.

    Includes all of the attributes of :class:`DispatchThumbnail`, as
    well as:

    Attributes
    ----------
    text : str
        The dispatch text.
    """
    def __init__(self, elem):
        self.text = unscramble_encoding(html.unescape(elem.find('TEXT').text))
        super()._update_from_elem(elem)

    def __repr__(self):
        return f'<Dispatch id={self.id}>'


# Census data classes:

class CensusScaleCurrent:
    """Current World Census scale data.

    .. warning::

        With the exception of score, you must not expect the fields
        to update instantly.

        For the exact same reason of NationStates' excessive
        quirkiness, those fields may be missing (set to ``None``) on
        newly-founded nations (perhaps also in other cases, there is
        not a way to reliably test).  You will need to account for
        that in your code.

    Obviously, regions lack :attr:`rrank` and :attr:`prrank`, and the
    world only has :attr:`score`.

    Attributes
    ----------
    info : :class:`ScaleInfo`
        Static information about the scale.
    score : float
        The absolute census score.  All the other scale values are
        calculated (by NationStates) from scale scores of multiple
        nations.  Should always be present.
    rank : int or None
        World rank by the scale.
    prank : float or None
        Percentage World rank by the scale.
    rrank : int or None
        Regional rank by the scale.
    prrank : float or None
        Percentage Regional rank by the scale.
    """

    def __init__(self, elem):
        self.info = census_info[int(elem.get('id'))]
        self.score = float(elem.find('SCORE').text)
        # For recently-founded nations (and maybe in other cases as well, who
        # knows) the ranks & percentages may not show up even if requested.
        self.rank = self.prank = self.rrank = self.prrank = None
        with suppress(AttributeError, TypeError):
            self.rank = int(elem.find('RANK').text)
        with suppress(AttributeError, TypeError):
            self.prank = float(elem.find('PRANK').text)
        with suppress(AttributeError, TypeError):
            self.rrank = int(elem.find('RRANK').text)
        with suppress(AttributeError, TypeError):
            self.prrank = float(elem.find('PRRANK').text)

    def __repr__(self):
        return f'<CensusScaleCurrent #{self.info.id} {self.info.title}>'


class CensusPoint(namedtuple('CensusPoint', ['timestamp', 'score'])):
    """A namedtuple of what the scale score was on a particular date.

    Attributes
    ----------
    timestamp : naive UTC :class:`datetime.datetime`
        When the score was recorded.
    score : float
        What it was.
    """
    __slots__ = ()

    def __new__(cls, elem):
        stamp = timestamp(elem.find('TIMESTAMP').text)
        score = float(elem.find('SCORE').text)
        return super(cls, CensusPoint).__new__(cls, stamp, score)


class CensusScaleHistory:
    """Change of a World Census scale score through time.

    Attributes
    ----------
    info : :class:`ScaleInfo`
        Static information about the scale.
    history : list of :class:`CensusPoint`
        The actual data.
    """

    def __init__(self, elem):
        self.info = census_info[int(elem.get('id'))]
        self.history = [CensusPoint(sub_elem) for sub_elem in elem]

    def __repr__(self):
        return f'<CensusScaleHistory #{self.info.id} {self.info.title}>'


# Shared Census shards:

class Census:
    def census(self, *scales):
        """Current World Census data.

        By default returns data on today's featured World Census
        scale, use arguments to get results on specific scales.  In
        order to request data on all scales at once you can do
        ``x.census(*range(81))``.

        Parameters
        ----------
        scales : int
            World Census scales, integers between 0 and 85 inclusive.

        Returns
        -------
        an :class:`ApiQuery` of a list of :class:`CensusScaleCurrent`
        """
        params = {'mode': 'score+rank+rrank+prank+prrank'}
        if scales:
            params['scale'] = '+'.join(str(x) for x in scales)

        @api_query('census', **params)
        async def result(_, root):
            return [
                CensusScaleCurrent(scale_elem)
                for scale_elem in root.find('CENSUS')
            ]
        return result(self)

    def censushistory(self, *scales):
        """Historical World Census data.

        Was split into its own method for the sake of simplicity.

        By default returns data on today's featured World Census
        scale, use arguments to get results on specific scales.  In
        order to request data on all scales at once you can do
        ``x.censushistory(*range(81))``.

        Returns data for the entire length of history NationStates
        stores.  There is no way to override that.

        Parameters
        ----------
        scales : int
            World Census scales, integers between 0 and 85 inclusive.

        Returns
        -------
        an :class:`ApiQuery` of a list of :class:`CensusScaleHistory`
        """
        params = {'mode': 'history'}
        if scales:
            params['scale'] = '+'.join(str(x) for x in scales)

        @api_query('census', **params)
        async def result(_, root):
            return [
                CensusScaleHistory(scale_elem)
                for scale_elem in root.find('CENSUS')
            ]
        return result(self)


class ArchivedHappening:
    """A happening from a national or regional archive.

    Attributes
    ----------
    timestamp : naive UTC :class:`datetime.datetime`
        When the happening occured.
    text : str
        The happening text.
    """
    def __init__(self, elem):
        self.timestamp = timestamp(elem.find('TIMESTAMP').text)
        self.text = elem.findtext('TEXT')


# Shared shard for archived happenings:

class ArchivedHappenings:
    @api_query('happenings')
    async def happenings(self, root):
        """Happenings archived on the in-game page.  Newest to oldest.

        These happenings are not parsed because they are subtly
        different from the ones in the normal feed and I see no
        practical use-cases for having them parsed as well.

        Returns
        -------
        an :class:`ApiQuery` of a list of :class:`ArchivedHappening`
        """
        return [ArchivedHappening(elem) for elem in root.find('HAPPENINGS')]


class Zombie:
    """The situation in a nation/region during the annual Z-Day event.

    Attributes
    ----------
    survivors : int
        The number of citizens surviving, in millions.
    zombies : int
        The number of undead citizens, in millions.
    dead : int
        The number of dead citizens, in millions.
    action : str or None
        The nation's strategy for dealing with the disaster.  Either
        "research", "exterminate", or "export".  ``None`` if the
        instance represents regional situation.
    """

    def __init__(self, elem):
        self.survivors = int(elem.find('SURVIVORS').text)
        self.zombies = int(elem.find('ZOMBIES').text)
        self.dead = int(elem.find('DEAD').text)
        self.action = elem.findtext('ZACTION')


# Shards shared by Nation & Region APIs:

class NationRegion(DataClassWithId, ArchivedHappenings, Census):
    def __init__(self, name):
        self.id = normalize(name)

    @api_query('zombie')
    async def zombie(self, root):
        """State during the annual Z-Day event.

        Returns
        -------
        an :class:`ApiQuery` of :class:`Zombie`
        """
        return Zombie(root.find('ZOMBIE'))

    def __repr__(self):
        return f'<{type(self).__name__} "{self.id}">'


class CensusRank:
    """A nation ranked on World Census scale."""
    def __init__(self, elem):
        #: :class:`Nation`: The nation ranked.
        self.nation = aionationstates.Nation(elem.find('NAME').text)

        #: int: The nation's rank.
        self.rank = int(elem.find('RANK').text)

        #: float: The nation's score on the scale.
        self.score = float(elem.find('SCORE').text)


class CensusRanks:
    def _get_censusranks(self, scale, start):
        @api_query('censusranks', scale=scale, start=start)
        async def result(_, root):
            return [CensusRank(elem) for elem
                    in root.find('./CENSUSRANKS/NATIONS')]
        return result(self)

    async def censusranks(self, scale):
        """Iterate through nations ranked on the World Census scale.

        If the ranks change while you interate over them, they may be
        inconsistent.

        Parameters
        ----------
        scale : int
            A World Census scale, an integer between 0 and 85 inclusive.

        Returns
        -------
        asynchronous iterator of :class:`CensusRank`
        """
        order = count(1)
        for offset in count(1, 20):
            census_ranks = await self._get_censusranks(
                scale=scale, start=offset)
            for census_rank in census_ranks:
                assert census_rank.rank == next(order)
                yield census_rank
            if len(census_ranks) < 20:
                break
