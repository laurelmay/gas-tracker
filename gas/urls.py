from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('cars', views.CarListView.as_view(), name='cars'),
    path('car/<uuid:uuid>/', views.CarDetailView.as_view(), name='car-detail'),
    path('car/<uuid:uuid>/update', views.CarUpdateView.as_view(), name='car-update'),
    path('car/<uuid:uuid>/delete', views.CarDeleteView.as_view(), name='car-delete'),
    path('car/<uuid:car_id>/gas-purchase/<uuid:gas_id>/update', views.GasPurchaseUpdateView.as_view(), name='gas-purchase-update'),
    path('car/<uuid:car_id>/gas-purchase/<uuid:gas_id>/delete', views.GasPurchaseDeleteView.as_view(), name='gas-purchase-delete'),
    path('car/<uuid:car_id>/maintenance/<uuid:maint_id>/update', views.MaintenanceUpdateView.as_view(), name='maintenance-update'),
    path('car/<uuid:car_id>/maintenance/<uuid:maint_id>/delete', views.MaintenanceDeleteView.as_view(), name='maintenance-delete'),
    path('car/<uuid:uuid>/gas-purchases', views.GasPurchaseListView.as_view(), name='car-gas-purchases'),
    path('car/<uuid:uuid>/maintenances', views.MaintenanceListView.as_view(), name='car-maintenances'),
    path('add-purchase', views.NewPurchaseView.as_view(), name='add-purchase'),
    path('add-car', views.NewCarView.as_view(), name='add-car'),
    path('add-maintenance', views.NewMaintenanceView.as_view(), name='add-maintenance'),
]
