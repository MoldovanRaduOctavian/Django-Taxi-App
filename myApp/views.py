from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from . import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .decorators import driverDecorator, riderDecorator
from .models import *
from django.db.models import Q

# Create your views here.

def home(request):
    try:
        return render(request, 'login.html')
    
    except:
        return Http404('404 Error')


def registerView(request):
    try:

        return render(request, 'register.html')
    
    except:
        return Http404("404")

def clientRegisteredView(request):

    if request.method == 'POST':
        form = forms.RegistrationForm(request.POST)

        username = request.POST['username']
        email = request.POST['email']
        ps = request.POST['password1']

        if form.is_valid():
            user = form.save()
            return redirect(reverse('home'))
        
        return HttpResponse('Nu merge ok')

def loginView(request):

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username = username, password = password)

            if user is not None:
                login(request, user)
                return redirect(reverse('app'))

            else:
                return redirect(reverse('home'))
        
        else:
            return redirect(reverse('home'))
    else:
        return redirect(reverse('home'))

def appView(request):

    if request.user.is_authenticated:
        
        if request.user.isClient:
            return redirect(reverse('appRider'))
        
        else:
            return redirect(reverse('appDriver'))

    return redirect(reverse('home'))

@login_required
def logoutView(request):
    
    logout(request)
    return redirect(reverse('home'))

@login_required
@riderDecorator
def appRiderView(request):
    return render(request, 'demoRider.html')

@login_required
@driverDecorator
def appDriverView(request):
    return render(request, 'demoDriver.html')

@login_required
@riderDecorator
def appRiderSettingsView(request):
    return render(request, 'settingsRider.html')

@login_required
@riderDecorator
def updateRiderView(request):
    
    
        form = forms.RiderUpdateForm(data = request.GET, instance=request.user)

        if form.is_valid():
            
            form.save()
            return redirect(reverse('appRider'))
            # userForm.save()

        else:
            print(form.errors)
            return HttpResponse('A crapat')

@login_required
@riderDecorator
def appRiderHistoryView(request):
    objs = Trip.objects.filter(Q(rider = request.user) & (Q(status = Trip.FINISHED) | Q(status = Trip.CANCELED)))
    return render(request, 'historyRider.html', {'objs': objs})

@login_required
@driverDecorator
def appDriverHistoryView(request):
    driver = getDriverForUser(request.user)
    objs = Trip.objects.filter(Q(driver = driver) & (Q(status = Trip.CANCELED) | Q(status = Trip.FINISHED)))
    return render(request, 'historyDriver.html', {'objs': objs})

@login_required
@driverDecorator
def appDriverSettingsView(request):
    driver = getDriverForUser(request.user)
    return render(request, 'settingsDriver.html', {'driver': driver})