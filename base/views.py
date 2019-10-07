from django.shortcuts import render
from django.http import HttpResponse

from django.views.generic import ListView
from .models import Person


class PersonsList(ListView):
    model = Person
    template_name="persons.html"

def index(request):
    return HttpResponse("Hello, world. You're at the polls index. Update!")
