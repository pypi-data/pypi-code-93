from . import email
from . import slack

_all_providers = {
    "email": email.Email,
    "slack": slack.Slack
}