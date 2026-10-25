"""Login with email or SRN plus password (REQ-21)."""
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q


class EmailOrSRNBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        identifier = (username or kwargs.get("email") or "").strip()
        if not identifier or password is None:
            return None

        user_model = get_user_model()
        try:
            user = user_model.objects.get(Q(email__iexact=identifier) | Q(srn__iexact=identifier))
        except (user_model.DoesNotExist, user_model.MultipleObjectsReturned):
            # Run the hasher anyway so a missing account takes as long as a wrong password.
            user_model().set_password(password)
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
