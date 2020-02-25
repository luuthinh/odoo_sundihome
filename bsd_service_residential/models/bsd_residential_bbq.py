# -*- coding:utf-8 -*-

try:
    import qrcode
except ImportError:
    qrcode = None
try:
    import base64
except ImportError:
    base64 = None
from io import BytesIO
import uuid
import math
import datetime

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class BsdResidentialBBQ(models.Model):
    _name = 'bsd.residential.bbq'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = "Đăng ký dịch vụ BBQ"
    _rec_name = 'bsd_residential_id'
    _order = 'bsd_start_time desc'

    name = fields.Char(string="Phiếu", required=True, index=True, copy=False, default='New')
    bsd_product_id = fields.Many2one('product.product', string="Dịch vụ", required=True,
                                     states={'draft': [('readonly', False)],
                                             'confirm': [('readonly', True)],

                                             'done': [('readonly', True)],
                                             'cancel': [('readonly', True)]})
    bsd_residential_id = fields.Many2one('bsd.residential', string="Cư dân", required=True,
                                         states={'draft': [('readonly', False)],
                                                 'confirm': [('readonly', True)],
                                                 'done': [('readonly', True)],
                                                 'cancel': [('readonly', True)]}
                                         )
    bsd_partner_id = fields.Many2one('res.partner', related='bsd_residential_id.partner_id')
    bsd_unit_id = fields.Many2one('bsd.unit', related='bsd_residential_id.bsd_unit_id', string="Căn hộ")
    bsd_due_date = fields.Date(string="Ngày đặt", default=fields.Date.today(), required=True,
                               states={'draft': [('readonly', False)],
                                       'confirm': [('readonly', True)],
                                       'done': [('readonly', True)],
                                       'cancel': [('readonly', True)]}
                               )
    bsd_duration = fields.Float(string="Thời lượng", required=True,
                                states={'draft': [('readonly', False)],
                                        'confirm': [('readonly', True)],
                                        'done': [('readonly', True)],
                                        'cancel': [('readonly', True)]}
                                )
    bsd_int_person = fields.Integer(string="Số người",
                                    states={'draft': [('readonly', False)],
                                            'confirm': [('readonly', True)],
                                            'done': [('readonly', True)],
                                            'cancel': [('readonly', True)]}
                                    )
    bsd_start_time = fields.Datetime(string="Giờ bắt đầu", required=True,
                                     states={'draft': [('readonly', False)],
                                             'confirm': [('readonly', True)],
                                             'done': [('readonly', True)],
                                             'cancel': [('readonly', True)]}
                                     )
    bsd_end_time = fields.Datetime(string="Giờ kết thúc", required=True,
                                   states={'draft': [('readonly', False)],
                                           'confirm': [('readonly', True)],
                                           'done': [('readonly', True)],
                                           'cancel': [('readonly', True)]}
                                   )
    bsd_position = fields.Char(string="Vị trí")
    bsd_price = fields.Monetary(string="Số tiền", required=True,
                                states={'draft': [('readonly', False)],
                                        'confirm': [('readonly', True)],
                                        'done': [('readonly', True)],
                                        'cancel': [('readonly', True)]}
                                )
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Currency", readonly=True)
    bsd_payment_id = fields.Many2one('account.payment', string="Phiếu thu", readonly=True)
    bsd_registry_date = fields.Date(string="Ngày đăng ký", default=fields.Date.today())
    bsd_cancel_date = fields.Date(string="Ngày hủy")

    bsd_qr_code = fields.Binary(string="Mã QR code", readonly=True)
    state = fields.Selection([('draft', 'Nháp'),
                              ('confirm', 'Đã xác nhận'),
                              ('done', 'Hoàn thành'),
                              ('cancel', 'Hủy')],
                             default='draft',
                             string="Trạng thái")

    bsd_pay_rec_id = fields.Many2one('account.payment', string="Phiếu thu cọc")
    bsd_pay_ret_id = fields.Many2one('account.payment', string="Phiếu trả cọc")
    bsd_deposit = fields.Boolean(string="Yêu cầu cọc")

    @api.onchange('bsd_due_date', 'bsd_duration')
    def _onchange_due_date(self):
        self.bsd_start_time = self.bsd_due_date
        hours = math.floor(self.bsd_duration)
        minutes = (self.bsd_duration - hours) * 60
        time = datetime.timedelta(hours=hours, minutes=minutes)
        self.bsd_end_time = self.bsd_start_time + time

    @api.onchange('bsd_start_time')
    def _onchange_start_time(self):
        hours = math.floor(self.bsd_duration)
        minutes = (self.bsd_duration - hours) * 60
        time = datetime.timedelta(hours=hours, minutes=minutes)
        self.bsd_end_time = self.bsd_start_time + time

    def _generate_access_token(self):
        return str(uuid.uuid4())

    def action_card(self):
        self.write({
            'access_token': self._generate_access_token()
        })
        url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        _logger.debug("action_card")
        _logger.debug(url)
        _logger.debug(self.access_token)
        if qrcode and base64:
            str_qrcode = url + '/service/bbq/' + str(self.id) + '?access_token=' + self.access_token
            qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
            )
            qr.add_data(str_qrcode)
            qr.make(fit=True)
            img = qr.make_image()
            temp = BytesIO()
            img.save(temp, format="PNG")
            qr_image = base64.b64encode(temp.getvalue())
            self.write({
                'bsd_qr_code': qr_image,
                'state': 'confirm',
            })
        else:
            raise UserError(_('Cài đặt các thư viện cần thiết tạo mã qr code'))

    def action_payment(self):
        pay_id = self.env['account.payment'].create({
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'partner_id': self.bsd_partner_id.id,
            'amount': self.bsd_price,
            'communication': 'Thu tiền BBQ',
            'payment_method_id': self.env.ref('account.account_payment_method_manual_in').id,
            'journal_id': 7,
        })
        self.bsd_payment_id = pay_id.id,
        return {
            'type': 'ir.actions.act_window',
            'name': _('Payment'),
            'res_model': 'account.payment',
            'res_id': pay_id.id,
            'view_mode': 'form',
        }

    def action_payment_deposit(self):
        pay_id = self.env['account.payment'].create({
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'partner_id': self.bsd_partner_id.id,
            'amount': self.bsd_price,
            'communication': 'Thu tiền cọc BBQ',
            'payment_method_id': self.env.ref('account.account_payment_method_manual_in').id,
            'journal_id': 7,
        })
        self.bsd_pay_rec_id = pay_id.id,
        return {
            'type': 'ir.actions.act_window',
            'name': _('Payment'),
            'res_model': 'account.payment',
            'res_id': pay_id.id,
            'view_mode': 'form',
        }

    def action_payment_return(self):
        pay_id = self.env['account.payment'].create({
            'payment_type': 'outbound',
            'partner_type': 'customer',
            'partner_id': self.bsd_partner_id.id,
            'amount': self.bsd_price,
            'communication': 'Trả cọc',
            'payment_method_id': self.env.ref('account.account_payment_method_manual_out').id,
            'journal_id': 7,
        })
        self.bsd_pay_ret_id = pay_id.id,
        return {
            'type': 'ir.actions.act_window',
            'name': _('Payment'),
            'res_model': 'account.payment',
            'res_id': pay_id.id,
            'view_mode': 'form',
        }

    def action_done(self):
        self.write({
            'state': 'done'
        })

    def action_cancel(self):
        self.write({
            'state': 'cancel',
            'bsd_cancel_date': fields.Date.today()
        })

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('bsd.residential.bbq') or '/'
        return super(BsdResidentialBBQ, self).create(vals)
