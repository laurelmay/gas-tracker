from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),

    path('cars', views.CarListView.as_view(), name='cars'),
    path('car/<uuid:uuid>/', views.CarDetailView.as_view(), name='car-detail'),
    path('car/<uuid:uuid>/update', views.CarUpdateView.as_view(), name='car-update'),
    path('car/<uuid:uuid>/delete', views.CarDeleteView.as_view(), name='car-delete'),

    path('car/<uuid:car_id>/gas-purchase/<uuid:entry_id>/update', views.GasPurchaseUpdateView.as_view(), name='gas-purchase-update'),
    path('car/<uuid:car_id>/gas-purchase/<uuid:entry_id>/delete', views.GasPurchaseDeleteView.as_view(), name='gas-purchase-delete'),

    path('car/<uuid:car_id>/maintenance/<uuid:entry_id>/update', views.MaintenanceUpdateView.as_view(), name='maintenance-update'),
    path('car/<uuid:car_id>/maintenance/<uuid:entry_id>/delete', views.MaintenanceDeleteView.as_view(), name='maintenance-delete'),

    path('car/<uuid:car_id>/toll/<uuid:entry_id>/update', views.TollUpdateView.as_view(), name='toll-update'),
    path('car/<uuid:car_id>/toll/<uuid:entry_id>/delete', views.TollDeleteView.as_view(), name='toll-delete'),

    path('car/<uuid:uuid>/gas-purchases', views.GasPurchaseListView.as_view(), name='car-gas-purchases'),
    path('car/<uuid:uuid>/maintenances', views.MaintenanceListView.as_view(), name='car-maintenances'),
    path('car/<uuid:uuid>/tolls', views.TollListView.as_view(), name='car-tolls'),

    path('add-purchase', views.NewPurchaseView.as_view(), name='add-purchase'),
    path('add-car', views.NewCarView.as_view(), name='add-car'),
    path('add-maintenance', views.NewMaintenanceView.as_view(), name='add-maintenance'),
    path('add-toll', views.NewTollView.as_view(), name='add-toll'),

    path('set-timezone', views.set_timezone, name='set-timezone'),
]
