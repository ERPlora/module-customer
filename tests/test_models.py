"""
Unit tests for Customer model.
"""

import pytest
from decimal import Decimal
from django.utils import timezone

from customers.models import Customer


@pytest.mark.django_db
class TestCustomerModel:
    """Tests for Customer model."""

    def test_create_customer_basic(self):
        """Test creating a customer with basic info."""
        customer = Customer.objects.create(
            name="John Doe",
            email="john@example.com",
            phone="+34600123456"
        )

        assert customer.id is not None
        assert customer.name == "John Doe"
        assert customer.email == "john@example.com"
        assert customer.phone == "+34600123456"
        assert customer.is_active is True

    def test_create_customer_full(self):
        """Test creating a customer with all fields."""
        customer = Customer.objects.create(
            name="Jane Smith",
            email="jane@example.com",
            phone="+34600654321",
            address="Calle Mayor 1, Madrid",
            tax_id="12345678Z",
            notes="VIP customer"
        )

        assert customer.address == "Calle Mayor 1, Madrid"
        assert customer.tax_id == "12345678Z"
        assert customer.notes == "VIP customer"

    def test_customer_default_values(self):
        """Test customer default values."""
        customer = Customer.objects.create(name="Test Customer")

        assert customer.total_spent == Decimal('0.00')
        assert customer.visit_count == 0
        assert customer.is_active is True
        assert customer.last_purchase_at is None

    def test_customer_str_representation(self):
        """Test customer string representation."""
        customer = Customer.objects.create(name="Test Customer")

        assert str(customer) == "Test Customer"

    def test_average_purchase_no_visits(self):
        """Test average purchase when no visits."""
        customer = Customer.objects.create(name="New Customer")

        assert customer.average_purchase == Decimal('0.00')

    def test_average_purchase_with_visits(self):
        """Test average purchase calculation."""
        customer = Customer.objects.create(
            name="Regular Customer",
            total_spent=Decimal('100.00'),
            visit_count=4
        )

        assert customer.average_purchase == Decimal('25.00')

    def test_customer_ordering(self):
        """Test customers are ordered by created_at descending."""
        customer1 = Customer.objects.create(name="First")
        customer2 = Customer.objects.create(name="Second")
        customer3 = Customer.objects.create(name="Third")

        customers = list(Customer.objects.all())

        assert customers[0] == customer3
        assert customers[1] == customer2
        assert customers[2] == customer1

    def test_customer_soft_delete(self):
        """Test customer can be soft deleted."""
        customer = Customer.objects.create(name="To Delete")
        assert customer.is_active is True

        customer.is_active = False
        customer.save()

        customer.refresh_from_db()
        assert customer.is_active is False

    def test_customer_email_optional(self):
        """Test email is optional."""
        customer = Customer.objects.create(name="No Email")

        assert customer.email == ""

    def test_customer_phone_optional(self):
        """Test phone is optional."""
        customer = Customer.objects.create(name="No Phone")

        assert customer.phone == ""

    def test_customer_tax_id_optional(self):
        """Test tax_id is optional."""
        customer = Customer.objects.create(name="No Tax ID")

        assert customer.tax_id == ""


@pytest.mark.django_db
class TestCustomerStats:
    """Tests for Customer statistics methods."""

    def test_update_stats_no_sales_module(self):
        """Test update_stats when sales module not installed."""
        customer = Customer.objects.create(name="Test")

        # Should not raise error
        customer.update_stats()

        assert customer.total_spent == Decimal('0.00')
        assert customer.visit_count == 0

    def test_get_recent_purchases_no_sales_module(self):
        """Test get_recent_purchases when sales module not installed."""
        customer = Customer.objects.create(name="Test")

        result = customer.get_recent_purchases()

        assert result == []


@pytest.mark.django_db
class TestCustomerIndexes:
    """Tests for Customer model indexes."""

    def test_name_index_exists(self):
        """Test name field has index."""
        indexes = Customer._meta.indexes
        index_fields = [idx.fields for idx in indexes]

        assert ['name'] in index_fields

    def test_phone_index_exists(self):
        """Test phone field has index."""
        indexes = Customer._meta.indexes
        index_fields = [idx.fields for idx in indexes]

        assert ['phone'] in index_fields

    def test_email_index_exists(self):
        """Test email field has index."""
        indexes = Customer._meta.indexes
        index_fields = [idx.fields for idx in indexes]

        assert ['email'] in index_fields
