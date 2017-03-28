
# -*- encoding: utf-8 -*-
from __future__ import unicode_literals

import json,pytz
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

def get_name_day(datetime_now):
    days_list = {
        'MONDAY': 'Lunes',
        'TUESDAY': 'Martes',
        'WEDNESDAY': 'Miércoles',
        'THURSDAY': 'Jueves',
        'FRIDAY': 'Viernes',
        'SATURDAY': 'Sábado',
        'SUNDAY': 'Domingo'
    }
    name_day = date(datetime_now.year, datetime_now.month, datetime_now.day)
    return days_list[name_day.strftime('%A').upper()]


def get_number_day():
    days = {
        'Lunes': 0, 'Martes': 1, 'Miércoles': 2, 'Jueves': 3, 'Viernes': 4, 'Sábado': 5, 'Domingo': 6,
    }
    return days[get_name_day(datetime.now())]

def start_datetime(back_days):
    start_date = date.today() - timedelta(days=back_days) 
    return naive_to_datetime(start_date)


def end_datetime(back_days):
    end_date = start_datetime(back_days) + timedelta(days=1)
    return naive_to_datetime(end_date)


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
    diners_access_log = AccessLog.objects.filter(access_to_room__range=(initial_date, final_date)).order_by('-access_to_room')
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

def get_diners_per_hour():
    hours_list = []
    hours_to_count = 12
    start_hour = 5
    customter_count = 0    
    logs = get_access_logs()

    while start_hour <= hours_to_count:

        hour = {            
            'count': None,
        }

        for log in logs:
            datetime = str(log.access_to_room)
            date,time = datetime.split(" ")        
            print("0"+str(start_hour))
            if(time.startswith("0"+str(start_hour))):
                customter_count += 1 
            hour['count'] = customter_count

        hours_list.append(hour)        
        customter_count = 0
        start_hour += 1
        total_entries = 0

    return json.dumps(hours_list) 

            

def get_diners_actual_week():
       
        week_diners_list = []
        total_entries = 0
        days_to_count = get_number_day()
        day_limit = days_to_count
        start_date_number = 0
        
        while start_date_number <= day_limit:
            day_object = {
                'date': str(start_datetime(days_to_count).date()),
                'day_name': None,
                'entries': None,
            }
            
            logs = AccessLog.objects.filter(access_to_room__range=[start_datetime(days_to_count), end_datetime(days_to_count)])

            for log in logs:                
                total_entries += 1;

            day_object['entries'] = str(total_entries)
            day_object['day_name'] = get_name_day(start_datetime(days_to_count).date())

            week_diners_list.append(day_object)

            # restarting counters
            days_to_count -= 1
            total_entries = 0
            start_date_number += 1

        return json.dumps(week_diners_list)         


def diners(request):
    diners_objects = get_access_logs()   
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
        'diners_hour' : get_diners_per_hour(),
        'diners_week' : get_diners_actual_week(),        
        'paginator': pag,
        'total_diners': total_diners,
    }
    return render(request, template, context)    
