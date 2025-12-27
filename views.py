from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from django.utils.translation import gettext as _

from apps.core.htmx import htmx_view
from .models import Customer


@require_http_methods(["GET"])
@htmx_view('customers/pages/list.html', 'customers/partials/list_content.html')
def customer_list(request):
    """
    Vista principal de listado de clientes.
    Soporta HTMX para navegación SPA.
    """
    # Stats for dashboard cards
    total_customers = Customer.objects.filter(is_active=True).count()
    inactive_customers = Customer.objects.filter(is_active=False).count()

    return {
        'total_customers': total_customers,
        'inactive_customers': inactive_customers,
        'page_title': _('Clientes'),
    }


@require_http_methods(["GET"])
def customer_list_ajax(request):
    """
    API: Lista de clientes para AJAX con infinite scroll.
    """
    from apps.core.htmx import InfiniteScrollPaginator

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

    # Pagination with infinite scroll
    per_page = int(request.GET.get('per_page', '25'))
    paginator = InfiniteScrollPaginator(customers, per_page=per_page)
    page_data = paginator.get_page(request.GET.get('page', 1))

    # Prepare data
    customers_data = []
    for customer in page_data['items']:
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

    return JsonResponse({
        'success': True,
        'customers': customers_data,
        'has_next': page_data['has_next'],
        'next_page': page_data['next_page'],
        'total_count': page_data['total_count'],
        'page_number': page_data['page_number'],
    })


@require_http_methods(["GET", "POST"])
@htmx_view('customers/pages/form.html', 'customers/partials/form_content.html')
def customer_create(request):
    """
    Vista para crear un nuevo cliente.
    Soporta HTMX para navegación SPA.
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
                return JsonResponse({'success': False, 'error': _('El nombre es obligatorio')})

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
                'message': _('Cliente creado correctamente'),
                'customer_id': customer.id
            })

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return {
        'page_title': _('Nuevo Cliente'),
        'customer': None,
    }


@require_http_methods(["GET"])
@htmx_view('customers/pages/detail.html', 'customers/partials/detail_content.html')
def customer_detail(request, customer_id):
    """
    Vista de detalle de un cliente.
    Soporta HTMX para navegación SPA.
    """
    customer = get_object_or_404(Customer, id=customer_id)

    # Get recent purchases
    recent_purchases = customer.get_recent_purchases(limit=10)

    return {
        'customer': customer,
        'recent_purchases': recent_purchases,
        'page_title': f'{_("Cliente")}: {customer.name}',
    }


@require_http_methods(["GET", "POST"])
@htmx_view('customers/pages/form.html', 'customers/partials/form_content.html')
def customer_edit(request, customer_id):
    """
    Vista para editar un cliente.
    Soporta HTMX para navegación SPA.
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
                return JsonResponse({'success': False, 'error': _('El nombre es obligatorio')})

            customer.save()

            return JsonResponse({
                'success': True,
                'message': _('Cliente actualizado correctamente')
            })

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return {
        'customer': customer,
        'page_title': f'{_("Editar")}: {customer.name}',
    }


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
            'message': _('Cliente desactivado correctamente')
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
