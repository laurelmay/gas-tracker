import abc
import datetime

import pytz

from django.http import HttpResponse
from django.shortcuts import (
    redirect,
    render,
    reverse,
    get_object_or_404,

)
from django.core.exceptions import (
    ValidationError
)
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    UserPassesTestMixin,
)
from django.views.generic.detail import DetailView
from django.views.generic.edit import (
    FormView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.views.generic.list import ListView
from django.utils import (
    timezone,
)

from .models import (
    Car,
    CarLinkedEntry,
    GasPurchase,
    Maintenance,
    User,
    Toll,
)

from .forms import (
    GasPurchaseForm,
)

_PAGE_SIZE = 10


def index(request):
    return render(request, "gas/index.html")


def set_timezone(request):
    if request.method == 'POST':
        request.session['django_timezone'] = request.POST['timezone']
        return redirect('/')
    else:
        return render(request, 'gas/user_timezone.html', {'timezones': pytz.common_timezones})


class NewCarLinkedFieldView(LoginRequiredMixin, CreateView):

    model = CarLinkedEntry
    fields = [
        'datetime',
        'vehicle'
    ]

    def form_valid(self, form):
        entry = form.save(commit=False)
        entry.owner = entry.vehicle.owner
        entry.save()
        return redirect(self.success_url)

    def get_form(self, *args, **kwargs):
        user = self.request.user
        form = super(NewCarLinkedFieldView, self).get_form(*args, **kwargs)
        form.fields['datetime'].label = "Date & Time"
        form.fields['vehicle'].queryset = Car.objects.filter(owner=user)
        return form

    def get_success_url(self):
        return reverse('car-detail', args=(self.object.vehicle.uuid, ))

    def get_initial(self):
        values = {}
        try:
            car = Car.objects.get(uuid=self.request.GET.get("uuid"))
            values['vehicle'] = car
        except (Car.DoesNotExist, ValidationError):
            pass

        values['datetime'] = timezone.now()

        return values


class CarLinkedFieldListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = CarLinkedEntry
    paginate_by = _PAGE_SIZE

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['car'] = Car.objects.get(uuid=self.kwargs.get("uuid"))
        return context

    def get_queryset(self):
        car = Car.objects.get(uuid=self.kwargs.get("uuid"))
        return self.model.objects.filter(vehicle=car)

    def test_func(self):
        car = Car.objects.get(uuid=self.kwargs.get("uuid"))
        return car.owner == self.request.user and all(obj.owner == self.request.user for obj in self.get_queryset())


class CarLinkedFieldUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = CarLinkedEntry
    fields = [
        'datetime',
        'vehicle'
    ]

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        form.fields['datetime'].label = "Date & time"
        return form

    def get_object(self, queryset=None):
        return get_object_or_404(self.model, uuid=self.kwargs.get("entry_id"))

    def get_success_url(self):
        return reverse('car-detail', args=(self.object.vehicle.uuid,))

    def test_func(self):
        return len(set((self.get_object().vehicle.owner, self.request.user, self.get_object().owner))) == 1


class CarLinkedFieldDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = CarLinkedEntry

    def get_object(self, queryset=None):
        return get_object_or_404(self.model, uuid=self.kwargs.get("entry_id"))

    def get_success_url(self):
        return reverse('car-detail', args=(self.object.vehicle.uuid,))

    def test_func(self):
        return len(set((self.get_object().vehicle.owner, self.request.user, self.get_object().owner))) == 1


## CAR ##


class CarListView(LoginRequiredMixin, ListView):
    model = Car
    template_name = 'gas/user_car_list.html'

    def get_queryset(self):
        user = self.request.user
        return Car.objects.filter(owner=user)


class CarDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Car
    template_name = 'gas/car-detail.html'
    raise_exception = False

    def get_queryset(self):
        return Car.objects.filter(owner=self.request.user)

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()

        return get_object_or_404(Car, uuid=self.kwargs.get("uuid"))

    def test_func(self):
        return self.get_object().owner == self.request.user


class NewCarView(LoginRequiredMixin, CreateView):
    model = Car
    success_url = '/cars'
    fields = [
        'make',
        'model',
        'year',
        'purchase_date',
        'vin',
        'nickname',
    ]

    def form_valid(self, form):
        car = form.save(commit=False)
        car.owner = self.request.user
        if not car.nickname.strip():
            car.nickname = None
        car.save()
        return redirect(self.success_url)


class CarUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Car
    fields = [
        'make',
        'model',
        'year',
        'purchase_date',
        'purchase_price',
        'vin',
        'nickname',
    ]

    def form_valid(self, form):
        car = form.save(commit=False)
        if not (isinstance(car.nickname, str) and car.nickname.strip()):
            car.nickname = None
        else:
            car.nickname = car.nickname.strip()
        car.save()
        return redirect(self.get_success_url())

    def get_object(self):
        return get_object_or_404(Car, uuid=self.kwargs.get("uuid"))

    def get_success_url(self):
        return reverse('car-detail', args=(self.get_object().uuid,))

    def test_func(self):
        return self.get_object().owner == self.request.user


class CarDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Car

    def get_object(self, queryset=None):
        return get_object_or_404(Car, uuid=self.kwargs.get("uuid"))

    def get_success_url(self):
        return reverse('cars')

    def test_func(self):
        return self.get_object().owner == self.request.user


## GAS PURCHASE ##


class GasPurchaseListView(CarLinkedFieldListView):
    model = GasPurchase
    template_name = 'gas/car_gas_list.html'


class NewPurchaseView(NewCarLinkedFieldView):
    model = GasPurchase
    fields = [
        'vehicle',
        'datetime',
        'odometer_reading',
        'gallons',
        'cost_per_gallon',
    ]


class GasPurchaseUpdateView(CarLinkedFieldUpdateView):
    model = GasPurchase
    fields = [
        'vehicle',
        'datetime',
        'odometer_reading',
        'gallons',
        'cost_per_gallon',
    ]


class GasPurchaseDeleteView(CarLinkedFieldDeleteView):
    model = GasPurchase


class MaintenanceListView(CarLinkedFieldListView):
    model = Maintenance
    template_name = 'gas/car_maintenance_list.html'


class NewMaintenanceView(NewCarLinkedFieldView):
    model = Maintenance
    fields = [
        'vehicle',
        'datetime',
        'odometer_reading',
        'description',
        'cost',
    ]


class MaintenanceUpdateView(CarLinkedFieldUpdateView):
    model = Maintenance
    fields = [
        'vehicle',
        'datetime',
        'odometer_reading',
        'description',
        'cost',
    ]

class MaintenanceDeleteView(CarLinkedFieldDeleteView):
    model = Maintenance


class NewTollView(NewCarLinkedFieldView):
    model = Toll
    fields = [
        'vehicle',
        'datetime',
        'cost',
        'description',
    ]

class TollListView(NewCarLinkedFieldView):
    model = Toll
    template_name = "gas/car-toll-list.html"


class TollUpdateView(CarLinkedFieldUpdateView):
    model = Toll
    fields = NewTollView.fields


class TollDeleteView(CarLinkedFieldDeleteView):
    model = Toll