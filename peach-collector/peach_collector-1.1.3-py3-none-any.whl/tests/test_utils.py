import pytest
from pytest_httpx import HTTPXMock

from peach_collector._utils import retry_with_backoff, RetryException, retry_secs


class CustomException(Exception):
    pass


def test_retry_secs():
    assert retry_secs(5, 3) == [1, 8, 27, 64, 125]


@pytest.mark.asyncio
async def test_retry_with_backoff(httpx_mock: HTTPXMock):

    call_counter = 0

    def test_coro(blow_up_count):
        async def blow_up():
            nonlocal call_counter
            call_counter += 1
            if call_counter <= blow_up_count:
                raise CustomException(f"boom {call_counter}")

        return blow_up

    call_counter = 0
    await retry_with_backoff(test_coro(blow_up_count=2), 3, 1.0, CustomException)
    assert call_counter == 3

    call_counter = 0
    with pytest.raises(RetryException):
        await retry_with_backoff(test_coro(blow_up_count=2), 2, 1.0)
    assert call_counter == 2

    class AnotherException(Exception):
        pass

    call_counter = 0
    with pytest.raises(CustomException):
        # If we get an another exception than we said we stop right away
        await retry_with_backoff(test_coro(blow_up_count=3), 1, 1.0, AnotherException)
    assert call_counter == 1
