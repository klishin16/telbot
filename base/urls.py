from django.urls import path

from . import views
from .views import PersonsList

urlpatterns = [
    path('', views.index, name='index'),
    path('persons/', PersonsList.as_view()),
    path('update_server/$', views.webhook, name='webhook'),
]