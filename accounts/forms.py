from django.contrib.auth.forms import UserCreationForm

from accounts.models import EmailUser

class CreateAccountForm(UserCreationForm):
	"""Form used to register a new user"""
	class Meta:
		model = EmailUser
		fields = ('email', 'first_name', 'last_name', 'password1', 'password2',)
