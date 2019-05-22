import datetime

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
    GasPurchase,
    Maintenance,
    User,
)

from .forms import (
    GasPurchaseForm,
)


def index(request):
    return render(request, "gas/index.html")


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
    ]

    def form_valid(self, form):
        car = form.save(commit=False)
        car.owner = self.request.user
        car.save()
        return redirect(self.success_url)


class CarUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Car
    fields = [
        'make',
        'model',
        'year',
        'purchase_date',
        'vin',
    ]

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


class GasPurchaseListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = GasPurchase
    template_name = 'gas/car_gas_list.html'

    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['car'] = Car.objects.get(uuid=self.kwargs.get("uuid"))
        return context

    def get_queryset(self):
        car = Car.objects.get(uuid=self.kwargs.get("uuid"))
        return GasPurchase.objects.filter(vehicle=car)

    def test_func(self):
        car = Car.objects.get(uuid=self.kwargs.get("uuid"))
        return car.owner == self.request.user


class NewPurchaseView(LoginRequiredMixin, CreateView):
    model = GasPurchase
    fields = [
        'vehicle',
        'datetime',
        'odometer_reading',
        'gallons',
        'cost_per_gallon',
    ]

    def get_form(self, *args, **kwargs):
        user = self.request.user
        form = super(NewPurchaseView, self).get_form(*args, **kwargs)
        form.fields['vehicle'].queryset = Car.objects.filter(owner=user)
        return form

    def get_success_url(self):
        return reverse('car-detail', args=(self.object.vehicle.uuid,))

    def get_initial(self):
        values = {}
        try:
            car = Car.objects.get(uuid=self.request.GET.get("uuid"))
            values['vehicle'] = car
        except (Car.DoesNotExist, ValidationError):
            pass

        values['datetime'] = timezone.now()

        return values


class GasPurchaseUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = GasPurchase
    fields = [
        'vehicle',
        'datetime',
        'odometer_reading',
        'gallons',
        'cost_per_gallon',
    ]

    def get_object(self, queryset=None):
        return get_object_or_404(GasPurchase, uuid=self.kwargs.get("gas_id"))

    def get_success_url(self):
        return reverse('car-detail', args=(self.object.vehicle.uuid,))

    def test_func(self):
        return self.get_object().vehicle.owner == self.request.user


class GasPurchaseDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = GasPurchase

    def get_object(self, queryset=None):
        return get_object_or_404(GasPurchase, uuid=self.kwargs.get("gas_id"))

    def get_success_url(self):
        return reverse('car-detail', args=(self.object.vehicle.uuid,))

    def test_func(self):
        return self.get_object().vehicle.owner == self.request.user


## MAINTENANCE ##


class MaintenanceListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Maintenance
    template_name = 'gas/car_maintenance_list.html'

    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['car'] = Car.objects.get(uuid=self.kwargs.get("uuid"))
        return context

    def get_queryset(self):
        car = Car.objects.get(uuid=self.kwargs.get("uuid"))
        return Maintenance.objects.filter(vehicle=car)

    def test_func(self):
        car = Car.objects.get(uuid=self.kwargs.get("uuid"))
        return car.owner == self.request.user


class NewMaintenanceView(LoginRequiredMixin, CreateView):
    model = Maintenance
    fields = [
        'vehicle',
        'datetime',
        'odometer_reading',
        'description',
        'cost',
    ]

    def get_form(self, *args, **kwargs):
        user = self.request.user
        form = super(NewMaintenanceView, self).get_form(*args, **kwargs)
        form.fields['vehicle'].queryset = Car.objects.filter(owner=user)
        return form

    def get_success_url(self):
        return reverse('car-detail', args=(self.object.vehicle.uuid,))

    def get_initial(self):
        values = {}
        try:
            car = Car.objects.get(uuid=self.request.GET.get("uuid"))
            values['vehicle'] = car
        except (Car.DoesNotExist, ValidationError):
            pass

        values['datetime'] = timezone.now()

        return values

class MaintenanceUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Maintenance
    fields = [
        'vehicle',
        'datetime',
        'odometer_reading',
        'description',
        'cost',
    ]

    def get_object(self, queryset=None):
        return get_object_or_404(Maintenance, uuid=self.kwargs.get("maint_id"))

    def get_success_url(self):
        return reverse('car-detail', args=(self.object.vehicle.uuid,))

    def test_func(self):
        return self.get_object().vehicle.owner == self.request.user


class MaintenanceDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Maintenance

    def get_object(self, queryset=None):
        return get_object_or_404(Maintenance, uuid=self.kwargs.get("maint_id"))

    def get_success_url(self):
        return reverse('car-detail', args=(self.object.vehicle.uuid,))

    def test_func(self):
        return self.get_object().vehicle.owner == self.request.user


