from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from django.contrib import messages
from django.utils.translation import gettext as _
import json

from .models import Customer


@require_http_methods(["GET"])
def customer_list(request):
    """
    Vista principal de listado de clientes.
    """
    # Stats for dashboard cards
    total_customers = Customer.objects.filter(is_active=True).count()
    inactive_customers = Customer.objects.filter(is_active=False).count()

    context = {
        'total_customers': total_customers,
        'inactive_customers': inactive_customers,
        'page_title': 'Customers',
    }
    return render(request, 'customers/list.html', context)


@require_http_methods(["GET"])
def customer_list_ajax(request):
    """
    API: Lista de clientes para AJAX.
    """
    search = request.GET.get('search', '').strip()
    status_filter = request.GET.get('status', 'active')  # active, inactive, all

    customers = Customer.objects.all()

    # Filter by status
    if status_filter == 'active':
        customers = customers.filter(is_active=True)
    elif status_filter == 'inactive':
        customers = customers.filter(is_active=False)

    # Search
    if search:
        customers = customers.filter(
            Q(name__icontains=search) |
            Q(phone__icontains=search) |
            Q(email__icontains=search) |
            Q(tax_id__icontains=search)
        )

    # Order
    customers = customers.order_by('-created_at')

    # Prepare data
    customers_data = []
    for customer in customers[:100]:  # Limit to 100
        customers_data.append({
            'id': customer.id,
            'name': customer.name,
            'phone': customer.phone,
            'email': customer.email,
            'tax_id': customer.tax_id,
            'total_spent': float(customer.total_spent),
            'visit_count': customer.visit_count,
            'average_purchase': float(customer.average_purchase),
            'last_purchase': customer.last_purchase_at.strftime('%Y-%m-%d %H:%M') if customer.last_purchase_at else None,
            'is_active': customer.is_active,
            'created_at': customer.created_at.strftime('%Y-%m-%d'),
        })

    return JsonResponse({'success': True, 'customers': customers_data})


@require_http_methods(["GET", "POST"])
def customer_create(request):
    """
    Vista para crear un nuevo cliente.
    """
    if request.method == 'POST':
        try:
            # Get form data
            name = request.POST.get('name', '').strip()
            email = request.POST.get('email', '').strip()
            phone = request.POST.get('phone', '').strip()
            address = request.POST.get('address', '').strip()
            tax_id = request.POST.get('tax_id', '').strip()
            notes = request.POST.get('notes', '').strip()

            # Validate
            if not name:
                return JsonResponse({'success': False, 'error': 'Name is required'})

            # Create customer
            customer = Customer.objects.create(
                name=name,
                email=email,
                phone=phone,
                address=address,
                tax_id=tax_id,
                notes=notes
            )

            return JsonResponse({
                'success': True,
                'message': _('Customer created successfully'),
                'customer_id': customer.id
            })

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    context = {
        'page_title': 'Create Customer',
    }
    return render(request, 'customers/form.html', context)


@require_http_methods(["GET"])
def customer_detail(request, customer_id):
    """
    Vista de detalle de un cliente.
    """
    customer = get_object_or_404(Customer, id=customer_id)

    # Get recent purchases
    recent_purchases = customer.get_recent_purchases(limit=10)

    context = {
        'customer': customer,
        'recent_purchases': recent_purchases,
        'page_title': f'Customer: {customer.name}',
    }
    return render(request, 'customers/detail.html', context)


@require_http_methods(["GET", "POST"])
def customer_edit(request, customer_id):
    """
    Vista para editar un cliente.
    """
    customer = get_object_or_404(Customer, id=customer_id)

    if request.method == 'POST':
        try:
            # Update fields
            customer.name = request.POST.get('name', '').strip()
            customer.email = request.POST.get('email', '').strip()
            customer.phone = request.POST.get('phone', '').strip()
            customer.address = request.POST.get('address', '').strip()
            customer.tax_id = request.POST.get('tax_id', '').strip()
            customer.notes = request.POST.get('notes', '').strip()
            customer.is_active = request.POST.get('is_active') == 'on'

            # Validate
            if not customer.name:
                return JsonResponse({'success': False, 'error': 'Name is required'})

            customer.save()

            return JsonResponse({
                'success': True,
                'message': _('Customer updated successfully')
            })

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    context = {
        'customer': customer,
        'page_title': f'Edit: {customer.name}',
    }
    return render(request, 'customers/form.html', context)


@require_http_methods(["POST"])
def customer_delete(request, customer_id):
    """
    API: Eliminar un cliente (soft delete).
    """
    try:
        customer = get_object_or_404(Customer, id=customer_id)
        customer.is_active = False
        customer.save()

        return JsonResponse({
            'success': True,
            'message': _('Customer deactivated successfully')
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@require_http_methods(["POST"])
def customer_update_stats(request, customer_id):
    """
    API: Actualizar estadísticas del cliente.
    """
    try:
        customer = get_object_or_404(Customer, id=customer_id)
        customer.update_stats()

        return JsonResponse({
            'success': True,
            'total_spent': float(customer.total_spent),
            'visit_count': customer.visit_count,
            'average_purchase': float(customer.average_purchase)
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@require_http_methods(["GET"])
def customers_export(request):
    """
    Exportar clientes a CSV.
    """
    import csv
    from django.utils import timezone

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="customers_{timezone.now().strftime("%Y%m%d")}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Name', 'Email', 'Phone', 'Tax ID', 'Total Spent', 'Visit Count', 'Created At'])

    customers = Customer.objects.filter(is_active=True).order_by('name')
    for customer in customers:
        writer.writerow([
            customer.name,
            customer.email,
            customer.phone,
            customer.tax_id,
            customer.total_spent,
            customer.visit_count,
            customer.created_at.strftime('%Y-%m-%d'),
        ])

    return response
