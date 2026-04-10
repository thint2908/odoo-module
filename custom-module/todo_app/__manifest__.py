{
    'name': 'Todo App',
    'version': '18.0.1.0.0',
    'category': 'Productivity',
    'summary': 'Simple Todo Application',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/todo_task_views.xml',
    ],
    'installable': True,
    'application': True,
}