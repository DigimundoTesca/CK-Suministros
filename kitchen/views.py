from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from cloudkitchen.settings.base import PAGE_TITLE
from helpers import SalesHelper, ProductsHelper, KitchenHelper


@login_required(login_url='users:login')
def kitchen(request):
    template = 'kitchen.html'
    title = 'Cocina'
    sales_helper = SalesHelper()
    kitchen_helper = KitchenHelper()

    context = {
        'title': PAGE_TITLE + ' | ' + title,
        'page_title': title,
        'extra_ingredients': sales_helper.get_all_extra_ingredients(),
        'products': kitchen_helper.get_processed_products(),
        'tickets': sales_helper.get_tickets(),
        'tickets_details': sales_helper.get_all_tickets_details(),
    }

    return render(request, template, context)


@login_required(login_url='users:login')
def assembly(request):
    kitchen_helper = KitchenHelper()
    sales_helper = SalesHelper()
    products_helper = ProductsHelper()

    all_processed_products = kitchen_helper.get_all_processed_products()
    all_tickets_details = sales_helper.get_all_tickets_details()
    all_cartridges = products_helper.get_all_cartridges()
    all_packages_cartridges = products_helper.get_all_packages_cartridges()

    if request.method == 'POST':
        if request.POST['order_id']:
            order = all_processed_products.get(ticket=request.POST['order_id'])
            order.status = 'AS'
            order.save()
        return redirect('kitchen:assembly')

    else:
        template = 'assembly.html'
        title = 'Ensamblado'
        pending_orders = all_processed_products.filter(status='PE')[:10]
        orders_list = []

        for order in pending_orders:
            order_object = {
                'ticket_id': order.ticket,
                'ticket_order': order.ticket.order_number,
                'products': [],
                'packages': [],
            }

            ticket_details = all_tickets_details.filter(ticket=order.ticket)

            for ticket_detail in ticket_details:
                for cartridge in all_cartridges:
                    if ticket_detail.cartridge == cartridge:
                        product_object = {
                            'name': ticket_detail.cartridge.name,
                            'quantity': ticket_detail.quantity,
                        }
                        order_object['products'].append(product_object)

                for package in all_packages_cartridges:
                    if ticket_detail.package_cartridge == package:
                        package_object = {
                            'name': ticket_detail.package_cartridge.name,
                            'quantity': ticket_detail.quantity,
                        }
                        order_object['packages'].append(package_object)

            orders_list.append(order_object)

        context = {
            'title': PAGE_TITLE + ' | ' + title,
            'page_title': title,
            'orders': orders_list
        }

        return render(request, template, context)
