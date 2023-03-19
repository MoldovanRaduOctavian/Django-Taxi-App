from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test

def driverDecorator(function = None, redirect_field_name = REDIRECT_FIELD_NAME, login_url = 'home'):
    aux = user_passes_test(lambda x: x.is_active and x.isDriver, login_url = login_url, redirect_field_name = redirect_field_name)

    if function is not None:
        return aux(function)
    
    return aux

def riderDecorator(function = None, redirect_field_name = REDIRECT_FIELD_NAME, login_url = 'home'):
    aux = user_passes_test(lambda x: x.is_active and x.isClient, login_url = login_url, redirect_field_name = redirect_field_name)

    if function is not None:
        return aux(function)
    
    return aux
