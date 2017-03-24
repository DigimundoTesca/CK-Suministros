
# -*- encoding: utf-8 -*-
from __future__ import unicode_literals

from datetime import date, datetime, timedelta

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

def get_access_log():
    year = int(datetime.now().year)
    month = int(datetime.now().month)
    day = int(datetime.now().day)
    initial_date = date(year, month, day)
    print(initial_date)
    final_date = initial_date + timedelta(days=1)
    diners_access_log = AccessLog.objects.filter(access_to_room__range=(initial_date, final_date)).order_by('-access_to_room')
    return diners_access_log

@csrf_exempt
def RFID(request):
    if request.method == 'POST':
        try:
            rfid = str(request.body).split('"')[3].lstrip()
            if rfid is None:
                return HttpResponse('No se recibió RFID\n')
            else:
                try:
                    access_logs = get_access_log()
                    diner = Diner.objects.get(RFID=rfid)
                    exists = False
                    
                    for log in access_logs:
                        if diner.RFID == log.RFID:
                            return HttpResponse('El usuario ya se ha registrado')
                        else:
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
    diners_objects = get_access_log()
    count = 0
    diners_list = []
    for diner in diners_objects:
        if diner not in diners_list:
            diners_list.append(diner)
            count += 1
    total_diners = len(diners_list)

    pag = diners_paginator(request, diners_objects, 50)
    template = 'diners.html'
    title = 'Comensales del Dia'
    page_title = PAGE_TITLE

    context={
        'title': PAGE_TITLE + ' | ' + title,
        'page_title': title,
        'diners' : pag['queryset'],
        'paginator': pag,
        'total_diners': total_diners,
    }
    return render(request, template, context)    
