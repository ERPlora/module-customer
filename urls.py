from django.urls import path
from . import views

app_name = 'customers'

urlpatterns = [
    # List and create
    path('', views.customer_list, name='list'),
    path('api/list/', views.customer_list_ajax, name='list_ajax'),
    path('create/', views.customer_create, name='create'),

    # Detail, update, delete
    path('<int:customer_id>/', views.customer_detail, name='detail'),
    path('<int:customer_id>/edit/', views.customer_edit, name='edit'),
    path('<int:customer_id>/delete/', views.customer_delete, name='delete'),

    # Stats update
    path('<int:customer_id>/update-stats/', views.customer_update_stats, name='update_stats'),

    # Export
    path('export/', views.customers_export, name='export'),

    # Settings
    path('settings/', views.customers_settings, name='settings'),
    path('settings/save/', views.customers_settings_save, name='settings_save'),
]
