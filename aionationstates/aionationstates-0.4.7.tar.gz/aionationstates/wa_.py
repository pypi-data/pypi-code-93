import enum
import html
from collections import namedtuple
from itertools import count, starmap
import datetime as dt

from aionationstates.utils import timestamp, DataClassWithId
from aionationstates.shared import ArchivedHappenings
from aionationstates.session import Session, api_query, NotFound
import aionationstates


__all__ = ('Proposal', 'VoteAction', 'DelegateVoteLogEntry',
           'VoteTrackEntry', 'ResolutionAtVote', 'Resolution', '_WA',
           'wa', '_WACouncil', 'ga', 'sc')


class _ProposalResolution(DataClassWithId):
    def __init__(self, elem):
        #: str: Name of the resolution.
        self.name = elem.find('NAME').text

        #: str: The resolution category.
        self.category = elem.find('CATEGORY').text

        #: str: The resolution text.  May contain BBCode.
        self.text = html.unescape(elem.find('DESC').text)

        #: naive UTC :class:`datetime.datetime`: When the resolution was
        #: proposed.
        self.submitted = timestamp(elem.find('CREATED').text)

        #: :class:`Nation`: The resolution author.
        self.author = aionationstates.Nation(elem.find('PROPOSED_BY').text)

        #: str: Whatever NationStates feels like.  Somewhat like a
        #: subcategory sometimes, though not really.  Sometimes
        #: represents resolution strength.
        self.option = elem.find('OPTION').text

        #: str: The proposal id, for example ``la_navasse_1521428163``.
        self.id = f'{self.author.id}_{elem.find("CREATED").text}'

    @property
    def _ga_or_sc(self):
        return {1: 'ga', 2: 'sc'}[self._council_id]

    @property
    def council(self):
        """str: ``General Assembly`` or ``Security Council``."""
        return {1: 'General Assembly', 2: 'Security Council'}[self._council_id]

    @property
    def target(self):
        """:class:`Nation`, :class:`Region`, or None: Target of a
        Liberation, Commendation, or Condemnation.  ``None`` if the
        resolution is not a Liberation, Commendation, or Condemnation.
        """
        if self.council == 'Security Council' and self.category != 'Repeal':
            # e.g. N:ever-wandering_souls
            entity_type, entity_name = self.option.split(':')
            entity_types = {
                'R': aionationstates.Region,
                'N': aionationstates.Nation
            }
            return entity_types[entity_type](entity_name)

    def repeal_target(self):
        """The resolution this resolution has repealed, or is attempting
        to repeal.

        Returns
        -------
        :class:`ApiQuery` of :class:`Resolution`

        Raises
        ------
        TypeError:
            If the resolution doesn't repeal anything.
        """
        if not self.category == 'Repeal':
            raise TypeError("This resolution doesn't repeal anything")
        return wa.resolution(int(self.option) + 1)


class Proposal(_ProposalResolution):
    """A World Assembly proposal."""

    def __init__(self, elem):
        approvers_text = elem.find('APPROVALS').text
        if not approvers_text:
            approvers = []
        else:
            approvers = [
                aionationstates.Nation(name)
                for name
                in approvers_text.split(':')
            ]

        #: list of :class:`Nation`: Delegates that approved this
        #: proposal.
        self.approved_by = approvers

        super().__init__(elem)

    @property
    def url(self):
        """str: URL to the proposal.  Expires when the vote on the
        proposal starts, or when it expires.
        """
        return ('https://www.nationstates.net/'
                f'page=UN_view_proposal/id={self.id}')

    @property
    def _council_id(self):
        # This assumes there isn't and never will be a GA resolution
        # with a name starting with Commend, Condemn, or Liberate
        if (
            self.category in ('Liberation', 'Commendation', 'Condemnation')
            or (
                self.category == 'Repeal'
                and (
                    # len('Repeal "') == 8
                    self.name.startswith('Liberate ', 8)
                    or self.name.startswith('Commend ', 8)
                    or self.name.startswith('Condemn ', 8)
                )
            )
        ):
            return 2  # Security Council
        else:
            return 1  # General Assembly


class VoteAction(enum.Enum):
    """How a nation votes on a resolution.

    Attributes
    ----------
    FOR
    AGAINST
    WITHDREW
    """
    FOR = 'FOR'
    AGAINST = 'AGAINST'
    WITHDREW = 'WITHDREW'


class DelegateVoteLogEntry:
    """An entry in the delegate vote log."""

    def __init__(self, elem):
        #: :class:`Nation`: The delegate nation.
        self.nation = aionationstates.Nation(elem.find('NATION').text)

        #: :class:`VoteAction`: Action the delegate took.
        self.action = VoteAction(elem.find('ACTION').text)

        #: int: The number of votes the delegate has.
        self.votes = int(elem.find('VOTES').text)

        #: naive UTC :class:`datetime.datetime`: When the event
        #: happened.
        self.timestamp = timestamp(elem.find('TIMESTAMP').text)


VoteTrackEntry = namedtuple('VoteTrackEntry', 'for_ against timestamp')
VoteTrackEntry.__doc__ = """\
A :any:`collections.namedtuple` of how many votes for & against the
resolution had at a particular point in time.

Attributes
----------
for_ : int
    The number of votes for the resolution.
against : int
    The number of votes against the resolution.
timestamp : :class:`datetime.datetime`
    When the above values were observed.
"""


class ResolutionAtVote(_ProposalResolution):
    """A World Assembly resolution at vote."""

    def __init__(self, elem):
        # _council_id is assigned in _WACouncil

        #: int: Number of votes for the resolution, including delegate
        #: votes.
        self.total_votes_for = int(elem.find('TOTAL_VOTES_FOR').text)

        #: int: Number of votes against the resolution, including
        #: delegate votes.
        self.total_votes_against = int(elem.find('TOTAL_VOTES_AGAINST').text)

        #: int: Number of nations who voted for the resolution.
        self.nation_votes_for = int(elem.find('TOTAL_NATIONS_FOR').text)

        #: int: Number of nations who voted against the resolution.
        self.nation_votes_against = int(
            elem.find('TOTAL_NATIONS_AGAINST').text)

        #: naive UTC :class:`datetime.datetime`: When the resolution was
        #: promoted to the voting floor.
        self.promoted = timestamp(elem.find('PROMOTED').text)

        #: list of :class:`DelegateVoteLogEntry`: Log of the delegate
        #: votes.
        self.delegate_vote_log = [
            DelegateVoteLogEntry(sub_elem)
            for sub_elem in elem.find('DELLOG')
        ]

        def text_as_int(elem): return int(elem.text)

        #: list of :class:`VoteTrackEntry`: Number of votes over time.
        self.vote_track = list(starmap(
            VoteTrackEntry,
            zip(
                map(text_as_int, elem.find('VOTE_TRACK_FOR')),
                map(text_as_int, elem.find('VOTE_TRACK_AGAINST')),
                (self.promoted + dt.timedelta(hours=1) * i for i in count())
            )
        ))

        #: list of :class:`Nation`: Nations who voted for the
        #: resolution.  Chronological, includes delegates.
        self.nations_voting_for = [
            aionationstates.Nation(sub_elem.text)
            for sub_elem in elem.find('VOTES_FOR')
        ]

        #: list of :class:`Nation`: Nations who voted against the
        #: resolution.  Chronological, includes delegates.
        self.nations_voting_against = [
            aionationstates.Nation(sub_elem.text)
            for sub_elem in elem.find('VOTES_AGAINST')
        ]

        super().__init__(elem)

    def _delegates_voting(self, option):
        def iterate():
            seen = set()
            for event in reversed(self.delegate_vote_log):
                if event.nation not in seen:
                    seen.add(event.nation)
                    if event.action is option:
                        yield event.nation, event.votes
        ret = list(iterate())
        ret.reverse()
        return ret

    @property
    def delegates_voting_for(self):
        """list of (:class:`Nation`, int) tuples: Delegates who voted
        for the resolution and the number of votes they have.

        In chronological order.
        """
        return self._delegates_voting(VoteAction.FOR)

    @property
    def delegates_voting_against(self):
        """list of (:class:`Nation`, int) tuples: Delegates who voted
        against the resolution and the number of votes they have.

        In chronological order.
        """
        return self._delegates_voting(VoteAction.AGAINST)

    @property
    def url(self):
        """str: URL to the council the proposal is being voted on at.
        Expires when the vote on the proposal ends.
        """
        return f'https://www.nationstates.net/page={self._ga_or_sc}'


class Resolution(_ProposalResolution):
    """A World Assembly resolution."""

    def __init__(self, elem):
        #: int: Index of the resolution irrespective of its councl.
        self.global_index = int(elem.find('RESID').text)

        #: int: Index of the resolution within its council.
        self.local_index = int(elem.find('COUNCILID').text)

        self._council_id = int(elem.find('COUNCIL').text)

        #: naive UTC :class:`datetime.datetime`: When the resolution was
        #: voted into law.
        self.implemented = timestamp(elem.find('IMPLEMENTED').text)

        #: int: Number of votes for the resolution, including delegate
        #: votes.
        self.total_votes_for = int(elem.find('TOTAL_VOTES_FOR').text)

        #: int: Number of votes against the resolution, including
        #: delegate votes.
        self.total_votes_against = int(elem.find('TOTAL_VOTES_AGAINST').text)

        super().__init__(elem)

    @property
    def promoted(self):
        """naive UTC :class:`datetime.datetime`: When the resolution was
        promoted to the voting floor.
        """
        # this tag isn't present on old resolutions
        return self.implemented - dt.timedelta(days=5)

    @property
    def url(self):
        """str: URL to the resolution."""
        return ('https://www.nationstates.net/'
                f'page=WA_past_resolution/id={self.global_index}')


# Don't you just love NS API design.

class _WAShared:
    def _call_api(self, params, **kwargs):
        params['wa'] = str(self._council_id)
        return super()._call_api(params, **kwargs)

    @api_query('proposals')
    async def proposals(self, root):
        """Resolution proposals.

        Returns
        -------
        :class:`ApiQuery` of list of :class:`Proposal`
        """
        return [Proposal(elem) for elem in root.find('PROPOSALS')]

    def resolution(self, index):
        """Resolution with a given index.

        Parameters
        ----------
        index : int
            Resolution index.

            Global if this is the ``aionationstates.wa`` object, local
            if this is ``aionationstates.ga`` or ``aionationstates.sc``.

        Returns
        -------
        :class:`ApiQuery` of :class:`Resolution`

        Raises
        ------
        :class:`NotFound`
            If a resolution with the requested index doesn't exist.
        """
        @api_query('resolution', id=str(index))
        async def result(_, root):
            elem = root.find('RESOLUTION')
            if not elem:
                raise NotFound(f'No resolution found with index {index}')
            return Resolution(elem)
        return result(self)


class _WA(_WAShared, ArchivedHappenings, Session):
    """General World Assembly shards.

    You shouldn't build this object yourself, it is already provided to
    you at ``aionationstates.wa``.
    """

    _council_id = 0

    @api_query('numnations')
    async def numnations(self, root):
        """The number of nations in the World Assembly.

        Returns
        -------
        an :class:`ApiQuery` of int
        """
        return int(root.find('NUMNATIONS').text)

    @api_query('members')
    async def nations(self, root):
        """All the nations in the World Assembly.

        Returns
        -------
        an :class:`ApiQuery` of a list of :class:`Nation` objects
        """
        text = root.find('MEMBERS').text
        return ([aionationstates.Nation(n) for n in text.split(',')]
                if text else [])

    @api_query('numdelegates')
    async def numdelegates(self, root):
        """The number of regional World Assembly delegates.

        Returns
        -------
        an :class:`ApiQuery` of int
        """
        return int(root.find('NUMDELEGATES').text)

    @api_query('delegates')
    async def delegates(self, root):
        """All the regional World Assembly delegates.

        Returns
        -------
        an :class:`ApiQuery` of a list of :class:`Nation` objects
        """
        text = root.find('DELEGATES').text
        return ([aionationstates.Nation(n) for n in text.split(',')]
                if text else [])


wa = _WA()


class _WACouncil(_WAShared, Session):
    """World Assembly shards specific to a council.

    You shouldn't build these objects yourself, the instances are
    already provided to you at ``aionationstates.ga`` and
    ``aionationstates.sc``.
    """

    def __init__(self, council_id):
        self._council_id = council_id

    @api_query('resolution', 'voters', 'votetrack', 'dellog')
    async def resolution_at_vote(self, root):
        """The proposal currently being voted on.

        Returns
        -------
        :class:`ApiQuery` of :class:`ResolutionAtVote`
        :class:`ApiQuery` of None
            If no resolution is currently at vote.
        """
        elem = root.find('RESOLUTION')
        if elem:
            resolution = ResolutionAtVote(elem)
            resolution._council_id = self._council_id
            return resolution


ga = _WACouncil(1)
sc = _WACouncil(2)
