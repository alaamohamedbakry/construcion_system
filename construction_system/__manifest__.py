# -*- coding: utf-8 -*-
{
    'name': "Construction System",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',
    'application': True,
    # any module necessary for this one to work correctly
    'depends': ['base','mail','project','purchase','stock','account','account_accountant','documents','sale_management','crm', 'hr'],

    # always loaded
    'data': [
     'security/ir.model.access.csv',

     'data/bid_file_sequence.xml',

     'views/bid_view.xml',
     'views/boq_views.xml',
     'views/estimation.xml',
     'views/tender_views.xml',
     'views/contract_view.xml',
     'views/material_request_views.xml',
     'views/project_views.xml',
     'views/cost_center_views.xml',
     'views/project_task_views.xml',
     'views/project_project_views.xml',
     'views/purchase_order_views.xml',
     'views/account_move_views.xml',
     'views/menu.xml',
     'views/views.xml',
     'views/templates.xml',
        
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

