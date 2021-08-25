import logging

from mozilla_django_oidc.auth import OIDCAuthenticationBackend

logger = logging.getLogger(__name__)

class ExtraClaimsOIDCAuthenticationBackend(OIDCAuthenticationBackend):
    def create_user(self, claims):
        """Return object for a newly created user account."""
        
        email = claims.get('email')
        first_name = claims.get("given_name", "")
        last_name = claims.get("family_name", "")
        is_staff = claims.get("is_staff", False)
        is_active = claims.get("is_active", True)
        is_superuser = claims.get("is_superuser", False)

        username = self.get_username(claims)

        return self.UserModel.objects.create_user(username, email, first_name=first_name, last_name=last_name, is_staff=is_staff, is_active=is_active, is_superuser=is_superuser)
    
    def update_user(self, user, claims):
        has_changes = False

        email = claims.get('email')
        first_name = claims.get("given_name", "")
        last_name = claims.get("family_name", "")
        is_staff = claims.get("is_staff", False)
        is_active = claims.get("is_active", True)
        is_superuser = claims.get("is_superuser", False)

        if user.first_name != first_name:
            user.first_name = first_name
            has_changes = True
        
        if user.last_name != last_name:
            user.last_name = last_name
            has_changes = True
        
        if user.email != email:
            logger.info("Updating user email...")
            user.email = email
            has_changes = True
        
        if user.is_staff != is_staff:
            logger.info("Updating user staff status...")
            user.is_staff = is_staff
            has_changes = True
        
        if user.is_active != is_active:
            logger.info("Updating user active status...")
            user.is_active = is_active
            has_changes = True
        
        if user.is_superuser != is_superuser:
            logger.info("Updating super user status...")
            user.is_superuser = is_superuser
            has_changes = True
        
        if has_changes:
            user.save()

        return user
