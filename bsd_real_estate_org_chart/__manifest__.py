# -*- coding:utf-8 -*-
{
    'name': 'BSD Real Estate Org Chart',
    'version': '0.1',
    'category': 'App',
    'author': 'Thịnh Lưu',
    'depends': [
                'base', 'bsd_real_estate', 'bsd_residential',
    ],
    'data': [
        'views/assets.xml',
        'views/org_chart_views.xml',
    ],
    'qweb': ['static/xml/*.xml'],
}