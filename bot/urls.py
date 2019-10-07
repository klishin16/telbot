from django.conf.urls import url
from django.urls import path

#from .views import CommandReceiveView
from . import views

urlpatterns = [
    path('bot/<str:bot_token>/', views.inc, name='command'),
    #url(r'^bot/(?P<bot_token>.+)/$', CommandReceiveView.as_view(), name='command'),
]