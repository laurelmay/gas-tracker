import abc
import uuid

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, RegexValidator
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
    year = models.CharField(
        max_length=4,
        validators=[RegexValidator(r"\d{4}")],
        error_messages={'invalid': "Enter a valid year"}
    )
    purchase_date = models.DateField()
    purchase_price = models.DecimalField(
        max_digits=9,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        default=0,
    )
    vin = models.CharField(max_length=17)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    nickname = models.CharField(
        max_length=90,
        null=True,
        blank=True,
        validators=[RegexValidator(r"\S+|^$")]
    )

    @property
    def _default_name(self):
        return f"{self.year} {self.make} {self.model} - {self.vin}"

    def __str__(self):
        return self.nickname if self.nickname else self._default_name

    def get_absolute_url(self):
        return reverse('car-detail', kwargs={'uuid': str(self.uuid)})

    @property
    def operating_cost(self):
        gas_total = sum([purchase.total_cost for purchase in self.gaspurchase_set.all()])
        maint_total = sum([maint.cost for maint in self.maintenance_set.all()])
        toll_total = sum([toll.cost for toll in self.toll_set.all()])
        return gas_total + maint_total + toll_total

    @property
    def average_mpg(self):
        gas_purchases = self.gaspurchase_set.order_by('odometer_reading').all()
        if gas_purchases:
            total_gallons = sum([purchase.gallons for purchase in gas_purchases])
            if not total_gallons:
                return 0
            return self.miles_driven / total_gallons

        return 0
    
    @property
    def total_cost_ownership(self):
        return self.purchase_price + self.operating_cost

    @property
    def miles_driven(self):
        gas_purchases = self.gaspurchase_set.order_by('odometer_reading').all()
        if gas_purchases:
            first_odom = gas_purchases[0].odometer_reading
            last_odom = gas_purchases.last().odometer_reading
            return last_odom - first_odom
        return 0

    @property
    def cost_per_mile(self):
        if not self.miles_driven:
            return self.operating_cost
        return self.operating_cost / self.miles_driven


class CarLinkedEntry(models.Model): 
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    datetime = models.DateTimeField()
    vehicle = models.ForeignKey(Car, on_delete=models.SET_NULL, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        abstract = True
        ordering = ['-datetime']


class GasPurchase(CarLinkedEntry):
    gallons = models.DecimalField(
        max_digits=6,
        decimal_places=3,
        validators=[MinValueValidator(0)],
    )
    cost_per_gallon = models.DecimalField(
        max_digits=6,
        decimal_places=3,
        validators=[MinValueValidator(0)],
    )
    odometer_reading = models.IntegerField(
        validators=[MinValueValidator(0)],
    )

    def __str__(self):
        return f"{self.datetime} {self.gallons}@{self.cost_per_gallon}"

    @property
    def total_cost(self):
        return self.cost_per_gallon * self.gallons

    @property
    def tank_mpg(self):
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


class Maintenance(CarLinkedEntry):
    cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    odometer_reading = models.IntegerField(
        validators=[MinValueValidator(0)],
    )
    description = models.TextField()

    class Meta:
        ordering = ['-odometer_reading']


class Toll(CarLinkedEntry):
    cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    description = models.TextField()

    class Meta:
        ordering = ['-datetime']