from django.shortcuts import render, redirect

@login_required
def logout(req):
    auth_logout(req)
    return redirect("home:home")
