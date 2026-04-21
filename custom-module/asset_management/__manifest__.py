{
    'name': 'Asset Management',
    'version': '1.0',
    'category': 'Human Resources/Asset Management',
    'summary': 'Manage company assets and assign them to users',
    'description': """
Asset Management System
=======================
Manage company assets like laptops, monitors, software, and furniture.
Assign assets to users and track history.
    """,
    'depends': ['base', 'mail'],
    'data': [
        'security/asset_security.xml',
        'security/ir.model.access.csv',
        'views/asset_category_views.xml',
        'views/asset_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
