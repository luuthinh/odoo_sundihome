# -*- coding:utf-8 -*-
{
    'name': 'BSD Residential V0.1',
    'version': '0.1',
    'category': 'Module',
    'author': 'Thịnh Lưu',
    'depends': [
                'bsd_real_estate',
                'base',
                'sale',
                'stock',
                'product',
                'sale_product_configurator',
    ],
    'data': [
        'security/bsd_security.xml',
        'security/ir.model.access.csv',
        'views/res_partner_views.xml',
        'data/bsd_registry_request_data.xml',
        'views/bsd_registry_request_views.xml',
        'views/account_asset_views.xml',
        'views/bsd_registry_service_views.xml',
        'views/bsd_residential_vehicle_views.xml',
        'views/bsd_residential_views.xml',
        'views/menu_item_views.xml',
        'wizards/bsd_wizard_registry_request_view.xml',
        'views/sale_order_views.xml',
    ],
}