from django.urls import path, include
from . import views

urlpatterns = [
    path('updateRider/', views.updateRiderView, name = 'updateRider'),
    path('appRiderSettings/', views.appRiderSettingsView, name = 'appRiderSettings'),
    path('appRiderHistory/', views.appRiderHistoryView, name = 'appRiderHistory'),
    path('appDriverHistory/', views.appDriverHistoryView, name = 'appDriverHistory'),
    path('appDriverSettings', views.appDriverSettingsView, name = 'appDriverSettings'),
    path('logout/', views.logoutView, name = 'logout'),
    path('app/', views.appView, name = 'app'),
    path('appRider/', views.appRiderView, name = 'appRider'),
    path('appDriver/', views.appDriverView, name = 'appDriver'),
    path('connected/', views.loginView, name = 'connected'),
    path('home/', views.home, name = 'home'),
    path('clientRegistered/', views.clientRegisteredView, name = 'clientRegistered'),
    path('registration/', views.registerView, name = 'register')
]

