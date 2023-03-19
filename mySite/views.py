from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse, Http404

def home(request):
    try:
        return redirect('myApp/home/')
    
    except:
        return Http404('404 Error')