from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import (
    Car,
    GasPurchase,
    Maintenance,
    Toll,
    User,
)


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = (
        'uuid', 'make', 'model', 'year', 'purchase_date', 'vin', 'owner'
    )
    list_display_links = (
        'uuid', 'vin'
    )
    search_fields = (
        'uuid', 'vin'
    )

    list_per_page = 25


@admin.register(GasPurchase)
class GasPurchaseAdmin(admin.ModelAdmin):
    list_display = (
        'uuid', 'datetime', 'gallons', 'cost_per_gallon', 'odometer_reading',
        'total_cost', 'vehicle', 'owner'
    )
    list_display_links = (
        'uuid',
    )
    search_fields = (
        'uuid', 'odometer_reading'
    )

    list_per_page = 25


@admin.register(Maintenance)
class MaintenanceAdmin(admin.ModelAdmin):
    list_display = (
        'uuid', 'datetime', 'vehicle', 'odometer_reading', 'cost', 'owner'
    )
    list_display_links = (
        'uuid',
    )
    search_fields = (
        'uuid', 'odometer_reading'
    )

    list_per_page = 25

@admin.register(Toll)
class TollAdmin(admin.ModelAdmin):
    list_display = (
        'uuid', 'datetime', 'vehicle', 'cost', 'owner'
    )
    list_display_links = (
        'uuid',
    )
    search_fields = (
        'uuid', 'vehicle'
    )
    list_per_page = 25

admin.site.register(User, UserAdmin)
