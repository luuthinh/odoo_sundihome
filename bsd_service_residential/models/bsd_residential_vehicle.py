# -*- coding:utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
import logging
_logger = logging.getLogger(__name__)


class BsdResidentialVehicle(models.Model):
    _name = 'bsd.residential.vehicle'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']
    _description = 'Đăng ký giữ xe'

    bsd_residential_id = fields.Many2one('bsd.residential', string="Cư Dân")
    name = fields.Char(string="Phiếu", required=True, index=True, copy=False, default='New')
    bsd_brand = fields.Char(string="Hiệu Xe", required=True)
    bsd_license = fields.Char(string="Biển kiểm soát", required=True)
    bsd_partner_id = fields.Many2one('bsd.residential', string="Chủ Hộ")
    bsd_unit_id = fields.Many2one('bsd.unit', string="Căn Hộ")
    bsd_note = fields.Char(string="Ghi chú")
    state = fields.Selection([('draft', 'Nháp'),
                              ('send', 'Gửi yêu cầu'),
                              ('card', 'Cấp thẻ'),
                              ('cancel', 'Hủy')],
                             default='draft',
                             string="Trạng thái")
    bsd_date_accuracy = fields.Date(string="Ngày cấp thẻ", readonly=True)
    bsd_product_id = fields.Many2one('product.product', string="Dịch vụ",
                                     domain=[('product_tmpl_id.bsd_type', '=', 'parking_service')])
    bsd_card = fields.Char(string="Mã thẻ", size=8)
    bsd_unit_vehicle_id = fields.Many2one('bsd.unit.vehicle', readonly=True)

    _sql_constraints = [
        ('bsd_card_key', 'UNIQUE (bsd_card)',  'Mã thẻ bị trùng!')
    ]

    def action_send(self):
        self.write({'state': 'send'})

    def action_card(self):
        if not self.bsd_card:
            raise UserError('Nhập mã thẻ')
        self.write({
            'state': 'card',
            'bsd_date_accuracy': fields.Date.today()
        })

    def action_cancel(self):
        self.write({
            'state': 'cancel',
        })
        self.bsd_unit_vehicle_id.write({
            'state': 'deactivate',
        })

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('bsd.residential.vehicle') or '/'
        return super(BsdResidentialVehicle, self).create(vals)