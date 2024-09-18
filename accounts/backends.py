from datetime import timedelta
from typing import Optional
from urllib.parse import urlunparse

from cas import CASClient
from django.contrib import messages
from django.contrib.auth.backends import BaseBackend
from django.db import transaction
from django.http import HttpRequest
from django.utils.timezone import now

from accounts.models import ClipperAccount, EmailUser


def get_cas_client(request: HttpRequest) -> CASClient:
    """Return a CAS client configured for SPI's CAS."""
    return CASClient(
        version=3,
        service_url=urlunparse((request.scheme, request.get_host(), request.path, "", "", "")),
        server_url="https://cas.eleves.ens.fr/",
    )


class ClipperCASBackend(BaseBackend):
    """AuthENS CAS authentication backend.

    Implement standard CAS v3 authentication and handles username clashes with non-CAS
    accounts and potential old CAS accounts.

    Every user connecting via CAS is given an `authens.models.CASAccount` instance which
    remembers her CAS login and her entrance year (the year her CAS account was
    created).
    At each connection, we search for a CAS account with the given CAS login and create
    one if none exists. In case the CAS account's entrance year does not match the
    entrance year given by CAS, it means it is a old account and it must be deleted. The
    corresponding user can still connect using regular Django authentication.
    """

    def authenticate(self, request: Optional[HttpRequest], ticket=None, **kwargs) -> Optional[EmailUser]:
        if request is None:
            return None
        cas_client = get_cas_client(request)
        cas_login, attributes, _ = cas_client.verify_ticket(ticket)

        print(attributes)
        homedir = attributes.get("homeDirectory")
        email = attributes.get("email")

        if cas_login is None or homedir is None or email is None:
            # Authentication failed
            return None
        cas_login = self.clean_cas_login(cas_login)

        # if request:
        #     request.session["CASCONNECTED"] = True

        return self.get_or_create(request, cas_login, email=email, homedir=homedir)

    def clean_cas_login(self, cas_login: str) -> str:
        return cas_login.strip().lower()

    def get_unique_id(self, cas_login: str, homedir: str, email: str) -> str:
        """Clipper usernames aren't unique accross many years, hopefully this ID is"""
        return cas_login + "#" + homedir

    def create_user(self, cas_login: str, homedir: str, email: str) -> EmailUser:
        """Create a CAS user, base method that can be overrided to add more
        information.
        """
        user = EmailUser.objects.create_user(email=email, password=EmailUser.objects.make_random_password())  # type: ignore
        ClipperAccount.objects.create(
            user=user, unique_id=self.get_unique_id(cas_login, homedir, email), clipper_login=cas_login
        )
        return user

    def get_or_create(self, request: HttpRequest, cas_login: str, email: str, homedir: str) -> Optional[EmailUser]:
        """Handles account retrieval, creation and invalidation as described above.

        - If no CAS account exists, create one;
        - If a CAS account exists, but with the wrong entrance year, convert it to
        an OldCASAccount instance, and create a fresh CAS Account with the correct year.
        - If a matching CAS account exists, retrieve it.
        """

        uid = self.get_unique_id(cas_login, homedir, email)
        with transaction.atomic():
            try:
                user = EmailUser.objects.get(email=email)
                if user.clipper_account is None or user.clipper_account.unique_id != uid:
                    # Non-clipper user with account exists or other clipper account exists
                    if (
                        user.last_login is None or now() - user.last_login >= timedelta(days=30.0 * 6.0)
                    ) and not user.is_superuser:
                        # Non-superuser, last login was 6 month ago, probably safe to delete
                        user.delete()
                        raise EmailUser.DoesNotExist

                    if user.clipper_account is None:
                        messages.error(
                            request,
                            "L'email {} est déjà associé à un compte non-clipper. Utilisez le formulaire de connexion classique.".format(
                                email
                            ),
                        )
                    else:
                        messages.error(
                            request,
                            "Impossible de se connecter avec ce compte clipper, un autre compte clipper du même identifiant est déjà présent",
                        )
                    return None
            except EmailUser.DoesNotExist:
                return self.create_user(cas_login, homedir, email)
        return None

    # Django boilerplate.
    def get_user(self, user_id) -> Optional[EmailUser]:
        try:
            return EmailUser.objects.get(pk=user_id)
        except EmailUser.DoesNotExist:
            return None
