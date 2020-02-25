# -*- coding:utf-8 -*-
{
    'name': 'BSD Quản lý tòa nhà',
    'version': 'V1',
    'category': 'App',
    'author': 'Thịnh Lưu',
    'depends': [
                'base',
                'mail',
                'portal',
                'stock',
                'hr',
                'uom',
    ],
    'data': [
        'security/user_groups.xml',
        'security/ir.model.access.csv',
        'security/bsd_security.xml',
        'views/bsd_block_views.xml',
        'views/bsd_floor_views.xml',
        'views/bsd_unit_views.xml',
        'views/product_template_views.xml',
        'views/stock_production_lot_views.xml',
        'views/bsd_menu_views.xml',
        'data/bsd_unit_data.xml'
    ],
    'application': True,
}