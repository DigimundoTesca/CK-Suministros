
# -*- encoding: utf-8 -*-
from __future__ import unicode_literals

from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from diners.models import AccessLog
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator

from .models import AccessLog, Diner
from cloudkitchen.settings.base import PAGE_TITLE

def diners_paginator(request, queryset, num_pages):
    result_list = Paginator(queryset, num_pages)

    try:
        num_page = int(request.GET['num_page'])
    except:
        num_page = 1

    if num_page <= 0:
        num_page = 1

    if num_page > result_list.num_pages:
        num_page = result_list.num_pages
    
    if result_list.num_pages >= num_page:
        page = result_list.page(num_page)
    
        context = {
            'queryset': page.object_list,
            'num_page': num_page,
            'pages': result_list.num_pages,
            'has_next': page.has_next(),
            'has_prev': page.has_previous(),
            'next_page': num_page + 1,
            'prev_page': num_page - 1,
            'first_page': 1,
        }
    return context

@csrf_exempt
def RFID(request):
    if request.method == 'POST':
        try:
            rfid = str(request.body).split('"')[3].lstrip()
            if rfid is None:
                return HttpResponse('No se recibió RFID\n')
            else:
                try:
                    diner = Diner.objects.get(RFID=rfid)
                    new_access_log = AccessLog(diner=diner, RFID=rfid)
                    new_access_log.save()    
                except Diner.DoesNotExist:
                    new_access_log = AccessLog(diner=None, RFID=rfid)
                    new_access_log.save()
        except:
            print('Error Interno')
        
        
        return HttpResponse('Operacion Terminada\n')

    else:
        return redirect('diners:diners')


def diners(request):
    diners_access_log = AccessLog.objects.all().order_by('-access_to_room')
    pag = diners_paginator(request, diners_access_log, 50)
    template = 'diners.html'
    title = 'Comensales del Dia'
    page_title = PAGE_TITLE

    context={
        'title': PAGE_TITLE + ' | ' + title,
        'page_title': title,
        'diners' : pag['queryset'],
        'paginator': pag,
    }
    return render(request, template, context)    
