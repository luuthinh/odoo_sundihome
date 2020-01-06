# -*- coding:utf-8 -*-
{
    'name': 'BSD Manager Project V0.1',
    'version': '0.1',
    'category': 'App',
    'author': 'Thịnh Lưu',
    'depends': [
                'base', 'mail'
    ],
    'data': [
        'security/user_groups.xml',
        'security/ir.model.access.csv',
        'data/bsd_ba_request_data.xml',
        'views/bsd_ba_request_view.xml',
        'views/bsd_project_views.xml',
        'views/bsd_screen_views.xml',
        'views/assets.xml',
        'views/menu_item_views.xml',
        'views/org_chart_views.xml',
    ],
    'qweb': ['static/xml/*.xml'],
    'application': True,
}