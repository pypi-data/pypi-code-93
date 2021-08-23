"""A set of tests for the bridgeobjects Call class."""
from ..source.call import Call
from ..source.denomination import Denomination


def test_call_name():
    """Ensure that the call name is correct."""
    assert Call('1S').name == '1S'
    assert Call('3C').name == '3C'
    assert Call('4H').name == '4H'
    assert Call('5D').name == '5D'
    assert Call('3NT').name == '3NT'
    assert Call('P').name == 'P'
    assert Call('D').name == 'D'


def test_call_repr():
    """Ensure that the call repr is correct."""
    assert repr(Call('1S')) == 'Call("1S")'
    assert repr(Call('3C')) == 'Call("3C")'
    assert repr(Call('4H')) == 'Call("4H")'
    assert repr(Call('5D')) == 'Call("5D")'
    assert repr(Call('3NT')) == 'Call("3NT")'
    assert repr(Call('P')) == 'Call("P")'
    assert repr(Call('D')) == 'Call("D")'


def test_call_str():
    """Ensure that the call str is correct."""
    assert str(Call('1S')) == 'Call("1S")'
    assert str(Call('3C')) == 'Call("3C")'
    assert str(Call('4H')) == 'Call("4H")'
    assert str(Call('5D')) == 'Call("5D")'
    assert str(Call('3NT')) == 'Call("3NT")'
    assert str(Call('P')) == 'Call("P")'
    assert str(Call('D')) == 'Call("D")'


def test_call_level():
    """Ensure that the call level is correct."""
    assert Call('1S').level == 1
    assert Call('3C').level == 3
    assert Call('4H').level == 4
    assert Call('5D').level == 5
    assert Call('3NT').level == 3
    assert Call('P').level == 0
    assert Call('D').level == 0


def test_call_suit():
    """Ensure that the call denomination is correct."""
    assert Call('1S').denomination == Denomination('S')
    assert Call('3C').denomination == Denomination('C')
    assert Call('4H').denomination == Denomination('H')
    assert Call('5D').denomination == Denomination('D')
    assert Call('3NT').denomination == Denomination('NT')
    assert Call('P').denomination == Denomination('')
    assert Call('D').denomination == Denomination('')


def test_call_is_major():
    """Ensure that the call is_major is correct."""
    assert Call('1S').is_major
    assert Call('4H').is_major
    assert not Call('3C').is_major
    assert not Call('5D').is_major
    assert not Call('3NT').is_major
    assert not Call('P').is_major
    assert not Call('D').is_major


def test_call_is_minor():
    """Ensure that the call is_minor is correct."""
    assert not Call('1S').is_minor
    assert not Call('4H').is_minor
    assert Call('3C').is_minor
    assert Call('5D').is_minor
    assert not Call('3NT').is_minor
    assert not Call('P').is_minor
    assert not Call('D').is_minor


def test_call_is_suit_call():
    """Ensure that the call is_suit_call is correct."""
    assert Call('1S').is_suit_call
    assert Call('4H').is_suit_call
    assert Call('3C').is_suit_call
    assert Call('5D').is_suit_call
    assert not Call('3NT').is_suit_call
    assert not Call('P').is_suit_call
    assert not Call('D').is_suit_call


def test_call_is_no_trumps():
    """Ensure that the call is_no_trumps is correct."""
    assert not Call('1S').is_no_trumps
    assert not Call('4H').is_no_trumps
    assert not Call('3C').is_no_trumps
    assert not Call('5D').is_no_trumps
    assert Call('3NT').is_no_trumps
    assert not Call('P').is_no_trumps
    assert not Call('D').is_no_trumps


def test_call_is_nt():
    """Ensure that the call is_no_trumps is correct."""
    assert not Call('1S').is_nt
    assert not Call('4H').is_nt
    assert not Call('3C').is_nt
    assert not Call('5D').is_nt
    assert Call('3NT').is_nt
    assert not Call('P').is_nt
    assert not Call('D').is_nt


def test_call_is_pass_or_double():
    """Ensure that the call is_pass_or_double is correct."""
    assert not Call('1S').is_pass_or_double
    assert not Call('4H').is_pass_or_double
    assert not Call('3C').is_pass_or_double
    assert not Call('5D').is_pass_or_double
    assert not Call('3NT').is_pass_or_double
    assert Call('P').is_pass_or_double
    assert Call('D').is_pass_or_double


def test_call_is_pass():
    """Ensure that the call is_pass is correct."""
    assert not Call('1S').is_pass
    assert not Call('4H').is_pass
    assert not Call('3C').is_pass
    assert not Call('5D').is_pass
    assert not Call('3NT').is_pass
    assert Call('P').is_pass
    assert not Call('D').is_pass


def test_call_is_double():
    """Ensure that the call is_double is correct."""
    assert not Call('1S').is_double
    assert not Call('4H').is_double
    assert not Call('3C').is_double
    assert not Call('5D').is_double
    assert not Call('3NT').is_double
    assert not Call('P').is_double
    assert Call('D').is_double
    assert not Call('R').is_double


def test_call_is_redouble():
    """Ensure that the call is_redouble is correct."""
    assert not Call('1S').is_redouble
    assert not Call('4H').is_redouble
    assert not Call('3C').is_redouble
    assert not Call('5D').is_redouble
    assert not Call('3NT').is_redouble
    assert not Call('P').is_redouble
    assert not Call('D').is_redouble
    assert Call('R').is_redouble


def test_call_is_value_call():
    """Ensure that the call is_value_call is correct."""
    assert Call('1S').is_value_call
    assert Call('4H').is_value_call
    assert Call('3C').is_value_call
    assert Call('5D').is_value_call
    assert Call('3NT').is_value_call
    assert not Call('P').is_value_call
    assert not Call('D').is_value_call
    assert not Call('R').is_value_call


def test_call_is_game():
    """Ensure that the call is_game is correct."""
    assert not Call('1S').is_game
    assert Call('5H').is_game
    assert not Call('3C').is_game
    assert Call('5D').is_game
    assert Call('3NT').is_game
    assert not Call('P').is_game
    assert not Call('D').is_game
    assert not Call('R').is_game


def test_call_equality():
    """Ensure that the call equality is correct."""
    assert Call('1S') == Call('1S')
    assert not Call('4H') == Call('1S')
    assert not Call('3C') == Call('R')
    assert not Call('5D') == Call('P')
    assert Call('3NT') == Call('3NT')


def test_call_inequality():
    """Ensure that the call inequality is correct."""
    assert Call('1S') != None
    assert not Call('1S') != Call('1S')
    assert Call('4H') != Call('1S')
    assert Call('3C') != Call('R')
    assert Call('5D') != Call('P')
    assert not Call('3NT') != Call('3NT')


def test_call_greater_than():
    """Ensure that the call greater_than is correct."""
    assert Call('1S') > Call('1H')
    assert not Call('1S') > Call('1S')
    assert not Call('1S') > Call('4H')
    assert Call('3C') > Call('R')
    assert Call('5D') > Call('P')
    assert not Call('3NT') > Call('3NT')


def test_call_greater_than_or_equal():
    """Ensure that the call greater_than_or_equal is correct."""
    assert Call('1S') >= Call('1H')
    assert Call('1S') >= Call('1S')
    assert not Call('1S') >= Call('4H')
    assert Call('3C') >= Call('R')
    assert Call('5D') >= Call('P')
    assert Call('3NT') >= Call('3NT')


def test_call_less_than():
    """Ensure that the call less_than is correct."""
    assert Call('1H') < Call('1S')
    assert not Call('1S') < Call('1S')
    assert Call('1S') < Call('4H')
    assert not Call('3C') < Call('R')
    assert not Call('5D') < Call('P')
    assert not Call('3NT') < Call('3NT')


def test_call_less_than_or_equal():
    """Ensure that the call less_than_or_equal is correct."""
    assert not Call('1S') <= Call('1H')
    assert Call('1S') <= Call('1S')
    assert Call('1S') <= Call('4H')
    assert not Call('3C') <= Call('R')
    assert not Call('5D') <= Call('P')
    assert Call('3NT') <= Call('3NT')
