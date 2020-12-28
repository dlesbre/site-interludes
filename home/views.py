from django.shortcuts import render

def static_view(request, slug):
	return render(request, slug+'.html', {'slug': slug})
