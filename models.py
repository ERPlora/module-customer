from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from decimal import Decimal


class Customer(models.Model):
    """
    Customer model for managing client information and purchase history.
    """
    # Basic Information
    name = models.CharField(max_length=255, verbose_name=_("Name"))
    email = models.EmailField(blank=True, verbose_name=_("Email"))
    phone = models.CharField(max_length=20, blank=True, verbose_name=_("Phone"))
    address = models.TextField(blank=True, verbose_name=_("Address"))
    tax_id = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("Tax ID"),
        help_text=_("DNI/NIF/CIF/VAT Number")
    )

    # Calculated Fields (updated via signals or methods)
    total_spent = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name=_("Total Spent")
    )
    visit_count = models.IntegerField(default=0, verbose_name=_("Visit Count"))

    # Metadata
    notes = models.TextField(blank=True, verbose_name=_("Notes"))
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))
    last_purchase_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Last Purchase"))

    class Meta:
        app_label = 'customers'
        verbose_name = _("Customer")
        verbose_name_plural = _("Customers")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['phone']),
            models.Index(fields=['email']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return self.name

    def update_stats(self):
        """
        Update calculated fields (total_spent, visit_count, last_purchase_at).
        Call this method after a sale is completed.
        """
        # Import here to avoid circular imports
        try:
            from sales.models import Sale
            sales = Sale.objects.filter(
                customer_name=self.name,  # Match by name (simplified)
                status=Sale.STATUS_COMPLETED
            )

            self.visit_count = sales.count()
            self.total_spent = sales.aggregate(
                total=models.Sum('total')
            )['total'] or Decimal('0.00')

            last_sale = sales.order_by('-created_at').first()
            if last_sale:
                self.last_purchase_at = last_sale.created_at

            self.save()
        except ImportError:
            # Sales plugin not installed
            pass

    def get_recent_purchases(self, limit=10):
        """
        Get recent purchases for this customer.
        """
        try:
            from sales.models import Sale
            return Sale.objects.filter(
                customer_name=self.name,
                status=Sale.STATUS_COMPLETED
            ).order_by('-created_at')[:limit]
        except ImportError:
            return []

    @property
    def average_purchase(self):
        """
        Calculate average purchase amount.
        """
        if self.visit_count > 0:
            return self.total_spent / self.visit_count
        return Decimal('0.00')
