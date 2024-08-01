# blog/urls.py
from django.urls import path
from django.contrib import admin
from . import views

app_name = 'selfchatgpt'
urlpatterns = [
    path("", views.chat_view, name='chat_view'),
    path('clear/', views.clear_chat_view, name='clear_chat'),
    path('load_chat/', views.load_chat, name='load_chat'),
]