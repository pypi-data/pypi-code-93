"""User Identity interface"""


class UserIdentityProvider:
    """An abstract class - something that tells you who the current user is"""
    def get_current_user(self) -> str:
        """Get an identification of the current user"""
        raise NotImplementedError()
