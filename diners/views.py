
# -*- encoding: utf-8 -*-
from __future__ import unicode_literals

from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from diners.models import AccessLog
from django.views.decorators.csrf import csrf_exempt

from .models import AccessLog, Diner

@csrf_exempt
def RFID(request):
    if request.method == 'POST':
        rfid = request.POST['rfid']
        
        if rfid is None:
            print('No hay RFID: ', rfid)
        else:
            print('RECIBIDO EL RFID: ', rfid)
            try:
                diner = Diner.objects.get(RFID=rfid)
                new_access_log = AccessLog(diner=diner)
                new_access_log.save()    
            except Diner.DoesNotExist:
                diner = None
            print('DINER:::', diner)

        return HttpResponse('Operacion Terminada\n')

    else:
        return redirect('diners:diners')


def diners(request):
    objects = AccessLog.objects.all().prefetch_related('diner')

    template = 'diners.html'
    title = 'Comensales del Dia'
    context={
        'titie' : title,
        'objects' : objects
    }
    return render(request, template, context)    
