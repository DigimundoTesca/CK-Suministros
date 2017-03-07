from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

# -------------------------------------  Kitchen -------------------------------------
from cashflow.settings.base import PAGE_TITLE
from kitchen.models import ProcessedProduct
from products.models import PackageCartridgeRecipe, Cartridge, PackageCartridge
from sales.models import Ticket, TicketDetail


@login_required(login_url='users:login')
def cold_kitchen(request):
    template = 'kitchen/cold.html'
    tickets = Ticket.objects.all()

    def get_processed_products():
        processed_products_list = []
        processed_objects = ProcessedProduct.objects.filter(status='PE')

        for processed in processed_objects:
            processed_product_object = {
                'ticket_id': processed.ticket,
                'cartridges': [],
                'packages': []
            }

            for ticket_detail in TicketDetail.objects.filter(ticket=processed.ticket):
                if ticket_detail.ticket == processed.ticket:
                    if ticket_detail.cartridge:
                        cartridge = {
                            'quantity': ticket_detail.quantity,
                            'cartridge': ticket_detail.cartridge
                        }
                        processed_product_object['cartridges'].append(cartridge)

                    elif ticket_detail.package_cartridge:
                        package = {
                            'quantity': ticket_detail.quantity,
                            'package_recipe': []
                        }
                        package_recipe = \
                            PackageCartridgeRecipe.objects.filter(package_cartridge=ticket_detail.package_cartridge)
                        for recipe in package_recipe:
                            package['package_recipe'].append(recipe.cartridge)
                        processed_product_object['packages'].append(package)

            processed_products_list.append(processed_product_object)
        return processed_products_list

    context = {
        'products': get_processed_products(),
        'tickets': tickets,
        'page_title': 'Cocina Fría' ,
        'title': PAGE_TITLE,
    }

    return render(request, template, context)


def hot_kitchen(request):
    template = 'kitchen/hot.html'
    tickets = Ticket.objects.all()

    def get_processed_products():
        processed_products_list = []
        processed_objects = ProcessedProduct.objects.filter(status='PE')

        for processed in processed_objects:
            processed_product_object = {
                'ticket_id': processed.ticket,
                'cartridges': [],
                'packages': []
            }

            for ticket_detail in TicketDetail.objects.filter(ticket=processed.ticket):
                if ticket_detail.ticket == processed.ticket:
                    if ticket_detail.cartridge:
                        cartridge = {
                            'quantity': ticket_detail.quantity,
                            'cartridge': ticket_detail.cartridge
                        }
                        processed_product_object['cartridges'].append(cartridge)

                    elif ticket_detail.package_cartridge:
                        package = {
                            'quantity': ticket_detail.quantity,
                            'package_recipe': []
                        }
                        package_recipe = \
                            PackageCartridgeRecipe.objects.filter(package_cartridge=ticket_detail.package_cartridge)
                        for recipe in package_recipe:
                            package['package_recipe'].append(recipe.cartridge)
                        processed_product_object['packages'].append(package)

            processed_products_list.append(processed_product_object)
        return processed_products_list

    context = {
        'products': get_processed_products(),
        'tickets': tickets,
        'page_title': 'Cocina Caliente',
        'title': PAGE_TITLE,
    }

    return render(request, template, context)


def assembly(request):
    if request.method == 'POST':
        if request.POST['order_id']:
            order = ProcessedProduct.objects.get(ticket=request.POST['order_id'])
            order.status = 'AS'
            order.save()
        return redirect('kitchen:assembly')

    else:
        template = 'kitchen/assembly.html'

        pending_orders = ProcessedProduct.objects.filter(status='PE')
        orders_list = []

        for order in pending_orders:
            order_object = {
                'ticket_id': order.ticket,
                'products': [],
                'packages': [],
            }

            ticket_details = TicketDetail.objects.filter(ticket=order.ticket)
            cartridges = Cartridge.objects.all()
            packages = PackageCartridge.objects.all()

            for ticket_detail in ticket_details:
                for cartridge in cartridges:
                    if ticket_detail.cartridge == cartridge:
                        product_object = {
                            'name': ticket_detail.cartridge.name,
                            'quantity': ticket_detail.quantity,
                        }
                        order_object['products'].append(product_object)

                for package in packages:
                    if ticket_detail.package_cartridge == package:
                        package_object = {
                            'name': ticket_detail.package_cartridge.name,
                            'quantity': ticket_detail.quantity,
                        }
                        order_object['packages'].append(package_object)

            orders_list.append(order_object)

        context = {
            'orders': orders_list,
            'page_title': 'Ensamblado',
            'title': PAGE_TITLE
        }

        return render(request, template, context)
