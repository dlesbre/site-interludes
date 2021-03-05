from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.http import Http404
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.urls import reverse
from django.template.loader import render_to_string
from django.views.generic import RedirectView, View
from django.shortcuts import render, redirect

from accounts.forms import CreateAccountForm
from accounts.models import EmailUser
from accounts.tokens import email_token_generator
from site_settings.models import SiteSettings

@login_required
def logout_view(request):
	"""Vue pour se deconnecter"""
	logout(request)
	return redirect("home")

class CreateAccountView(View):
	"""Vue pour la creation de compte"""
	form_class = CreateAccountForm
	template_name = 'registration/create_account.html'

	@staticmethod
	def check_creation_allowed():
		"""Vérifie que la création de compte est authorisée
		Renvoie un 404 si ce n'est pas le cas"""
		settings = SiteSettings.load()
		if not settings.registrations_open:
			raise Http404("La création de compte n'est pas ouverte actuellement")

	def get(self, request, *args, **kwargs):
		"""handle get requests"""
		self.check_creation_allowed()
		form = self.form_class()
		return render(request, self.template_name, {'form': form})

	def post(self, request, *args, **kwargs):
		"""handle post requests"""
		self.check_creation_allowed()
		form = self.form_class(request.POST)
		if not form.is_valid():
			return render(request, self.template_name, {'form': form})

		user = form.save()
		user.is_active = False # can't login until email validation
		user.email_confirmed = False

		current_site = get_current_site(request)
		subject = 'Activation de votre compte Interludes'
		message = render_to_string('registration/activation_email.html', {
			'user': user,
			'domain': current_site.domain,
			'uid': urlsafe_base64_encode(force_bytes(user.pk)),
			'token': email_token_generator.make_token(user),
		})
		user.email_user(subject, message)

		user.save()

		messages.success(request, ('Please Confirm your email to complete registration.'))

		return redirect('accounts:login')

class ActivateAccountView(RedirectView):

	permanent = False

	def get_redirect_url(self, uidb64, token, *args, **kwargs):
		try:
			uid = urlsafe_base64_decode(uidb64).decode()
			user = EmailUser.objects.get(pk=uid)
		except (TypeError, ValueError, OverflowError, EmailUser.DoesNotExist):
			messages.error(
				self.request,
				"Le lien de confirmation d'adresse mail ne correspond à aucun·e "
				"utilisateur·ice inscrit·e",
			)
			return reverse("home")

		if not email_token_generator.check_token(user, token):
			messages.error(
				self.request,
				"Le lien de confirmation d'adresse mail est invalide ou déjà utilisé",
			)
			return reverse("home")

		user.is_active = True
		user.email_confirmed = True
		user.save()
		login(self.request, user)
		messages.info(self.request, "Votre adresse email a bien été confirmée.")
		return reverse("home")
