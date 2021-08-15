from django.utils.translation import gettext_lazy as _


def get_context_explanation():
    return [
        {
            "name": "confirmation_link",
            "explanation": _("Link to confirm a proposal after it has been accepted."),
        },
        {
            "name": "event_name",
            "explanation": _("The event's full name."),
        },
        {
            "name": "submission_title",
            "explanation": _(
                "The title of the proposal in question. Only usable in default templates."
            ),
        },
        {
            "name": "submission_url",
            "explanation": _(
                "The link to a proposal. Only usable in default templates."
            ),
        },
        {
            "name": "speakers",
            "explanation": _("The name(s) of all speakers in this proposal."),
        },
        {
            "name": "submission_type",
            "explanation": _("The proposal type. Only usable in default templates."),
        },
        {
            "name": "track_name",
            "explanation": _("The track the proposal belongs to"),
        },
    ]


def template_context_from_event(event):
    return {
        "all_submissions_url": event.urls.user_submissions.full(),
        "event_name": event.name,
    }


def template_context_from_submission(submission):
    context = template_context_from_event(submission.event)
    context.update(
        {
            "confirmation_link": submission.urls.confirm.full(),
            "submission_title": submission.title,
            "submission_url": submission.urls.user_base.full(),
            "speakers": submission.display_speaker_names,
            "orga_url": submission.orga_urls.base.full(),
            "submission_type": str(submission.submission_type.name),
            "track_name": str(submission.track.name) if submission.track else None,
        }
    )
    return context
