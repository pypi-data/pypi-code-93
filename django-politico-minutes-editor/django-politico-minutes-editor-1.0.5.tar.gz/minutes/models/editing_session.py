import uuid
from django.utils import timezone
from django.contrib.postgres.fields import JSONField
from django.contrib.auth import get_user_model
from django.db import models
from django.conf import settings
from concurrency.exceptions import RecordModifiedError


class EditingSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    last_ping = models.DateTimeField(blank=True, null=True)
    active_id = models.CharField(max_length=100, blank=True, null=True)

    minute = models.ForeignKey(
        "Minute",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="editing_session",
        related_query_name="editing_session",
    )

    interstitial = models.ForeignKey(
        "Interstitial",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="editing_session",
        related_query_name="editing_session",
    )

    def __str__(self):
        if self.minute is not None:
            return "Session: {}".format(self.minute)
        elif self.interstitial is not None:
            return "Session: {}".format(self.interstitial)
        else:
            return "Null Session"

    def get_user_from_active_id(self):
        """
        Parses the active_id for a given user ID.
        Returns the user object that matches it.
        """
        user_id = self.active_id.split("|")[0]
        if user_id == "":
            return None

        User = get_user_model()
        u = User.objects.get(username=user_id)
        fname = u.first_name
        lname = u.last_name
        if (
            fname is not None
            and fname != ""
            and lname is not None
            and lname != ""
        ):
            return "{} {}".format(fname, lname)

        return u.username

    def open_session(self, id):
        """
        Sets the active_id to a given id and resets the last_ping.
        """
        self.active_id = id
        self.last_ping = timezone.now()
        self.save()
        return (True, "OK")

    def close_session(self, id):
        """
        Unsets the active_id and last_ping, if id matches.
        """
        if id == self.active_id:
            self.active_id = None
            self.last_ping = None
            self.save()
            return (True, "OK")
        else:
            return (False, "This is not the active session.")

    def request_new_session(self, id):
        """
        Requests to create a new session with a given ID.
        Returns whether or not the request was successful.
        """
        if self.active_id is None:
            self.open_session(id)
            return (True, "OK")
        else:
            if (
                timezone.now() - self.last_ping
            ).seconds > settings.MINUTES_INACTIVE_TIMEOUT:
                self.open_session(id)
                return (True, "OK")
            else:
                active_user = self.get_user_from_active_id()
                return (
                    False,
                    "{} is currently working on this page.".format(
                        active_user
                    ),
                )

    def ping(self, id):
        """
        Sets the last ping if the id matches.
        Returns whether or not the ping was accepted (and an error message).
        """
        if id == self.active_id:
            self.last_ping = timezone.now()
            return (True, "OK")
        elif self.active_id is not None:
            active_user = self.get_user_from_active_id()
            return (
                False,
                "You've been kicked out. {} is currently working on this page.".format(
                    active_user
                ),
            )
        else:
            return (False, "Someone kicked you out.")
