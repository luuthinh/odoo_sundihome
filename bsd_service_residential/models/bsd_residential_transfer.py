# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
from odoo.exceptions import ValidationError
_logger = logging.getLogger(__name__)


class BsdResidentialTransfer(models.Model):
    _name = 'bsd.residential.transfer'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = "Mẫu đăng ký chuyển đồ"

    name = fields.Char(string="Phiếu đăng ký", required=True, index=True, copy=False, default='New', tracking=1)
    bsd_type = fields.Selection([('in', 'Chuyển vào'), ('out', 'Chuyển ra')], string="Loại")
    bsd_partner_id = fields.Many2one('res.partner', string="Chủ Hộ", readonly=True, required=True,
                                     states={'draft': [('readonly', False)]}, tracking=True)

    bsd_unit_id = fields.Many2one('bsd.unit', string="Unit", readonly=True, required=True,
                                  states={'draft': [('readonly', False)]}, tracking=True)
    bsd_registry_date = fields.Date(string="Ngày đăng ký", default=fields.Date.today())
    bsd_from_date = fields.Datetime(string="Thời gian bắt đầu", default=fields.Datetime.today())
    bsd_to_date = fields.Datetime(string="Thời gian kết thúc", default=fields.Datetime.today())
    bsd_elevator = fields.Selection([('yes', 'Có'), ('no', 'Không')], string="Thang máy")
    bsd_item_ids = fields.One2many('bsd.residential.transfer.item', 'bsd_residential_transfer_id',
                                   string="Bảng kê tài sản")
    state = fields.Selection([('draft', 'Nháp'),
                              ('send', 'Chờ duyệt'),
                              ('confirm', 'Phê duyệt'),
                              ('refuse', 'Từ chối'),
                              ('cancel', 'Hủy')], string="Trạng thái", default='draft')

    def action_send(self):
        self.write({
            'state': 'send'
        })

    def action_confirm(self):
        self.write({
            'state': 'confirm'
        })

    def action_refuse(self):
        self.write({
            'state': 'refuse'
        })

    def action_cancel(self):
        self.write({
            'state': 'cancel'
        })

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('bsd.residential.transfer') or '/'
        return super(BsdResidentialTransfer, self).create(vals)


class BsdResidentialTransferItem(models.Model):
    _name = 'bsd.residential.transfer.item'
    _description = 'Bảng kê tài sản'

    name = fields.Char(string="Loại tài sản")
    bsd_count = fields.Integer(string="Số lượng")
    bsd_residential_transfer_id = fields.Many2one('bsd.residential.transfer', string="Mẫu đăng ký chuyển đồ")

