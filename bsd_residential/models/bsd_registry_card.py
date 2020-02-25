# -*- coding:utf-8 -*-

from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)


class BsdRegistryCard(models.Model):
    _name = 'bsd.registry.card'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = "Mẫu đăng ký thẻ cư dân"

    name = fields.Char(string="Phiếu đăng ký", required=True, index=True, copy=False, default='New', tracking=1)
    bsd_partner_id = fields.Many2one('res.partner', string="Chủ Hộ", states={'draft': [('readonly', False)],
                                     'waiting': [('readonly', True)],
                                     'refuse': [('readonly', True)],
                                     'approve': [('readonly', True)]}, tracking=3)
    bsd_unit_id = fields.Many2one('bsd.unit', string="Unit",
                               states={'draft': [('readonly', False)],
                                       'waiting': [('readonly', True)],
                                       'refuse': [('readonly', True)],
                                       'approve': [('readonly', True)]}, tracking=4)
    bsd_type_card = fields.Selection([('res', 'Thẻ cư dân')], string="Loại thẻ", default='res', required=True,
                                     states={'draft': [('readonly', False)],
                                             'waiting': [('readonly', True)],
                                             'refuse': [('readonly', True)],
                                             'approve': [('readonly', True)]}, tracking=2)
    bsd_request = fields.Selection([('new', 'Cấp mới'), ('renew', 'Cấp lại')], string="Nội dung yêu cầu",
                                   required=True, default='new')
    bsd_send_date = fields.Date(string="Ngày yêu cầu", default=fields.Date.today(),
                                states={'draft': [('readonly', False)],
                                        'waiting': [('readonly', True)],
                                        'refuse': [('readonly', True)],
                                        'approve': [('readonly', True)]}, tracking=5)
    bsd_send_user = fields.Many2one('res.users', 'Người tiếp nhận', default=lambda self: self.env.uid,
                                    readonly=True, tracking=6)

    bsd_line_ids = fields.One2many('bsd.registry.card.line', 'bsd_registry_card_id', string="Danh sách đăng ký",
                                   states={'draft': [('readonly', False)],
                                           'waiting': [('readonly', True)],
                                           'refuse': [('readonly', True)],
                                           'approve': [('readonly', True)]}, tracking=7)
    bsd_free_card = fields.Integer(string="Số thẻ miễn phí")
    bsd_fee_card = fields.Integer(string="Số thẻ tính phí")
    bsd_confirm_date = fields.Date(string="Ngày phê duyệt", readonly=True, tracking=6)
    bsd_confirm_user = fields.Many2one('res.users', 'Người phê duyệt', readonly=True, tracking=10)
    bsd_cap_card = fields.Date(string="Ngày cấp thẻ")
    bsd_int_cap_card = fields.Integer(string="Số lượng thẻ cấp")

    bsd_registry_request_id = fields.Many2one('bsd.registry.request', string="Phiếu đăng ký cư dân")

    state = fields.Selection([('draft', 'Nháp'),
                              ('waiting', 'Chờ duyệt'),
                              ('confirm', 'Đã duyệt'),
                              ('card', 'Cấp thẻ'),
                              ('cancel', 'Hủy')], default='draft', tracking=8, copy=False, string="Trạng thái")

    def action_send(self):
        self.write({
            'state': 'waiting',
        })

    def action_confirm(self):
        self.write({'state': 'confirm',
                    'bsd_confirm_user': self.env.uid,
                    'bsd_confirm_date': fields.Date.today()})

    def action_card(self):
        self.write({
            'state': 'card',
        })

    def action_cancel(self):
        self.write({
            'state': 'cancel',
        })

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            _logger.debug("create new")
            vals['name'] = self.env['ir.sequence'].next_by_code('bsd.registry.card') or '/'
        return super(BsdRegistryCard, self).create(vals)


class BsdRegistryRequestResidential(models.Model):
    _name = 'bsd.registry.card.line'
    _description = 'Thông tin cư dân đăng ký thẻ'

    bsd_registry_card_id = fields.Many2one('bsd.registry.card')
    bsd_residential_id = fields.Many2one('bsd.residential', string="Cư dân")
    bsd_cmnd = fields.Char(related='bsd_residential_id.bsd_cmnd', string="CMND/CCCD")
    bsd_cmnd_date = fields.Date(related='bsd_residential_id.bsd_cmnd_date', string="Ngày cấp")
    bsd_cmnd_state = fields.Char(related='bsd_residential_id.bsd_cmnd_state', string="Nơi cấp")
    bsd_birthday = fields.Date(related="bsd_residential_id.bsd_birthday", string="Ngày sinh")
    bsd_unit_id = fields.Many2one('bsd.unit', string="Unit")

    @api.onchange('bsd_unit_id')
    def _get_residential(self):
        _logger.debug("_get_residential")
        res = {}
        res.update({
            'domain': {'bsd_residential_id': [('bsd_unit_id.id', '=', self.bsd_unit_id.id), ('state', '=', 'in')]}
        })
        _logger.debug(res)
        return res


class BsdResidentialCard(models.Model):
    _name = 'bsd.residential.card'

    name = fields.Char(string="Mã thẻ")
    state = fields.Selection([('new', 'Chưa cấp'),
                              ('active', 'Đã cấp'),
                              ('inactive', 'Ngưng sử dụng')], string="Trạng thái", default="1")
