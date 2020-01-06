# -*- coding:utf-8 -*-
{
    'name': 'BSD PriceList V0.1',
    'version': '0.1',
    'category': 'Module',
    'author': 'Thịnh Lưu',
    'depends': [
                'bsd_real_estate',
                'bsd_residential'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/product_pricelist_views.xml',
        'views/bsd_unit_views.xml',
        'views/account_move_views.xml',
        'views/res_partner_views.xml',
        'views/bsd_contract_sale_views.xml',
    ],
}