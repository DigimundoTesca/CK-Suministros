import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect

from django.contrib.auth import authenticate
from django.contrib.auth import login as login_django
from django.contrib.auth import logout as logout_django

from users.forms import CustomerProfileForm, UserForm

from cashflow.settings.base import PAGE_TITLE


# -------------------------------------  Index -------------------------------------
from users.models import CustomerProfile


def arduino(request):
    print(request)
    return HttpResponse('HOLA')

def test(request):
    form_customer = CustomerProfileForm(request.POST, request.FILES)
    if request.method == 'POST':
        if form_customer.is_valid():
            print('IS VALID!!!')
            customer = form_customer.save(commit=False)
            customer.save()
            return redirect('users:thanks')
    else:
        form_customer = CustomerProfileForm()
    template = 'test/test.html'
    title = 'Dabbawala - Registro de clientes'
    form_user = UserForm()
    context = {
        'form_customer': form_customer,
        'title': title,
    }

    return render(request, template, context)


# -------------------------------------  Index -------------------------------------
def index(request):
    return redirect('users:login')


# -------------------------------------  Auth -------------------------------------
def login(request):
    if request.user.is_authenticated():
        return redirect('sales:sales')
    tab = 'login'
    error_message = None
    success_message = None
    template = 'auth/login.html'

    form_user = UserForm(request.POST or None)

    if request.method == 'POST':
        if 'form-register' in request.POST:
            tab = 'register'
            if form_user.is_valid():
                new_user = form_user.save(commit=False)
                new_user.set_password(form_user.cleaned_data['password'])
                new_user.save()
                tab = 'register'
                success_message = 'Usuario creado. Necesita ser activado por un administrador'
                form_user = None

        elif 'form-login' in request.POST:
            form_user = UserForm(None)
            username_login = request.POST.get('username_login')
            password_login = request.POST.get('password_login')
            user = authenticate(username=username_login, password=password_login)

            if user is not None:
                login_django(request, user)
                return redirect('sales:sales')

            else:
                error_message = 'Usuario o contraseña incorrecto'

    context = {
        'tab': tab,
        'title': 'Bienvenido a Dabbanet. Inicia Sesión o registrate.',
        'error_message': error_message,
        'success_message': success_message,
        'form_user': form_user,
    }
    return render(request, template, context)


@login_required(login_url='users:login')
def logout(request):
    logout_django(request)
    return redirect('users:login')


# -------------------------------------  Customers -------------------------------------
def new_customer(request):
    form_customer = CustomerProfileForm(request.POST or None)
    if request.method == 'POST':
        if form_customer.is_valid():
            customer = form_customer.save(commit=False)
            customer.save()
            return redirect('users:thanks')

    template = 'customers/register/new_customer.html'
    title = 'Dabbawala - Bienvenido a Dabbawala. Registrare y obtén un desayuno gratis. '
    context = {
        'form_customer': form_customer,
        'title': title,
    }

    return render(request, template, context)


def thanks(request):
    if request.method == 'POST':
        form = CustomerProfileForm(request.POST, request.FILES)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.save()
            return redirect('users:new_customer')
    else:
        form = CustomerProfileForm()

    template = 'customers/register/thanks.html'
    title = 'Dabbawala - Registro de clientes'

    context = {
        'form': form,
        'title': title,
    }

    return render(request, template, context)


@login_required(login_url='users:login')
def customers_list(request):
    if request.method == 'POST':
        customer_json_object = json.loads(request.POST.get('customer'))

        customer_object = CustomerProfile.objects.get(id=customer_json_object['id'])
        customer_object.first_dabba = True
        customer_object.save()
        data = {
            'status': 'ready'
        }
        return JsonResponse(data)

    template = 'customers/register/customers_list.html'
    customers = CustomerProfile.objects.all().order_by('first_dabba')
    title = 'Clientes registrados'

    context = {
        'title': title,
        'page_title': PAGE_TITLE,
        'customers': customers,
    }

    return render(request, template, context)