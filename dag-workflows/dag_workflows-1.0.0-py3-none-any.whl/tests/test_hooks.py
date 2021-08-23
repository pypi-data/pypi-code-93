import responses

from workflows import bases, hooks


@responses.activate
def test_slack_hook(mocker):
    url = "http://test_url"
    responses.add(responses.POST, url)
    hook = hooks.make_slack_notification_hook(url, "message {exception}")
    mock_task = mocker.MagicMock(spec=bases.Task)()

    hook(bases.Event.TASK_FINISH, task=mock_task)
    assert len(responses.calls) == 0

    hook(bases.Event.TASK_FINISH, task=mock_task, exception=RuntimeError("some failure"))
    assert b"message some failure" in responses.calls[0].request.body
