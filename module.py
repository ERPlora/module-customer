"""
Customers Module Configuration

This file defines the module metadata and navigation for the Customers module.
Used by the @module_view decorator to automatically render navigation tabs.
"""
from django.utils.translation import gettext_lazy as _

# Module Identification
MODULE_ID = "customers"
MODULE_NAME = _("Customers")
MODULE_ICON = "people-outline"
MODULE_VERSION = "1.0.0"
MODULE_CATEGORY = "crm"

# Target Industries (business verticals this module is designed for)
MODULE_INDUSTRIES = [
    "retail",       # Retail stores
    "wholesale",    # Wholesale distributors
    "restaurant",   # Restaurants
    "bar",          # Bars & pubs
    "cafe",         # Cafes & bakeries
    "beauty",       # Beauty & wellness
    "consulting",   # Professional services
    "ecommerce",    # E-commerce
]

# Sidebar Menu Configuration
MENU = {
    "label": _("Customers"),
    "icon": "people-outline",
    "order": 20,
    "show": True,
}

# Internal Navigation (Tabs)
NAVIGATION = [
    {
        "id": "list",
        "label": _("Customers"),
        "icon": "people-outline",
        "view": "",
    },
    {
        "id": "create",
        "label": _("New"),
        "icon": "person-add-outline",
        "view": "create",
    },
    {
        "id": "settings",
        "label": _("Settings"),
        "icon": "settings-outline",
        "view": "settings",
    },
]

# Module Dependencies
DEPENDENCIES = []

# Default Settings
SETTINGS = {
    "require_email": False,
    "require_phone": False,
    "allow_duplicates": False,
}

# Permissions
# Format: (action_suffix, display_name) -> becomes "customers.action_suffix"
PERMISSIONS = [
    ("view_customer", _("Can view customers")),
    ("add_customer", _("Can add customers")),
    ("change_customer", _("Can edit customers")),
    ("delete_customer", _("Can delete customers")),
    ("export_customer", _("Can export customers")),
    ("import_customer", _("Can import customers")),
]

# Role Permissions - Default permissions for each system role in this module
# Keys are role names, values are lists of permission suffixes (without module prefix)
# Use ["*"] to grant all permissions in this module
ROLE_PERMISSIONS = {
    "admin": ["*"],  # Full access to all customer permissions
    "manager": [
        "view_customer",
        "add_customer",
        "change_customer",
        "export_customer",
        "import_customer",
    ],
    "employee": [
        "view_customer",
        "add_customer",
        "change_customer",
    ],
}
