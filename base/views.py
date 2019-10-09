from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from django.views.generic import ListView
from .models import Person
import git


class PersonsList(ListView):
    model = Person
    template_name="persons.html"

def index(request):
    return HttpResponse("Hello, world. You're at the polls index. Update! 5!!!")

@csrf_exempt
def webhook(request):
    if request.method == 'GET':
        return HttpResponse("This path you can update server by POST requst")
    if request.method == 'POST':
        repo = git.Repo('./')
        origin = repo.remotes.origin

        origin.pull()
        #проверка dfd
        return HttpResponse('pong')
