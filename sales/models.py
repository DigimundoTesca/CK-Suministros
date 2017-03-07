from django.db import models
from django.db.models import Avg, Sum
from django.utils import timezone

from branchoffices.models import CashRegister
from products.models import Cartridge, PackageCartridge
from users.models import User as UserProfile


class Ticket(models.Model):
    # Payment Type
    CASH = 'CA'
    CREDIT = 'CR'

    PAYMENT_TYPE = (
        (CASH, 'Efectivo'),
        (CREDIT, 'Crédito'),
    )

    created_at = models.DateTimeField(editable=True)
    seller = models.ForeignKey(
        UserProfile, default=1, on_delete=models.CASCADE)
    cash_register = models.ForeignKey(
        CashRegister, on_delete=models.CASCADE, default=1)
    payment_type = models.CharField(
        choices=PAYMENT_TYPE, default=CASH, max_length=2)
    order_number = models.IntegerField(
        null=True)

    def __str__(self):
        return '%s' % self.id

    def save(self, *args, **kwargs):
        """ On save, update timestamps"""
        if not self.id:
            self.created_at = timezone.now()
        return super(Ticket, self).save(*args, **kwargs)

    def total(self):
        tickets_details = TicketDetail.objects.filter(ticket=self.id)
        total = 0
        for x in tickets_details:
            total += x.price
        return total

    def ticket_details(self):
        tickets_details = TicketDetail.objects.filter(ticket=self.id)
        options = []

        for ticket_detail in tickets_details:
            if ticket_detail.cartridge:
                options.append(("<option value=%s>%s</option>" %
                                (ticket_detail, ticket_detail.cartridge)))
            elif ticket_detail.package_cartridge:
                options.append(("<option value=%s>%s</option>" %
                                (ticket_detail, ticket_detail.package_cartridge)))
        tag = """<select>%s</select>""" % str(options)
        return tag

    ticket_details.allow_tags = True

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'Ticket '
        verbose_name_plural = 'Tickets'


class TicketDetail(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    cartridge = models.ForeignKey(
        Cartridge, on_delete=models.CASCADE, blank=True, null=True)
    package_cartridge = models.ForeignKey(
        PackageCartridge, on_delete=models.CASCADE, blank=True, null=True)
    quantity = models.IntegerField(default=0)
    price = models.DecimalField(default=0, max_digits=12, decimal_places=2)


    def created_at(self):
        return self.ticket.created_at

    def __str__(self):
        return '%s' % self.id

    class Meta:
        ordering = ('id',)
        verbose_name = 'Ticket Details'
        verbose_name_plural = 'Tickets Details'
