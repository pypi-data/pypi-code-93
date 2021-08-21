import spotipy.oauth2 as oauth2
import webbrowser
import os
from lastipy import definitions

REDIRECT_URI = "https://www.example.com/callback/"


# TODO test
def get_token(username, client_id_key, client_secret_key):
    """Returns a Spotify token for the given user. If a cached token file exists (with the format .cache-<username>),
    it is returned; otherwise, the given user will be prompted to authorize the app.
    This function was copied from util.py in spotipy and modified in order to customize the path to the cached token."""

    # These are the only scopes required by this app so no need to parameterize this
    scope = (
        "playlist-modify-public user-library-read user-library-modify user-follow-read"
    )

    sp_oauth = oauth2.SpotifyOAuth(
        client_id_key,
        client_secret_key,
        REDIRECT_URI,
        scope=scope,
        cache_path=os.path.join(definitions.ROOT_DIR, ".cache-" + username),
    )

    token_info = sp_oauth.get_cached_token()

    if not token_info:
        print(
            """
            User authentication requires interaction with your
            web browser. Once you enter your credentials and
            give authorization, you will be redirected to
            a url.  Paste that url you were directed to to
            complete the authorization.
        """
        )
        auth_url = sp_oauth.get_authorize_url()
        try:
            webbrowser.open(auth_url)
            print("Opened %s in your browser" % auth_url)
        except:
            print("Please navigate here: %s" % auth_url)

        print()
        print()
        response = input("Enter the URL you were redirected to: ")

        print()
        print()

        code = sp_oauth.parse_response_code(response)
        token_info = sp_oauth.get_access_token(code)

    if token_info:
        return token_info["access_token"]
    else:
        return None
