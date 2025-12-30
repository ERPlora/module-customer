from django.apps import AppConfig


class CustomersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'customers'
    verbose_name = 'Customer Management'

    def ready(self):
        """
        Register extension points for the Customers module.

        This module EMITS signals:
        - customer_created: When a new customer is created
        - customer_updated: When a customer is modified
        - customer_deleted: When a customer is deleted

        This module provides SLOTS:
        - customers.list_actions: Actions in customer list toolbar
        - customers.card_header: Badge area on customer card
        - customers.card_actions: Action buttons on customer card
        - customers.detail_tabs: Additional tabs in detail view
        - customers.detail_sidebar: Sidebar in detail view
        """
        pass  # Signals are emitted in views/models when actions occur
