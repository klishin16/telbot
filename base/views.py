from django.shortcuts import render
from django.http import HttpResponse

from django.views.generic import ListView
from .models import Person
import git


class PersonsList(ListView):
    model = Person
    template_name="persons.html"

def index(request):
    return HttpResponse("Hello, world. You're at the polls index. Update!")

def webhook(request):
    if request.method == 'GET':
        return HttpResponse("This path you can update server by POST requst")
    if request.method == 'POST':
        repo = git.Repo('../')
        origin = repo.remotes.origin

        origin.pull()
        return 'Updated Pythonanywhere successfully', 200
    else:
        return 'Wrong event type', 400
