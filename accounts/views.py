from django.shortcuts import render, redirect
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required

@login_required
def logout(req):
    auth_logout(req)
    return redirect("home")
