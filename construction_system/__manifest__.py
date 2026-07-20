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
    'depends': ['base','mail','project','purchase','stock','account','account_accountant','documents','sale_management','crm', 'hr','stock_accountant'],

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
     'views/progress_billing.xml',
     'views/sub_contract_views.xml',
     'views/variation_order_views.xml',
     'views/budget_vs_actual_report_views.xml',
     'views/project_progress_report_views.xml',
     'views/cost_center_performance_report.xml',
     'views/project_profitability_report.xml',
     'views/variation_order_report.xml',
     'views/purchase_order_report.xml',
     'views/material_consumption_report.xml',
     'views/cash_flow_report.xml',
     'views/menu.xml',
     'views/views.xml',
     'views/templates.xml',
        
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],


    'assets': {

    'web.assets_backend': [

        'construction_system/static/src/js/dashboard.js',

        'construction_system/static/src/xml/dashboard_template.xml',

        'construction_system/static/src/scss/dashboard.scss',

        'https://cdn.jsdelivr.net/npm/chart.js',


    ],

},
}

