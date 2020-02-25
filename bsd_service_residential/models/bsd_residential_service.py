# -*- coding:utf-8 -*-

from odoo import models, fields, api


class BsdResidentialElectric(models.Model):
    _name = 'bsd.residential.electric'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Chỉ số điện'
    _rec_name = 'bsd_unit_id'

    bsd_unit_id = fields.Many2one('bsd.unit', string='Unit', required=True)
    bsd_partner_id = fields.Many2one('res.partner', string='Chủ hộ')

    bsd_old_index = fields.Float(string="Chỉ số (cũ)", required=True)
    bsd_new_index = fields.Float(string="Chỉ số (mới)", required=True)

    bsd_old_employee_id = fields.Many2one('hr.employee', string='Nhân viên ghi tháng trước')
    bsd_new_employee_id = fields.Many2one('hr.employee', string='Nhân viên ghi tháng này')

    bsd_old_date = fields.Date(string="Ngày ghi tháng trước", required=True)
    bsd_new_date = fields.Date(string="Ngày ghi tháng này", required=True)

    bsd_total = fields.Float(string='Tổng số tiêu thụ',required=True)
    bsd_price = fields.Float(string='Số tiền', required=True)

    bsd_product_id = fields.Many2one('product.product', string='Dịch vụ', required=True)

    bsd_year = fields.Selection([(str(num), str(num)) for num in range(2020, 2100)],
                                string='Năm',
                                default='2020', required=True)
    bsd_month = fields.Selection([(str(num), str(num)) for num in range(1, 12)],
                                 string='Tháng',
                                 default='1', required=True)


class BsdResidentialWater(models.Model):
    _name = 'bsd.residential.water'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Chỉ số nước'
    _rec_name = 'bsd_unit_id'

    bsd_unit_id = fields.Many2one('bsd.unit', string='Unit', required=True)
    bsd_partner_id = fields.Many2one('res.partner', string='Chủ hộ')

    bsd_old_index = fields.Float(string="Chỉ số (cũ)", required=True)
    bsd_new_index = fields.Float(string="Chỉ số (mới)", required=True)

    bsd_old_employee_id = fields.Many2one('hr.employee', string='Nhân viên ghi tháng trước')
    bsd_new_employee_id = fields.Many2one('hr.employee', string='Nhân viên ghi tháng này')

    bsd_old_date = fields.Date(string="Ngày ghi tháng trước", required=True)
    bsd_new_date = fields.Date(string="Ngày ghi tháng này", required=True)

    bsd_total = fields.Float(string='Tổng số tiêu thụ', required=True)
    bsd_price = fields.Float(string='Số tiền', required=True)

    bsd_product_id = fields.Many2one('product.product', string='Dịch vụ', required=True)
    bsd_year = fields.Selection([(str(num), str(num)) for num in range(2020, 2100)],
                                string='Năm',
                                default='2020', required=True)
    bsd_month = fields.Selection([(str(num), str(num)) for num in range(1, 12)],
                                 string='Tháng',
                                 default='1', required=True)
