# -*- coding: utf-8 -*-
{
    'name': "My API Module",
    'summary': "Module cung cấp API RESTful",
    'description': """
    Module này xây dựng API RESTful để quản lý student trên Odoo 18.
    Bao gồm các endpoint: GET, POST, PUT, DELETE.
    """,
    'author': "Son",
    
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base','website'],
    'data': [
        'security/ir.model.access.csv',
        'views/templates.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False
}