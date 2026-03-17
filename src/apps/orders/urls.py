from django.shortcuts import render
from django.urls import path

app_name = "orders"

urlpatterns = [
    path("", render, name="index"),
]
