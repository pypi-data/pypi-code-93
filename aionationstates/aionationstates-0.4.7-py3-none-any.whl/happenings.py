"""Digest all NationStates happenings, extracting their type and useful data.

A great undertaking to be sure.
"""

import re
import html
import asyncio
from contextlib import suppress

from aionationstates.utils import timestamp, unscramble_encoding, logger
import aionationstates


class _ParseError(Exception):
    pass


class UnrecognizedHappening:
    """A happening that wasn't recognized by the system.

    Most likely cause of this is the futility of this measly effort
    against the inescapable and ever-growing chaos of our Universe.

    Not necessarily an error in the parsing system, rather an indicator
    of its incompleteness.

    Note that all the other classes in the `happenings` module inherit
    from this class, so all the attributes listed below are present on
    them as well.

    Attributes
    ----------
    id : int
        The happening id.
    timestamp : naive UTC :class:`datetime.datetime`
        Time of the happening.
    text : str
        The unparsed happening text.  May contain HTML tags and
        character references.  You generaly shouldn't have to use this.
    """
    def __init__(self, text, params):
        self.id, self.timestamp = params
        self.text = text

    def __eq__(self, other):
        if not isinstance(other, UnrecognizedHappening):
            return NotImplemented
        return self.id == other.id

    def __hash__(self):
        return hash((self.id,))

    def __repr__(self):
        return f'<Happening #{self.id}>'


# Main categories:

class Action(UnrecognizedHappening):
    """A direct action taken by a player.

    Attributes
    ----------
    agent : :class:`~aionationstates.Nation`
        The player who took the action.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        assert 'agent' in dir(self)


class Consequence(UnrecognizedHappening):
    """A result of previous actions."""


# Traits:

class Regional(UnrecognizedHappening):
    """An event taking place in a single region.

    Attributes
    ----------
    region : :class:`~aionationstates.Region`
        The region the event took place inside of.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        assert 'region' in dir(self)


class Affecting(UnrecognizedHappening):
    """An event passively involving a player.

    Attributes
    ----------
    patient : :class:`~aionationstates.Nation`
        The player who was passively involved in the event.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        assert 'patient' in dir(self)


# Nations doing things:

class Move(Action):
    """A nation moving regions.

    Attributes
    ----------
    region_from : :class:`~aionationstates.Region`
    region_to : :class:`~aionationstates.Region`
    """
    def __init__(self, text, params):
        match = re.match(
            r'@@(.+?)@@ relocated from %%(.+?)%% to %%(.+?)%%', text)
        if not match:
            raise _ParseError
        self.agent = aionationstates.Nation(match.group(1))
        self.region_from = aionationstates.Region(match.group(2))
        self.region_to = aionationstates.Region(match.group(3))
        super().__init__(text, params)


class Founding(Action, Regional):
    """A nation being founded."""
    def __init__(self, text, params):
        match = re.match('@@(.+?)@@ was founded in %%(.+?)%%', text)
        if not match:
            raise _ParseError
        self.agent = aionationstates.Nation(match.group(1))
        self.region = aionationstates.Region(match.group(2))
        super().__init__(text, params)


class Refounding(Action, Regional):
    """A nation being refounded."""
    def __init__(self, text, params):
        match = re.match('@@(.+?)@@ was refounded in %%(.+?)%%', text)
        if not match:
            raise _ParseError
        self.agent = aionationstates.Nation(match.group(1))
        self.region = aionationstates.Region(match.group(2))
        super().__init__(text, params)


class CTE(Consequence, Affecting, Regional):
    """A nation ceasing to exist."""
    def __init__(self, text, params):
        match = re.match('@@(.+?)@@ ceased to exist in %%(.+?)%%', text)
        if not match:
            raise _ParseError
        self.patient = aionationstates.Nation(match.group(1))
        self.region = aionationstates.Region(match.group(2))
        super().__init__(text, params)


class Legislation(Action):
    """A nation answering an issue.

    Attributes
    ----------
    effect_line : str
        May contain HTML elements and character references.
    """
    def __init__(self, text, params):
        match = re.match(
            r'Following new legislation in @@(.+?)@@, (.+)\.', text)
        if not match:
            raise _ParseError
        self.agent = aionationstates.Nation(match.group(1))
        self.effect_line = match.group(2)
        super().__init__(text, params)


class FlagChange(Action):
    """A nation altering its flag."""
    def __init__(self, text, params):
        match = re.match('@@(.+?)@@ altered its national flag', text)
        if not match:
            raise _ParseError
        self.agent = aionationstates.Nation(match.group(1))
        super().__init__(text, params)


class SettingsChange(Action):
    """A nation modifying its customizeable fields.

    Attributes
    ----------
    changes : dict with keys and values of str
        A mapping of field names (such as "currency", "motto", etc.) to
        their new values.
    """
    def __init__(self, text, params):
        match = re.match(
            '@@(.+?)@@ changed its national', text)
        if not match:
            raise _ParseError
        self.agent = aionationstates.Nation(match.group(1))
        self.changes = {}

        # If you harbor any sort of motivation to refactor this, feel free.
        index = text.index('@@ changed its national') + 23
        new_text = 'its' + text[index:]

        while True:
            # none of the fields are supposed to contain quotes
            match = re.search('its (.+?) to "(.+?)"', new_text)
            if not match:
                break
            value = unscramble_encoding(html.unescape(match.group(2)))
            self.changes[match.group(1)] = value
            new_text = new_text[len(match.group(0)):]

        super().__init__(text, params)


class DispatchPublication(Action):
    """A dispatch being published.

    In case you're wondering, deleting a dispatch doesn't produce a
    happening.

    Attributes
    ----------
    dispatch : :class:`~aionationstates.DispatchThumbnail`
    """
    def __init__(self, text, params):
        match = re.match(
            r'@@(.+?)@@ published "<a href="page=dispatch/id=(.+?)">(.+?)</a>" \((.+?): (.+?)\).',
            text
        )
        if not match:
            raise _ParseError
        self.agent = aionationstates.Nation(match.group(1))
        self.dispatch = aionationstates.DispatchThumbnail(
            id=int(match.group(2)),
            title=unscramble_encoding(html.unescape(match.group(3))),
            category=match.group(4),
            subcategory=match.group(5),
            views=1,
            score=1,
            # The happening timestamp
            created=params[1],
            edited=params[1]
        )
        super().__init__(text, params)


class CategoryChange(Consequence, Affecting):
    """A nation being reclassified to a different WA Category.

    Attributes
    ----------
    category_before : str
    category_after : str
    """
    def __init__(self, text, params):
        match = re.match(
            '@@(.+?)@@ was reclassified from "(.+?)" to "(.+?)".',
            text
        )
        if not match:
            raise _ParseError
        self.patient = aionationstates.Nation(match.group(1))
        self.category_before = match.group(2)
        self.category_after = match.group(3)
        super().__init__(text, params)


class BannerCreation(Action):
    """A nation creating a custom banner."""
    def __init__(self, text, params):
        match = re.match('@@(.+?)@@ created a custom banner.', text)
        if not match:
            raise _ParseError
        self.agent = aionationstates.Nation(match.group(1))
        super().__init__(text, params)


class MessageLodgement(Action, Regional):
    """A nation lodging a message on a regional message board."""
    def __init__(self, text, params):
        match = re.match(
            '@@(.+?)@@ lodged '
            '<a href="/region=.+?/page=display_region_rmb\\?postid=(.+?)#p.+?">a message</a> '
            'on the %%(.+?)%% Regional Message Board.',
            text
        )
        if not match:
            raise _ParseError
        self.agent = aionationstates.Nation(match.group(1))
        self._post_id = int(match.group(2))
        self.region = aionationstates.Region(match.group(3))
        super().__init__(text, params)

    async def post(self):
        """Get the message lodged.

        Returns
        -------
        an :class:`aionationstates.ApiQuery` of :class:`aionationstates.Post`
        """
        post = (await self.region._get_messages(
            fromid=self._post_id, limit=1))[0]
        assert post.id == self._post_id
        return post


# World Assembly:


class WorldAssembly(UnrecognizedHappening):
    """Base class for any event related to the World Assembly."""


class Endorsement(Action, Affecting):
    """A nation endorsing another nation."""
    def __init__(self, text, params):
        match = re.match('@@(.+?)@@ endorsed @@(.+?)@@', text)
        if not match:
            raise _ParseError
        self.agent = aionationstates.Nation(match.group(1))
        self.patient = aionationstates.Nation(match.group(2))
        super().__init__(text, params)


class EndorsementWithdrawal(Action, Affecting):
    """A nation withdrawing its endorsement of another nation."""
    def __init__(self, text, params):
        match = re.match(
            '@@(.+?)@@ withdrew its endorsement from @@(.+?)@@', text)
        if not match:
            raise _ParseError
        self.agent = aionationstates.Nation(match.group(1))
        self.patient = aionationstates.Nation(match.group(2))
        super().__init__(text, params)


class ResolutionVote(Action, WorldAssembly):
    """A nation voting on a WA resolution.

    Attributes
    ----------
    action : :class:`aionationstates.VoteAction`
    resolution_name : str
    """
    def __init__(self, text, params):
        match = re.match(
            '@@(.+?)@@ (.+?) the World Assembly Resolution "(.+?)".',
            text
        )
        if not match:
            raise _ParseError
        self.agent = aionationstates.Nation(match.group(1))
        if match.group(2) == 'voted for':
            self.action = aionationstates.VoteAction.FOR
        elif match.group(2) == 'voted against':
            self.action = aionationstates.VoteAction.AGAINST
        elif match.group(2) == 'withdrew its vote on':
            self.action = aionationstates.VoteAction.WITHDREW
        else:
            raise _ParseError
        self.resolution_name = match.group(3)
        super().__init__(text, params)

    async def resolution(self):
        """Get the resolution voted on.

        Returns
        -------
        awaitable of :class:`aionationstates.ResolutionAtVote`
            The resolution voted for.

        Raises
        ------
        aionationstates.NotFound
            If the resolution has since been passed or defeated.
        """
        resolutions = await asyncio.gather(
            aionationstates.ga.resolution_at_vote(),
            aionationstates.sc.resolution_at_vote(),
        )
        for resolution in resolutions:
            if (resolution is not None
                    and resolution.name == self.resolution_name):
                return resolution
        raise aionationstates.NotFound


class WorldAssemblyApplication(Action, WorldAssembly):
    """A nation applying to join the World Assembly."""
    def __init__(self, text, params):
        match = re.match(
            '@@(.+?)@@ applied to join the World Assembly.',
            text
        )
        if not match:
            raise _ParseError
        self.agent = aionationstates.Nation(match.group(1))
        super().__init__(text, params)


class WorldAssemblyAdmission(Action, WorldAssembly):
    """A nation being admitted to the World Assembly.

    This is an :class:`Action`, not a :class:`Consequence`, as WA
    admissions are a direct result of following an emailed link.
    """
    def __init__(self, text, params):
        match = re.match(
            '@@(.+?)@@ was admitted to the World Assembly.',
            text
        )
        if not match:
            raise _ParseError
        self.agent = aionationstates.Nation(match.group(1))
        super().__init__(text, params)


class WorldAssemblyResignation(Action, WorldAssembly):
    """A nation resigning from World Assembly."""
    def __init__(self, text, params):
        match = re.match(
            '@@(.+?)@@ resigned from the World Assembly.',
            text
        )
        if not match:
            raise _ParseError
        self.agent = aionationstates.Nation(match.group(1))
        super().__init__(text, params)


class _ProposalHappening:
    async def proposal(self):
        """Get the proposal in question.

        Actually just the first proposal with the same name, but the
        chance of a collision is tiny.

        Returns
        -------
        awaitable of :class:`aionationstates.Proposal`
            The proposal submitted.

        Raises
        ------
        aionationstates.NotFound
            If the proposal has since been withdrawn or promoted.
        """
        proposals = await aionationstates.wa.proposals()
        for proposal in proposals:
            if (proposal.name == self.proposal_name):
                return proposal
        raise aionationstates.NotFound


class ProposalSubmission(_ProposalHappening, Action, WorldAssembly):
    """A nation submitting a World Assembly proposal."""
    def __init__(self, text, params):
        match = re.match(
            '@@(.+?)@@ submitted a proposal to the '
            '(General Assembly|Security Council) (.+?) Board entitled "(.+?)"',
            text
        )
        if not match:
            raise _ParseError
        self.agent = aionationstates.Nation(match.group(1))

        #: str: ``General Assembly`` or ``Security Council``.
        self.proposal_council = match.group(2)

        #: str: The proposal category.
        self.proposal_category = match.group(3)

        #: str: Name of the proposal.
        self.proposal_name = match.group(4)

        super().__init__(text, params)


class ProposalApproval(_ProposalHappening, Action, WorldAssembly):
    """A delegate approving a World Assembly proposal."""
    def __init__(self, text, params):
        match = re.match(
            '@@(.+?)@@ approved the World Assembly proposal "(.+?)".',
            text
        )
        if not match:
            raise _ParseError
        self.agent = aionationstates.Nation(match.group(1))

        #: str: Name of the proposal.
        self.proposal_name = html.unescape(match.group(2))

        super().__init__(text, params)


# Regions doing things:

class RegionalAdministrative(Regional):
    """Base class for any action taken by regional administration, or a
    change thereof."""


class DelegateChange(Consequence, RegionalAdministrative):
    """A region changing World Assembly Delegates.

    Note that NationStates spreads this out to three distinct happening
    formats:

    - delegates changing;
    - a nation taking the free delegate position; and
    - a delegate being removed, leaving the position empty.

    As I believe this to be superfluous, this class represents all three.
    In case either the old of new delegate is missing, the corresponding
    attribute will be set to None.

    Attributes
    ----------
    new_delegate : :class:`~aionationstates.Nation` or None
    old_delegate : :class:`~aionationstates.Nation` or None
    """
    def __init__(self, text, params):
        match = re.match(
            '@@(.+?)@@ seized the position of %%(.+?)%% WA Delegate from @@(.+?)@@.',
            text
        )
        if match:
            self.new_delegate = aionationstates.Nation(match.group(1))
            self.region = aionationstates.Region(match.group(2))
            self.old_delegate = aionationstates.Nation(match.group(3))
            super().__init__(text, params)
            return

        match = re.match(
            '@@(.+?)@@ became WA Delegate of %%(.+?)%%.',
            text
        )
        if match:
            self.new_delegate = aionationstates.Nation(match.group(1))
            self.region = aionationstates.Region(match.group(2))
            self.old_delegate = None
            super().__init__(text, params)
            return

        match = re.match(
            '@@(.+?)@@ lost WA Delegate status in %%(.+?)%%.',
            text
        )
        if match:
            self.old_delegate = aionationstates.Nation(match.group(1))
            self.region = aionationstates.Region(match.group(2))
            self.new_delegate = None
            super().__init__(text, params)
            return

        raise _ParseError


class PollCreation(Action, RegionalAdministrative):
    """A nation creating a new regional poll.

    Note that the poll id is inaccessible from the happening, so the
    created poll can't be linked directly.  The best you can do is
    request the current poll of the region from the happening.

    Attributes
    ----------
    title : str
        Poll title.  Don't rely on this being accurate, some characters
        (such as brackets) are for whatever horror inducing reason
        stripped from the happening.
    """
    def __init__(self, text, params):
        match = re.match(
            '@@(.+?)@@ created a new poll in %%(.+?)%%: "(.+?)".', text)
        if not match:
            raise _ParseError
        self.agent = aionationstates.Nation(match.group(1))
        self.region = aionationstates.Region(match.group(2))
        self.title = html.unescape(match.group(3))
        super().__init__(text, params)


class PollDeletion(Action, RegionalAdministrative):
    """A nation deleting the regional poll."""
    def __init__(self, text, params):
        match = re.match(
            '@@(.+?)@@ deleted a regional poll in %%(.+?)%%.', text)
        if not match:
            raise _ParseError
        self.agent = aionationstates.Nation(match.group(1))
        self.region = aionationstates.Region(match.group(2))
        super().__init__(text, params)


class OfficerAppointment(Action, Affecting, RegionalAdministrative):
    """A nation appointing a Regional Officer.

    Attributes
    ----------
    title : str
        Title of the new officer.
    authority : :class:`~aionationstates.Authority`
        Authority of the new officer.
    """
    def __init__(self, text, params):
        match = re.match(
            # Officer titles can be blank if you confuse NS enough
            '@@(.+?)@@ appointed @@(.+?)@@ as (.*?) with authority over (.+?) in %%(.+?)%%',
            text
        )
        if not match:
            raise _ParseError
        self.agent = aionationstates.Nation(match.group(1))
        self.patient = aionationstates.Nation(match.group(2))
        self.title = match.group(3)
        self.authority = aionationstates.Authority._from_happening(match.group(4))
        self.region = aionationstates.Region(match.group(5))
        super().__init__(text, params)


class OfficerDismissal(Action, Affecting, RegionalAdministrative):
    """A nation dismissing a Regional Officer.

    Attributes
    ----------
    title : str
        Title the officer previously held.
    """
    def __init__(self, text, params):
        match = re.match(
            # Officer titles can be blank if you confuse NS enough
            '@@(.+?)@@ dismissed @@(.+?)@@ as (.*?) of %%(.+?)%%', text)
        if not match:
            raise _ParseError
        self.agent = aionationstates.Nation(match.group(1))
        self.patient = aionationstates.Nation(match.group(2))
        self.title = match.group(3)
        self.region = aionationstates.Region(match.group(4))
        super().__init__(text, params)


class DelegateModification(Action, RegionalAdministrative):
    """A founder modifying the authority of the World Assembly Delegate.

    Attributes
    ----------
    authority_granted : :class:`~aionationstates.Authority`
    authority_removed : :class:`~aionationstates.Authority`
    """
    def __init__(self, text, params):
        match = re.match(
            '@@(.+?)@@ '
            # granted X authority and removed Y authority from
            # granted X authority to
            # removed Y authority from
            '(?:granted (.+?) authority )?'
            '(?:and |to )?'
            '(?:removed (.+?) authority from )?'
            'the WA Delegate in %%(.+?)%%', text)
        if not match:
            raise _ParseError
        self.agent = aionationstates.Nation(match.group(1))
        self.authority_granted = aionationstates.Authority._from_happening(
            match.group(2) or '')
        self.authority_removed = aionationstates.Authority._from_happening(
            match.group(3) or '')
        self.region = aionationstates.Region(match.group(4))
        super().__init__(text, params)


class OfficerModification(Action, Affecting, RegionalAdministrative):
    """A founder or Delegate modifying one of the Regional Officers.

    Attributes
    ----------
    title : str
        Current title of the officer.
    old_title : str or None
        Title the officer previously held.  None if the office wasn't
        renamed.
    authority_granted : :class:`~aionationstates.Authority`
    authority_removed : :class:`~aionationstates.Authority`
    """
    def __init__(self, text, params):
        match = re.match(
            '@@(.+?)@@ '
            # granted X authority and removed Y authority from
            # granted X authority to
            # removed Y authority from
            '(?:granted (.+?) authority )?'
            '(?:and |to )?'
            '(?:removed (.+?) authority from )?'
            '@@(.+?)@@ '
            '(?:and renamed the office from "(.*?)" to "(.*?)" )?'
            '(?:as (.*?) )?'
            'in %%(.+?)%%', text)
        if match:
            self.agent = aionationstates.Nation(match.group(1))
            self.authority_granted = aionationstates.Authority._from_happening(
                match.group(2) or '')
            self.authority_removed = aionationstates.Authority._from_happening(
                match.group(3) or '')
            self.patient = aionationstates.Nation(match.group(4))
            self.old_title = match.group(5)
            self.title = match.group(6) or match.group(7)
            self.region = aionationstates.Region(match.group(8))
            super().__init__(text, params)
            return

        match = re.match(
            '@@(.+?)@@ renamed the office'
            ' held by @@(.*?)@@'
            ' from "(.*?)" to "(.*?)"'
            ' in %%(.+?)%%', text)
        if match:
            self.agent = aionationstates.Nation(match.group(1))
            self.authority_granted = aionationstates.Authority(0)
            self.authority_removed = aionationstates.Authority(0)
            self.patient = aionationstates.Nation(match.group(2))
            self.old_title = match.group(3)
            self.title = match.group(4)
            self.region = aionationstates.Region(match.group(5))
            super().__init__(text, params)
            return

        raise _ParseError


# Embassies:

class Embassy(UnrecognizedHappening):
    """Base class for any event related to an embassy between two
    regions.

    Attributes
    ----------
    regions : a frozenset of two :class:`~aionationstates.Region`
        Regions sharing an embassy.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        assert 'regions' in dir(self)


class EmbassyOrder(Action, RegionalAdministrative, Embassy):
    """Base class for any action affecting an embassy.

    Attributes
    ----------
    other_region : :class:`~aionationstates.Region`
        Region the embassy is with.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        assert 'other_region' in dir(self)

    @property
    def regions(self):
        return frozenset((self.region, self.other_region))


class EmbassyConstructionRequest(EmbassyOrder):
    """A nation proposing construction of embassies between two regions."""
    def __init__(self, text, params):
        match = re.match(
            '@@(.+?)@@ proposed constructing embassies between %%(.+?)%% and %%(.+?)%%.',
            text
        )
        if not match:
            raise _ParseError
        self.agent = aionationstates.Nation(match.group(1))
        self.region = aionationstates.Region(match.group(2))
        self.other_region = aionationstates.Region(match.group(3))
        super().__init__(text, params)


class EmbassyConstructionConfirmation(EmbassyOrder):
    """A nation accepting a request to construct embassies between two
    regions."""
    def __init__(self, text, params):
        match = re.match(
            '@@(.+?)@@ agreed to construct embassies between %%(.+?)%% and %%(.+?)%%.',
            text
        )
        if not match:
            raise _ParseError
        self.agent = aionationstates.Nation(match.group(1))
        self.region = aionationstates.Region(match.group(2))
        self.other_region = aionationstates.Region(match.group(3))
        super().__init__(text, params)


class EmbassyConstructionRequestWithdrawal(EmbassyOrder):
    """A nation withdrawing a request to construct embassies between two
    regions."""
    def __init__(self, text, params):
        match = re.match(
            '@@(.+?)@@ withdrew a request for embassies between %%(.+?)%% and %%(.+?)%%.',
            text
        )
        if not match:
            raise _ParseError
        self.agent = aionationstates.Nation(match.group(1))
        self.region = aionationstates.Region(match.group(2))
        self.other_region = aionationstates.Region(match.group(3))
        super().__init__(text, params)


class EmbassyConstructionAbortion(EmbassyOrder):
    """A nation aborting construction of embassies between two regions."""
    def __init__(self, text, params):
        match = re.match(
            '@@(.+?)@@ aborted construction of embassies between %%(.+?)%% and %%(.+?)%%.',
            text
        )
        if not match:
            raise _ParseError
        self.agent = aionationstates.Nation(match.group(1))
        self.region = aionationstates.Region(match.group(2))
        self.other_region = aionationstates.Region(match.group(3))
        super().__init__(text, params)


class EmbassyClosureOrder(EmbassyOrder):
    """A nation ordering closure of embassies between two regions."""
    def __init__(self, text, params):
        match = re.match(
            '@@(.+?)@@ ordered the closure of embassies between %%(.+?)%% and %%(.+?)%%.',
            text
        )
        if not match:
            raise _ParseError
        self.agent = aionationstates.Nation(match.group(1))
        self.region = aionationstates.Region(match.group(2))
        self.other_region = aionationstates.Region(match.group(3))
        super().__init__(text, params)


class EmbassyEstablishment(Consequence, Embassy):
    """An embassy being established between two regions."""
    def __init__(self, text, params):
        match = re.match(
            'Embassy established between %%(.+?)%% and %%(.+?)%%.',
            text
        )
        if not match:
            raise _ParseError
        self.regions = frozenset((
            aionationstates.Region(match.group(1)),
            aionationstates.Region(match.group(2))
        ))
        super().__init__(text, params)


class EmbassyCancellation(Consequence, Embassy):
    """Embassy being cancelled between two regions."""
    def __init__(self, text, params):
        match = re.match(
            'Embassy cancelled between %%(.+?)%% and %%(.+?)%%.',
            text
        )
        if not match:
            raise _ParseError
        self.regions = frozenset((
            aionationstates.Region(match.group(1)),
            aionationstates.Region(match.group(2))
        ))
        super().__init__(text, params)


# Z-Day:

class Zombie(Action, Affecting):
    """Base class for any Z-Day strike.

    Attributes
    ----------
    weapon : str
        Weapon type used, for example "Mk II (Sterilizer) Cure Missile".
    impact : int
        Citizens affected, in millions.
    """
    def __init__(self, match, text, params):
        self.patient = aionationstates.Nation(match.group(1))
        self.weapon = match.group(2)
        self.agent = aionationstates.Nation(match.group(3))
        self.impact = int(match.group(4))
        super().__init__(text, params)


class ZombieCure(Zombie):
    """A nation curing another nation during Z-Day."""
    def __init__(self, text, params):
        match = re.match(
            '@@(.+?)@@ was struck by a (.+?) from @@(.+?)@@, curing ([0-9]+) million infected.',
            text
        )
        if not match:
            raise _ParseError
        super().__init__(match, text, params)


class ZombieKill(Zombie):
    """A nation cleansing another nation during Z-Day."""
    def __init__(self, text, params):
        match = re.match(
            '@@(.+?)@@ was cleansed by a (.+?) from @@(.+?)@@, killing ([0-9]+) million zombies.',
            text
        )
        if not match:
            raise _ParseError
        super().__init__(match, text, params)


class ZombieInfect(Zombie):
    """A nation infecting another nation during Z-Day.

    Attributes
    ----------
    convert : bool
        Whether the nation is converted to a zombie exporter.
    """
    def __init__(self, text, params):
        match = re.match(
            '@@(.+?)@@ was ravaged by a (.+?) from @@(.+?)@@, infecting ([0-9]+) million survivors.',
            text
        )
        if not match:
            raise _ParseError
        self.convert = text.endswith('converting to a zombie exporter! Oh no!')
        super().__init__(match, text, params)


class ZombieBorderControlActivation(Action, RegionalAdministrative):
    """A nation activating regional border control during Z-Day.

    Attributes
    ----------
    type : str
        Type of lockdown.  Currently either 'Lockdown' or 'Keycode'.
    """
    def __init__(self, text, params):
        match = re.match(
            '@@(.+?)@@ instituted (.*?) Zombie Border Control in %%(.+?)%%', text)
        if not match:
            raise _ParseError
        self.agent = aionationstates.Nation(match.group(1))
        self.type = match.group(2)
        self.region = aionationstates.Region(match.group(3))
        super().__init__(text, params)


class ZombieBorderControlDeactivation(Action, RegionalAdministrative):
    """A nation removing regional border control during Z-Day."""
    def __init__(self, text, params):
        match = re.match(
            '@@(.+?)@@ removed Zombie Border Control in %%(.+?)%%', text)
        if not match:
            raise _ParseError
        self.nation = aionationstates.Nation(match.group(1))
        self.region = aionationstates.Region(match.group(2))
        super().__init__(text, params)


def _submost_classes(classes):
    for cls in classes:
        subclasses = cls.__subclasses__()
        if not subclasses:
            yield cls
        else:
            yield from _submost_classes(subclasses)


_happening_classes = list(
    _submost_classes(UnrecognizedHappening.__subclasses__()))


def process_happening(elem):
    # Call ElementTree methods only once, to get a bit of extra performance.
    params_id = int(elem.get('id'))
    params_timestamp = timestamp(elem.find('TIMESTAMP').text)
    text = elem.findtext('TEXT')
    params = (text, (params_id, params_timestamp))

    for cls in _happening_classes:
        with suppress(_ParseError):
            return cls(*params)

    logger.error(f'could not process happening {params_id}')

    return UnrecognizedHappening(*params)
