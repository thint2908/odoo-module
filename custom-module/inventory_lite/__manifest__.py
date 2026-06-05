{
    "name": "Inventory Lite",
    "version": "18.0.1.0.0",
    "category": "Inventory",
    "summary": "Simple inventory module for learning Odoo ORM",
    "depends": ["base"],
    "data": [
        "security/ir.model.access.csv",
        "views/inventory_menu_views.xml",
        "views/inventory_product_views.xml",
        "views/inventory_location_views.xml",
        ],
    "installable": True,
    "application": True,
} # pyright: ignore[reportUnusedExpression]