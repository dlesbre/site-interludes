from django.contrib.auth.mixins import UserPassesTestMixin

class SuperuserRequiredMixin(UserPassesTestMixin):
	"""Classe restreignant l'accès d'une vue aux superusers"""
	raise_exception = True
	permission_denied_message = "Seul les superutilisateurs ont accès à cette page"

	def test_func(self):
		user = self.request.user
		return user.is_authenticated and user.is_superuser
