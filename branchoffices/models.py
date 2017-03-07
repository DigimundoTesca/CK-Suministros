from django.core.validators import MinLengthValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from users.models import User as UserProfile


class BranchOffice(models.Model):
    name = models.CharField(max_length=90, default='')
    address = models.CharField(max_length=255, default='')
    manager = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    is_activate = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('id',)
        verbose_name = 'Sucursal'
        verbose_name_plural = 'Sucursales'


class CashRegister(models.Model):
    code = models.CharField(
        help_text='Asigne un nuevo nombre a la caja registradora',
        max_length=9,
        default='Cash_'
    )
    branch_office = models.ForeignKey(BranchOffice, default=1, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=False)

    @receiver(post_save, sender=BranchOffice)
    def create_first_cash_register(sender, instance, **kwargs):
        """
            Validates if there is at least one cash register in the branch office
        """
        office = BranchOffice.objects.get(id=instance.id)
        has_cash_registers = CashRegister.objects.filter(branch_office=office).exists()
        print(has_cash_registers)

        if has_cash_registers is False:
            new_cash_register = CashRegister.objects.create(code='Cash_01', branch_office=office, is_active=True)
            new_cash_register.save()

    def __str__(self):
        return '%s' % self.id

    class Meta:
        ordering = ('id',)
        verbose_name = 'Punto de Venta'
        verbose_name_plural = 'Puntos de Venta'


class Supplier(models.Model):
    name = models.CharField(validators=[MinLengthValidator(4)], max_length=255, unique=True)
    image = models.ImageField(blank=False, upload_to='media/suppliers')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('id',)
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'