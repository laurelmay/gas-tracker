import uuid

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.urls import reverse

class User(AbstractUser):
    """
    Custom user class that can be modified later if needed.
    """
    pass


class Car(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    make = models.CharField(max_length=30)
    model = models.CharField(max_length=30)
    year = models.IntegerField()
    purchase_date = models.DateField()
    vin = models.CharField(max_length=17)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)


    def __str__(self):
        return f"{self.make} {self.model} - {self.vin}"

    def get_absolute_url(self):
        return reverse('car-detail', kwargs={'uuid': str(self.uuid)})

    @property
    def operating_cost(self):
        gas_purchases = GasPurchase.objects.filter(vehicle=self)
        maintenances = Maintenance.objects.filter(vehicle=self)
        gas_total = sum([purchase.total_cost for purchase in gas_purchases])
        maint_total = sum([maint.cost for maint in maintenances])
        return gas_total + maint_total


class GasPurchase(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    datetime = models.DateTimeField()
    gallons = models.DecimalField(
        max_digits=6,
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.01'))],
    )
    cost_per_gallon = models.DecimalField(
        max_digits=6,
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.01'))],
    )
    odometer_reading = models.IntegerField(
        validators=[MinValueValidator(0)],
    )
    vehicle = models.ForeignKey(Car, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.datetime} {self.gallons}@{self.cost_per_gallon}"

    @property
    def total_cost(self):
        return self.cost_per_gallon * self.gallons

    @property
    def average_mpg(self):
        # Get all the gas purchases with an odometer reading more than the
        # reading at this purchase, allowing for finding the next reading
        # (the one that is immediately larger than the current purchase).
        qs = GasPurchase.objects.filter(
            vehicle=self.vehicle,
            odometer_reading__gt=self.odometer_reading,
        ).order_by('odometer_reading')
        # An empty query set suggests that there are no larger readings (such
        # as the most recent fill up)
        if not qs:
            return None

        next = qs[0]
        return (next.odometer_reading - self.odometer_reading) / next.gallons

    class Meta:
        ordering = ['-odometer_reading']


class Maintenance(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    datetime = models.DateTimeField()
    cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    odometer_reading = models.IntegerField(
        validators=[MinValueValidator(0)],
    )
    description = models.TextField()
    vehicle = models.ForeignKey(Car, on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['odometer_reading']
