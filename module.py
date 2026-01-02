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
SETTINGS = {}

# Permissions
PERMISSIONS = [
    "customers.view_customer",
    "customers.add_customer",
    "customers.change_customer",
    "customers.delete_customer",
]
