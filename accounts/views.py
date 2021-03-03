from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from accounts.forms import CreateAccountForm

@login_required
def logout_view(request):
	"""Vue pour se deconnecter"""
	logout(request)
	return redirect("home")

def create_account(request):
	"""Vue pour l'inscription"""
	if request.method == 'POST':
		form = CreateAccountForm(request.POST)
		if form.is_valid():
			user = form.save()
			user.refresh_from_db()
			# load the profile instance created by the signal
			user.save()
			raw_password = form.cleaned_data.get('password1')

			# login user after signing up
			user = authenticate(email=user.email, password=raw_password)
			login(request, user)

			# redirect user to home page
			return redirect('home')
	else:
		form = CreateAccountForm()
	return render(request, 'registration/create_account.html', {'form': form})
