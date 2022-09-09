from django.contrib.auth import get_user_model
from cas_server.auth import AuthUser, DjangoAuthUser

class InterLudesAuthUser(DjangoAuthUser):  # pragma: no cover
    """
        Overrides DjangoAuthUser constructor
    """

    def __init__(self, username):
        User = get_user_model()
        try:
            self.user = User.objects.get(email=username)
        except User.DoesNotExist:
            pass
        super(DjangoAuthUser, self).__init__(username)