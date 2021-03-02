from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from home.models import InterludesParticipant

class CreateAccountForm(UserCreationForm):
	"""Form used to register a new user"""
	class Meta:
		model = User
		fields = ('username', 'password1', 'password2',)
