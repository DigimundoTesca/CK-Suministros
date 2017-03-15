
# -*- encoding: utf-8 -*-
from __future__ import unicode_literals

from django.http import HttpResponse
from django.shortcuts import render
from diners.models import Diner

def pin(request, pin,date):
    print('PIN::::')
    print(pin)
    cadena = "ESTE ES TU PIN: " + pin

    return HttpResponse(cadena)


def diners(request):
    objects = Diner.objects.all()

    template = 'diners.html'
    title = 'Comensales del Dia'
    context={
        'titie' : title,
        'objects' : objects
    }
    return render(request, template, context)    
