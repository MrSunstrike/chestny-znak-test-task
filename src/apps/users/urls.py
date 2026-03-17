from django.shortcuts import render
from django.urls import path

app_name = "users"

urlpatterns = [
    path("", render, name="index"),
]
