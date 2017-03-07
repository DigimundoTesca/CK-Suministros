import json, pytz
from datetime import datetime, date, timedelta, time
import time as python_time

from decimal import Decimal

from django.contrib.auth.decorators import login_required,permission_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_protect, requires_csrf_token
from django.middleware.csrf import get_token
from django.utils import timezone

from branchoffices.models import CashRegister
from cashflow.settings.base import PAGE_TITLE
from products.models import Cartridge, PackageCartridge, PackageCartridgeRecipe
from sales.models import Ticket, TicketDetail
from users.models import User as UserProfile

"""
Start auxiliary functions
"""
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


def get_week_number():
    return date.today().isocalendar()[1]


def start_datetime(back_days):
    start_date = date.today() - timedelta(days=back_days) 
    return naive_to_datetime(start_date)


def end_datetime(back_days):
    end_date = start_datetime(back_days) + timedelta(days=1)
    return naive_to_datetime(end_date)


def items_list_to_int(list_to_cast):
    """
    Evaluates each of the elements of the list received and casts them to integers
    """
    cast_list = []
    for item in range(0, len(list_to_cast)):
        cast_list.append(int(list_to_cast[item]))

    return cast_list


def are_equal_lists(list_1, list_2):
    """
     Checks if two lists are identical
    """
    list_1 = items_list_to_int(list_1)
    list_2 = items_list_to_int(list_2)

    list_1.sort()
    list_2.sort()

    if len(list_1) != len(list_2):
        return False
    else:
        for element in range(0, len(list_1)):
            if list_1[element] != list_2[element]:
                return False

    return True



"""
Start of views
"""
# -------------------------------------  Sales -------------------------------------
@login_required(login_url='users:login')
def sales(request):
    all_tickets = Ticket.objects.all()
    all_ticket_details = TicketDetail.objects.all()

    def get_sales_week():
        """
        1. Gets the following properties for the day: Name, Date and Earnings
        """
        week_sales_list = []
        total_earnings = 0
        days_to_count = get_number_day()
        day_limit = days_to_count
        start_date_number = 0
        
        while start_date_number <= day_limit:
            day_object = {
                'date': str(start_datetime(days_to_count).date()),
                'day_name': None,
                'earnings': None,
            }

            tickets = all_tickets.filter(created_at__range=[start_datetime(days_to_count), end_datetime(days_to_count)])

            for ticket in tickets:
                for ticket_detail in all_ticket_details:
                    if ticket_detail.ticket == ticket:
                        total_earnings += ticket_detail.price

            day_object['earnings'] = str(total_earnings)
            day_object['day_name'] = get_name_day(start_datetime(days_to_count).date())

            week_sales_list.append(day_object)

            # restarting counters
            days_to_count -= 1
            total_earnings = 0
            start_date_number += 1

        return json.dumps(week_sales_list)

    def get_tickets():
        tickets_details = TicketDetail.objects.select_related(
            'ticket', 'ticket__seller', 'cartridge', 'package_cartridge').filter()
        tickets = Ticket.objects.filter(created_at__gte=naive_to_datetime(date.today()))
        tickets_list = []

        for ticket in tickets:
            ticket_object = {
                'ticket_parent': ticket,
                'cartridges': [],
                'packages': [],
                'total': Decimal(0.00),
            }

            for ticket_details in tickets_details:
                if ticket_details.ticket == ticket:
                    if ticket_details.cartridge:
                        cartridge_object = {
                            'cartridge': ticket_details.cartridge,
                            'quantity': ticket_details.quantity
                        }
                        ticket_object['cartridges'].append(cartridge_object)
                        ticket_object['total'] += ticket_details.price
                    elif ticket_details.package_cartridge:
                        package_cartridge_object = {
                            'package': ticket_details.package_cartridge,
                            'quantity': ticket_details.quantity
                        }
                        ticket_object['packages'].append(package_cartridge_object)
                        ticket_object['total'] += ticket_details.price

            tickets_list.append(ticket_object)

        return tickets_list

    if request.method == 'POST':
        if request.POST['type'] == 'sales_day':
            """
            Returns a list with objects:
            Each object has the following characteristics
            """
            sales_day_list = []
            start_day = naive_to_datetime(datetime.strptime(request.POST['date'], '%Y-%m-%d').date())
            end_date = naive_to_datetime(start_day + timedelta(days=1))
            tickets_objects = all_tickets.filter(created_at__range=[start_day, end_date])

            for ticket in tickets_objects:
                """
                Filling in the sales list of the day
                """
                earnings_sale_object = {
                    'id_ticket': ticket.id,
                    'datetime': timezone.localtime(ticket.created_at),
                    'earnings': 0
                }
                for ticket_detail in all_ticket_details:
                    if ticket_detail.ticket == ticket:
                        earnings_sale_object['earnings'] += ticket_detail.price
                sales_day_list.append(earnings_sale_object)

            return JsonResponse({'sales_day_list': sales_day_list})

        if request.POST['type'] == 'ticket_details':
            ticket_id = int(request.POST['ticket_id'])
            ticket_object = {
                'ticket_id': ticket_id,
                'cartridges': [],
                'packages': [],
            }

            # Get cartridges details
            for ticket_detail in all_ticket_details:
                if ticket_detail.ticket.id == ticket_id:
                    if ticket_detail.cartridge:
                        cartridge_object = {
                            'name': ticket_detail.cartridge.name,
                            'quantity': ticket_detail.quantity,
                            'total': ticket_detail.price
                        }
                        ticket_object['cartridges'].append(cartridge_object)
                    elif ticket_detail.package_cartridge:
                        cartridges_list = []
                        package_cartridge_recipe = PackageCartridgeRecipe.objects.filter(
                            package_cartridge=ticket_detail.package_cartridge)

                        for cartridge_recipe in package_cartridge_recipe:
                            cartridges_list.append(cartridge_recipe.cartridge.name)
                            
                        package_cartridge_object = {
                            'cartridges': cartridges_list,
                            'quantity': ticket_detail.quantity,
                            'total': ticket_detail.price
                        }
                        ticket_object['packages'].append(package_cartridge_object)
            return JsonResponse({'ticket_details': ticket_object})
            
        if request.POST['type'] == 'tickets':
            tickets_objects_list = []

            for ticket in all_tickets:
                for ticket_detail in all_ticket_details:
                    if ticket_detail.ticket == ticket:
                        ticket_object = {
                            'ticket_id': ticket.id,
                            'created_at': ticket.created_at,
                            'seller': ticket.seller.username,
                            'payment_type': ticket.payment_type,
                        }
                        if ticket_detail.cartridge:
                            ticket_object['cartridge'] =  ticket_detail.cartridge.name
                        else:
                            ticket_object['cartridge'] =  None
                        if ticket_detail.package_cartridge:
                            ticket_object['package_cartridge'] = ticket_detail.package_cartridge.name
                        else:
                            ticket_object['package_cartridge'] = None
                        ticket_object['quantity'] = ticket_detail.quantity
                        ticket_object['price'] = ticket_detail.price

                        tickets_objects_list.append(ticket_object)

            return JsonResponse({'ticket': tickets_objects_list})

    # Any other request method:
    template = 'sales/sales.html'
    title = 'Ventas'
    context = {
        'page_title': PAGE_TITLE,
        'title': title,
        'sales_week': get_sales_week(),
        'today_name': get_name_day(datetime.now()),
        'today_number': get_number_day(),
        'week_number': get_week_number(),
        'tickets': get_tickets(),
    }
    return render(request, template, context)


@login_required(login_url='users:login')
def delete_sale(request):
    if request.method == 'POST':
        ticket_id = request.POST['ticket_id']
        ticket = Ticket.objects.get(id=ticket_id)
        ticket.delete()
        return JsonResponse({'result': 'excelente!'})


@login_required(login_url='users:login')
def new_sale(request):
    if request.method == 'POST':
        if request.POST['ticket']:
            username = request.user
            user_profile_object = get_object_or_404(UserProfile, username=username)
            cash_register = CashRegister.objects.first()
            ticket_detail_json_object = json.loads(request.POST.get('ticket'))
            payment_type = ticket_detail_json_object['payment_type']
            new_ticket_object = Ticket(
                cash_register=cash_register, seller=user_profile_object, payment_type=payment_type)

            """ 
            Gets the tickets in the week and returns n + 1 
            where n is the Ticket.order_number biggest for the current week
            TODO:
            1. Get tickets in the current week range
            2. Search the ticket with the largest order_number atribute
            3. save the 'new_ticket_object' with the new atribute (n + 1)
            4. Save the new object
            """
            new_ticket_object = Ticket(
                cash_register=cash_register, seller=user_profile_object, payment_type=payment_type)
            new_ticket_object.save()

            """
            Saves the tickets details for cartridges
            """
            for ticket_detail in ticket_detail_json_object['cartuchos']:
                cartridge_object = get_object_or_404(Cartridge, id=ticket_detail['id'])
                quantity = ticket_detail['cant']
                price = ticket_detail['price']
                new_ticket_detail_object = TicketDetail(
                    ticket=new_ticket_object,
                    cartridge=cartridge_object,
                    quantity=quantity,
                    price=price
                )
                new_ticket_detail_object.save()

            for ticket_detail_packages in ticket_detail_json_object['paquetes']:               
                """
                Saves the tickets details for package cartridges
                    1. Iterates each package
                    2. For each package, gets the list of cartridges tha make up each recipe
                    3. Compares the cartridge's list obtained with the corresponding list in the JSON
                    4. Depending on the result on th result creates a new item in the package table and the new
                        ticket or just creates the new ticket
                """
                quantity = ticket_detail_packages['quantity']
                price = ticket_detail_packages['price']
                packages_id_list = ticket_detail_packages['id_list']
                package_id = None
                is_new_package = True
                packages_recipes = PackageCartridge.objects.all()

                for package_recipe in packages_recipes:
                    """
                    Gets the cartridges for each package cartridge and compares
                    each package recipe cartridges if is equal that packages_id_list
                    """
                    cartridges_per_recipe = PackageCartridgeRecipe.objects.select_related(
                        'package_cartridge', 'cartridge').filter(package_cartridge=package_recipe)
                    cartridges_in_package_recipe = []

                    for cartridge_recipe in cartridges_per_recipe:
                        cartridges_in_package_recipe.append(cartridge_recipe.cartridge.id)

                    if are_equal_lists(cartridges_in_package_recipe, packages_id_list):
                        is_new_package = False
                        package_id = package_recipe.id

                if is_new_package:
                    package_name = ticket_detail_packages['name']
                    package_price = ticket_detail_packages['price']
                    new_package_object = PackageCartridge(name=package_name, price=package_price, package_active=True)
                    new_package_object.save()

                    """
                    Creates a new package
                    """
                    for id_cartridge in packages_id_list:
                        cartridge_object = get_object_or_404(Cartridge, id=id_cartridge)
                        new_package_recipe_object = PackageCartridgeRecipe(
                            package_cartridge=new_package_object,
                            cartridge=cartridge_object,
                            quantity=1
                        )
                        new_package_recipe_object.save()

                    """
                    Creates the ticket detail
                    """
                    new_ticket_detail_object = TicketDetail(
                        ticket=new_ticket_object,
                        package_cartridge=new_package_object,
                        quantity=quantity,
                        price=price
                    )
                    new_ticket_detail_object.save()

                else:
                    """
                    Uses an existent package
                    """
                    package_object = get_object_or_404(PackageCartridge, id=package_id)
                    new_ticket_detail_object = TicketDetail(
                        ticket=new_ticket_object,
                        package_cartridge=package_object,
                        quantity=quantity,
                        price=price,
                    )
                    new_ticket_detail_object.save()
            print(new_ticket_object.order_number)
            json_response = {
                'status': 'ready',
                'ticket_id': new_ticket_object.id,
                'ticket_order': new_ticket_object.order_number,
            }
            return JsonResponse(json_response)

        return JsonResponse({'status': 'error'})

    else:
        cartridges_list = Cartridge.objects.all()
        package_cartridges = PackageCartridge.objects.all()
        template = 'sales/new_sale.html'
        title = 'Nueva venta'
        context = {
            'page_title': PAGE_TITLE,
            'title': title,
            'cartridges': cartridges_list,
            'package_cartridges': package_cartridges
        }
        return render(request, template, context)


# -------------------------------- Test ------------------------------
def test(request):
    template = 'sales/test.html'

    tickets_details = TicketDetail.objects.select_related('ticket', 'ticket__seller', 'cartridge','package_cartridge').filter()
    tickets = Ticket.objects.all()
    tickets_list = []

    for ticket in tickets:
        ticket_object = {
            'ticket_parent': ticket,
            'cartridges': [],
            'packages': [],
            'total': Decimal(0.00),
        }

        for ticket_details in tickets_details:
            if ticket_details.ticket == ticket:
                if ticket_details.cartridge:
                    cartridge_object = {
                        'cartridge': ticket_details.cartridge,
                        'quantity': ticket_details.quantity
                    }
                    ticket_object['cartridges'].append(cartridge_object)
                    ticket_object['total'] += ticket_details.price
                elif ticket_details.package_cartridge:
                    package_cartridge_object = {
                        'package': ticket_details.package_cartridge,
                        'quantity': ticket_details.quantity
                    }
                    ticket_object['packages'].append(package_cartridge_object)
                    ticket_object['total'] += ticket_details.price

        tickets_list.append(ticket_object)

    context = {
        'tickets': tickets_list,
    }

    return render(request, template, context)
