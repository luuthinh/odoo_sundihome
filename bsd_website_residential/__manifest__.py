# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Website Residential',
    'category': 'Website/Website',
    'sequence': 140,
    'summary': 'Phiếu đăng kí',
    'version': '1.0',
    'description': "",
    'depends': ['website', 'bsd_residential'],
    'data': [
        'data/website_residential_data.xml',
        'views/assets.xml',
        'views/templates.xml',
    ],
    'installable': True,
    'application': True,
}
