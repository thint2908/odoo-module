{
    'name': 'Mini Inventory',
    'version': '18.0.1.0.0',
    'category': 'Inventory',
    'summary': 'Mini Inventory',
    'depends': ['base', 'mail'],
    'data': [
        'security/todo_task_security.xml',
        'security/ir.model.access.csv',
        #data seed
        'data/location_data.xml',
        
        #views
        'views/product_views.xml',
        'views/location_views.xml',
        'views/move_views.xml',
        'views/picking_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': True,
}