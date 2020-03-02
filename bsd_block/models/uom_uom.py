# -*- coding:utf-8 -*-

from odoo import fields, models


class UomCategory(models.Model):
    _inherit = 'uom.category'

    measure_type = fields.Selection(selection_add=[('time', 'Tính theo tháng'),
                                                   ('m2month', 'Tính theo diện tích * tháng'),
                                                   ('kw', "Tính điện năng")])
