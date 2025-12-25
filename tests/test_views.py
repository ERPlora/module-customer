"""
Integration tests for Customer views.
"""

import pytest
import json
from decimal import Decimal
from django.test import Client
from django.urls import reverse

from customers.models import Customer


@pytest.fixture
def client():
    """Create test client."""
    return Client()


@pytest.fixture
def sample_customer():
    """Create a sample customer."""
    return Customer.objects.create(
        name="Test Customer",
        email="test@example.com",
        phone="+34600123456",
        address="Test Address",
        tax_id="12345678Z"
    )


@pytest.mark.django_db
class TestCustomerListView:
    """Tests for customer list view."""

    def test_customer_list_get(self, client):
        """Test GET customer list."""
        response = client.get('/modules/customers/')

        assert response.status_code == 200
        assert 'total_customers' in response.context

    def test_customer_list_htmx(self, client):
        """Test HTMX request returns partial."""
        response = client.get(
            '/modules/customers/',
            HTTP_HX_REQUEST='true'
        )

        assert response.status_code == 200

    def test_customer_list_with_customers(self, client, sample_customer):
        """Test list with existing customers."""
        response = client.get('/modules/customers/')

        assert response.status_code == 200
        assert response.context['total_customers'] == 1


@pytest.mark.django_db
class TestCustomerListAjaxView:
    """Tests for customer list AJAX API."""

    def test_list_ajax_empty(self, client):
        """Test AJAX list when empty."""
        response = client.get('/modules/customers/api/list/')

        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['success'] is True
        assert data['customers'] == []

    def test_list_ajax_with_customers(self, client, sample_customer):
        """Test AJAX list with customers."""
        response = client.get('/modules/customers/api/list/')

        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['success'] is True
        assert len(data['customers']) == 1
        assert data['customers'][0]['name'] == "Test Customer"

    def test_list_ajax_search(self, client, sample_customer):
        """Test AJAX list with search."""
        response = client.get('/modules/customers/api/list/?search=Test')

        data = json.loads(response.content)
        assert len(data['customers']) == 1

        response = client.get('/modules/customers/api/list/?search=NotFound')
        data = json.loads(response.content)
        assert len(data['customers']) == 0

    def test_list_ajax_filter_active(self, client, sample_customer):
        """Test AJAX list filter by active status."""
        # Create inactive customer
        Customer.objects.create(name="Inactive", is_active=False)

        response = client.get('/modules/customers/api/list/?status=active')
        data = json.loads(response.content)
        assert len(data['customers']) == 1

        response = client.get('/modules/customers/api/list/?status=inactive')
        data = json.loads(response.content)
        assert len(data['customers']) == 1

        response = client.get('/modules/customers/api/list/?status=all')
        data = json.loads(response.content)
        assert len(data['customers']) == 2


@pytest.mark.django_db
class TestCustomerCreateView:
    """Tests for customer create view."""

    def test_create_get_form(self, client):
        """Test GET create form."""
        response = client.get('/modules/customers/create/')

        assert response.status_code == 200

    def test_create_customer_success(self, client):
        """Test POST create customer."""
        response = client.post('/modules/customers/create/', {
            'name': 'New Customer',
            'email': 'new@example.com',
            'phone': '+34600111222'
        })

        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['success'] is True
        assert 'customer_id' in data

        customer = Customer.objects.get(id=data['customer_id'])
        assert customer.name == 'New Customer'

    def test_create_customer_no_name(self, client):
        """Test POST create customer without name."""
        response = client.post('/modules/customers/create/', {
            'email': 'new@example.com'
        })

        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['success'] is False
        assert 'error' in data


@pytest.mark.django_db
class TestCustomerDetailView:
    """Tests for customer detail view."""

    def test_detail_view(self, client, sample_customer):
        """Test GET customer detail."""
        response = client.get(f'/modules/customers/{sample_customer.id}/')

        assert response.status_code == 200
        assert response.context['customer'] == sample_customer

    def test_detail_view_not_found(self, client):
        """Test GET customer not found."""
        response = client.get('/modules/customers/99999/')

        assert response.status_code == 404

    def test_detail_view_htmx(self, client, sample_customer):
        """Test HTMX detail request."""
        response = client.get(
            f'/modules/customers/{sample_customer.id}/',
            HTTP_HX_REQUEST='true'
        )

        assert response.status_code == 200


@pytest.mark.django_db
class TestCustomerEditView:
    """Tests for customer edit view."""

    def test_edit_get_form(self, client, sample_customer):
        """Test GET edit form."""
        response = client.get(f'/modules/customers/{sample_customer.id}/edit/')

        assert response.status_code == 200
        assert response.context['customer'] == sample_customer

    def test_edit_customer_success(self, client, sample_customer):
        """Test POST edit customer."""
        response = client.post(f'/modules/customers/{sample_customer.id}/edit/', {
            'name': 'Updated Name',
            'email': 'updated@example.com',
            'phone': '+34600999888',
            'address': 'New Address',
            'tax_id': '87654321X',
            'notes': 'Updated notes',
            'is_active': 'on'
        })

        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['success'] is True

        sample_customer.refresh_from_db()
        assert sample_customer.name == 'Updated Name'
        assert sample_customer.email == 'updated@example.com'

    def test_edit_customer_no_name(self, client, sample_customer):
        """Test POST edit customer without name."""
        response = client.post(f'/modules/customers/{sample_customer.id}/edit/', {
            'name': '',
            'email': 'test@example.com'
        })

        data = json.loads(response.content)
        assert data['success'] is False


@pytest.mark.django_db
class TestCustomerDeleteView:
    """Tests for customer delete view."""

    def test_delete_customer(self, client, sample_customer):
        """Test POST delete customer (soft delete)."""
        response = client.post(f'/modules/customers/{sample_customer.id}/delete/')

        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['success'] is True

        sample_customer.refresh_from_db()
        assert sample_customer.is_active is False

    def test_delete_customer_not_found(self, client):
        """Test delete non-existent customer."""
        response = client.post('/modules/customers/99999/delete/')

        assert response.status_code == 404


@pytest.mark.django_db
class TestCustomerExportView:
    """Tests for customer export view."""

    def test_export_csv(self, client, sample_customer):
        """Test export customers to CSV."""
        response = client.get('/modules/customers/export/')

        assert response.status_code == 200
        assert response['Content-Type'] == 'text/csv'
        assert 'attachment' in response['Content-Disposition']

    def test_export_csv_content(self, client, sample_customer):
        """Test export CSV contains customer data."""
        response = client.get('/modules/customers/export/')

        content = response.content.decode('utf-8')
        assert 'Test Customer' in content
        assert 'test@example.com' in content
