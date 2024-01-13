# views.py
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import render, redirect

def dashboardview(request):
    data = "hail"
    return render(request, 'index.html')