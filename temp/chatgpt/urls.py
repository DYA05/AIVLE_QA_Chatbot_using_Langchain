# blog/urls.py
from django.urls import path
from django.contrib import admin
from . import views

app_name = 'chatgpt'
urlpatterns = [
    path("", views.chat_view, name='chat_view'),
    path('clear/', views.clear_chat_view, name='clear_chat'),
]