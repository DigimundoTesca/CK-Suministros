from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from branchoffices.models import Supplier
from products.models import Supply, Cartridge, PackageCartridge
from users.models import User as UserProfile


class SupplierOrder(models.Model):
    CANCELED = 'CA'
    IN_PROCESS = 'IP'
    RECEIVED = 'RE'
    STATUS = (
        (IN_PROCESS, 'Pedido'),
        (RECEIVED, 'Recibido'),
        (CANCELED, 'Cancelado'),
    )

    created_at = models.DateTimeField(editable=False, auto_now_add=True)
    status = models.CharField(choices=STATUS, default=IN_PROCESS, max_length=2)
    assigned_dealer = models.ForeignKey(UserProfile, default=1, on_delete=models.CASCADE)

    def __str__(self):
        return '%s' % self.id

    class Meta:
        ordering = ('id',)
        verbose_name = 'Pedido al Proveedor'
        verbose_name_plural = 'Pedidos a Proveedores'


class SupplierOrderDetail(models.Model):
    order = models.ForeignKey(SupplierOrder, default=1, on_delete=models.CASCADE)
    supply = models.ForeignKey(Supply, default=1, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    cost = models.DecimalField(default=0, max_digits=12, decimal_places=2)
    supplier = models.ForeignKey(Supplier, default=1, on_delete=models.CASCADE)

    def __str__(self):
        return '%s %s %s' % (self.id, self.supply, self.quantity)

    class Meta:
        ordering = ('id',)
        verbose_name = 'Detalles del Pedido a Proveedor'
        verbose_name_plural = 'Detalles de Pedidos a Proveedores'


# ----------------------------------- Customers models ----------------------------------
class CustomerOrder(models.Model):
    IN_PROCESS = 'PR'
    SOLD = 'SO'
    CANCELLED = 'CA'

    STATUS = (
        (IN_PROCESS, 'En proceso',),
        (SOLD, 'Vendido'),
        (CANCELLED, 'Cancelado'),
    )
    customer_user = models.ForeignKey(UserProfile, default=1)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    delivery_date = models.DateTimeField(auto_created=True, editable=True)
    status = models.CharField(max_length=10, choices=STATUS, default=IN_PROCESS)
    latitude = models.FloatField(default=0)
    longitude = models.FloatField(default=0)
    price = models.DecimalField(default=0, max_digits=12, decimal_places=2)
    score = models.PositiveIntegerField(
        validators=[MaxValueValidator(5), MinValueValidator(1)],
        null=False, blank=False, default=1)
    pin = models.CharField(default='1234', max_length=254, blank=False)

    def __str__(self):
        return '%s' % self.id

    class Meta:
        ordering = ('id',)
        verbose_name = 'Pedido del Cliente'
        verbose_name_plural = 'Pedidos de los Clientes'


class CustomerOrderDetail(models.Model):
    IN_PROCESS = 'PR'
    SOLD = 'SE'
    CANCELLED = 'CA'

    STATUS = (
        (IN_PROCESS, 'En proceso',),
        (SOLD, 'Vendido'),
        (CANCELLED, 'Cancelado'),
    )
    customer_order = models.ForeignKey(CustomerOrder, default=1, on_delete=models.CASCADE)
    cartridge = models.ForeignKey(Cartridge, on_delete=models.CASCADE, blank=True, null=True)
    package_cartridge = models.ForeignKey(PackageCartridge, on_delete=models.CASCADE, blank=True, null=True)
    quantity = models.IntegerField()

    def __str__(self):
        return '%s' % self.id

    class Meta:
        ordering = ('id',)
        verbose_name = 'Detalles del Pedido del Cliente'
        verbose_name_plural = 'Detalles de los Pedidos de Clientes'