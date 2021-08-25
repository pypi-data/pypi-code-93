import json
import os
import uuid

from appdirs import user_config_dir


DEFAULT_REQUEST_PROMPT = """
To help improve the quality of our tools, we track basic
anonymized usage information so that we learn what features
are used and how people use them.

Here's an example of an event we would collect:
{event_data}

Your settings will be saved here and can be changed at any time:
{settings_path}

Can we collect anonymous usage data from your installation (y/N)?
"""


class CLSSettings:
    def __init__(self):
        self.project_slug = ""

        self.request_permission_prompt = DEFAULT_REQUEST_PROMPT
        self.invocation_id = str(uuid.uuid4())
        self.is_noninteractive = False
        self.noninteractive_tracking_enabled = False

        # Should not be accessed directly (can be overriden by env)
        self._project_key = ""
        self._debug = False

    def set_debug(self, value):
        self._debug = value

    def is_debug(self):
        if os.environ.get("CLS_DEBUG", "false").lower() in ("true", "1"):
            return True

        return self._debug

    def set_project_key(self, key):
        self._project_key = key

    def get_project_key(self):
        if "CLS_PROJECT_KEY" in os.environ:
            # For setting a different key in dev
            return os.environ["CLS_PROJECT_KEY"]

        return self._project_key

    def set_project_slug(self, slug):
        self.project_slug = slug

    def set_noninteractive_tracking(self, enabled, is_noninteractive):
        self.is_noninteractive = is_noninteractive
        self.noninteractive_tracking_enabled = enabled

    def set_request_permission_prompt(self, text):
        self.request_permission_prompt = text

    def get_api_url(self, path):
        base_url = os.environ.get("CLS_API_URL", "https://app.cls.dev/api/")
        return base_url.rstrip("/") + "/" + path.strip("/") + "/"

    def get_user_settings_path(self):
        return os.path.join(
            user_config_dir(f"{self.project_slug}_cls"), "settings.json"
        )

    def get_user_settings(self):
        path = self.get_user_settings_path()

        if os.path.exists(path):
            with open(path, "r") as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return {}

        return {}

    def set_user_setting(self, setting_name, setting_value):
        user_settings = self.get_user_settings()
        user_settings[setting_name] = setting_value

        path = self.get_user_settings_path()

        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))

        with open(path, "w+") as f:
            json.dump(user_settings, f, indent=2)

    def should_track(self, event_data={}):
        if self.is_noninteractive:
            return self.noninteractive_tracking_enabled

        already_enabled = self.get_user_settings().get("tracking_enabled", None)
        if already_enabled is not None:
            return already_enabled

        response = input(
            self.request_permission_prompt.strip().format(
                event_data=json.dumps(event_data, indent=2),
                settings_path=self.get_user_settings_path(),
            )
            + "\n",
        )
        tracking_enabled = response.lower() in ("y", "yes")

        self.set_user_setting("tracking_enabled", tracking_enabled)
        return tracking_enabled


settings = CLSSettings()
