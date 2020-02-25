# -*- coding:utf-8 -*-
{
    'name': 'BSD Quản lý hợp đồng',
    'version': '0.1',
    'category': 'App',
    'author': 'Thịnh Lưu',
    'depends': [
                'base',
                'bsd_block',
                'contacts',
                'bsd_residential',
                'hr',
                'account',
    ],
    'data': [
        'security/user_groups.xml',
        'security/bsd_security.xml',
        'security/ir.model.access.csv',
        'views/bsd_contract_tenancy_views.xml',
        'views/res_partner_views.xml',
        'views/account_payment_views.xml',
        'views/bsd_contract_sale_views.xml',
        'views/menu_item_views.xml',
        'wizards/bsd_tenancy_renew_views.xml',
        'views/bsd_unit_views.xml'
    ],
    'application': True,
}