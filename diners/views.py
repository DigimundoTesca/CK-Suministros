
# -*- encoding: utf-8 -*-
from __future__ import unicode_literals

import  pytz
from datetime import date, datetime, timedelta, time

from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from diners.models import AccessLog
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator

from .models import AccessLog, Diner
from cloudkitchen.settings.base import PAGE_TITLE

def naive_to_datetime(nd):
    if type(nd) == datetime:
        if nd.tzinfo is not None and nd.tzinfo.utcoffset(nd) is not None: # Is Aware
            return nd
        else: # Is Naive
            return pytz.timezone('America/Mexico_City').localize(nd)              

    elif type(nd) == date:
        d = nd
        t = time(0,0)
        new_date = datetime.combine(d, t)
        return pytz.timezone('America/Mexico_City').localize(new_date)

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

def get_access_logs():
    year = int(datetime.now().year)
    month = int(datetime.now().month)
    day = int(datetime.now().day)
    initial_date = naive_to_datetime(date(year, month, day))
    final_date = naive_to_datetime(initial_date + timedelta(days=1))
    #diners_access_log = AccessLog.objects.filter(access_to_room__range=(initial_date, final_date)).order_by('-access_to_room')
    diners_access_log = AccessLog.objects.all().order_by('-access_to_room')
    return diners_access_log

@csrf_exempt
def RFID(request):
    if request.method == 'POST':
        rfid = str(request.body).split('"')[3].lstrip()
        if rfid is None:
            return HttpResponse('No se recibió RFID\n')
        else:
            access_logs = get_access_logs()
            exists = False
            
            for log in access_logs:
                if rfid == log.RFID:
                    exists = True
                    break

            if exists:
                return HttpResponse('El usuario ya se ha registrado')
            else:
                try:
                    diner = Diner.objects.get(RFID=rfid)
                    new_access_log = AccessLog(diner=diner, RFID=rfid)
                    new_access_log.save()
                except Diner.DoesNotExist:
                    new_access_log = AccessLog(diner=None, RFID=rfid)
                    new_access_log.save()    

        return HttpResponse('Operacion Terminada\n')

    else:
        return redirect('diners:diners')


def diners(request):
    diners_objects = get_access_logs()
    count = 0
    diners_list = []
    for diner in diners_objects:
        if diner not in diners_list:
            diners_list.append(diner)
            count += 1
    total_diners = len(diners_list)

    pag = diners_paginator(request, diners_objects, 10000)
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
