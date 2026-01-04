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

        This module LISTENS to:
        - sale_completed: To update customer purchase history

        This module provides HOOKS:
        - customers.before_customer_save: Called before saving customer
        - customers.after_customer_save: Called after saving customer
        - customers.filter_customer_data: Filter customer data before save
        - customers.filter_customer_list: Filter customer list queries

        This module provides SLOTS:
        - customers.list_actions: Actions in customer list toolbar
        - customers.card_header: Badge area on customer card
        - customers.card_actions: Action buttons on customer card
        - customers.detail_tabs: Additional tabs in detail view
        - customers.detail_sidebar: Sidebar in detail view
        """
        self._register_signal_handlers()
        self._register_hooks()
        self._register_slots()

    def _register_signal_handlers(self):
        """Register handlers for signals."""
        pass  # Signals are emitted in views/models when actions occur

    def _register_hooks(self):
        """
        Register hooks that this module OFFERS to other modules.

        Other modules can use these hooks to:
        - Validate customer changes before they happen
        - Modify customer data before saving
        - Filter customer listings
        """
        pass

    def _register_slots(self):
        """
        Register slots that this module OFFERS to other modules.

        Slots are template injection points where other modules
        can add their content.
        """
        pass

    # =========================================================================
    # Hook Helper Methods (called from views)
    # =========================================================================

    @staticmethod
    def do_before_customer_save(customer, data, user=None):
        """
        Execute before_customer_save hook.

        Called by views before saving customer. Other modules can:
        - Validate the data (raise ValidationError to block)
        - Enrich the data
        - Log the action

        Args:
            customer: Customer instance (None for new)
            data: Dict of customer data
            user: User making the change

        Raises:
            ValidationError: If a hook wants to block the save
        """
        from apps.core.hooks import hooks

        hooks.do_action(
            'customers.before_customer_save',
            customer=customer,
            data=data,
            user=user
        )

    @staticmethod
    def do_after_customer_save(customer, created, user=None):
        """
        Execute after_customer_save hook.

        Called by views after customer has been saved. Other modules can:
        - Update their own data
        - Send notifications
        - Trigger workflows

        Args:
            customer: Customer instance
            created: True if customer was just created
            user: User who made the change
        """
        from apps.core.hooks import hooks

        hooks.do_action(
            'customers.after_customer_save',
            customer=customer,
            created=created,
            user=user
        )

    @staticmethod
    def filter_customer_data(data, customer=None, user=None):
        """
        Apply filter_customer_data hook.

        Called before saving customer data. Other modules can:
        - Add calculated fields
        - Validate data
        - Modify values

        Args:
            data: Dict of customer data
            customer: Existing customer (None for new)
            user: User saving the customer

        Returns:
            Modified data dict
        """
        from apps.core.hooks import hooks

        return hooks.apply_filters(
            'customers.filter_customer_data',
            data,
            customer=customer,
            user=user
        )

    @staticmethod
    def filter_customer_list(queryset, filters=None, user=None):
        """
        Apply filter_customer_list hook.

        Called when listing customers. Other modules can:
        - Add additional filters
        - Exclude certain customers
        - Annotate with extra data

        Args:
            queryset: Customer queryset
            filters: Applied filters dict
            user: Requesting user

        Returns:
            Modified queryset
        """
        from apps.core.hooks import hooks

        return hooks.apply_filters(
            'customers.filter_customer_list',
            queryset,
            filters=filters,
            user=user
        )
