# -*-coding:utf-8 -*-

from odoo import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)


class BsdUnit(models.Model):
    _inherit = 'bsd.unit'

    bsd_residential_history_ids = fields.One2many('bsd.residential.history', 'bsd_unit_id', string="Cư đân", readonly=True)
    bsd_count_residential = fields.Integer(string='Số người', compute='_compute_residential', store=True)

    @api.depends('bsd_residential_history_ids', 'bsd_residential_history_ids.state')
    def _compute_residential(self):
        for each in self:
            residential = each.bsd_residential_history_ids.filtered(lambda x: x.state == 'in')
            each.bsd_count_residential = len(residential)


class BsdResidential(models.Model):
    _name = 'bsd.residential'
    _inherits = {'res.partner': 'partner_id'}
    _description = "Cư dân"

    bsd_code = fields.Char(readonly=True, required=True, index=True, copy=False, default='-', tracking=1, string="Mã cư dân")
    bsd_birthday = fields.Date(string="Ngày sinh")
    bsd_cmnd = fields.Char(string="CMND", size=12)
    bsd_cmnd_date = fields.Date(string="Ngày cấp")
    bsd_cmnd_state = fields.Char(string="Nơi cấp")
    bsd_gender = fields.Selection([('men', 'Nam'), ('women', 'Nữ')], string='Giới tính', default='men')

    state = fields.Selection([('in', 'Đang cư trú'), ('out', 'Đã chuyển đi')], default='in', string="Trạng thái",
                             compute='_compute_state', store=True)
    bsd_card_id = fields.Many2one('bsd.residential.card', string="Thẻ cư dân", readonly=True)
    bsd_card_date = fields.Date(string='Ngày cấp thẻ', readonly=True)
    bsd_history_ids = fields.One2many('bsd.residential.history', 'bsd_residential_id', string="Lịch sử cư trú")
    bsd_unit_id = fields.Many2one('bsd.unit', compute='_compute_state', store=True, string="Unit")

    _sql_constraints = [
        ('bsd_cmnd_key', 'UNIQUE (bsd_cmnd)',  'CMND đã được đăng ký!')
    ]

    @api.depends('bsd_history_ids', 'bsd_history_ids.state')
    def _compute_state(self):
        for each in self:
            his = each.bsd_history_ids.filtered(lambda x: x.state == 'in') if each.bsd_history_ids else False
            if his:
                each.state = 'in'
                each.bsd_unit_id = his[0].bsd_unit_id.id
            else:
                each.state = 'out'
                each.bsd_unit_id = False

    @api.model
    def create(self, vals):
        _logger.debug("Val residential")
        _logger.debug(vals)
        if vals.get('bsd_code', '-') == '-':
            vals['bsd_code'] = self.env['ir.sequence'].next_by_code('bsd.residential') or '/'
        _logger.debug("create xong")
        return super(BsdResidential, self).create(vals)


class BsdResidentialRelationship(models.Model):
    _name = 'bsd.residential.relationship'

    name = fields.Char(string="Quan hệ chủ hộ", required=True)


class BsdResidentialHistory(models.Model):
    _name = 'bsd.residential.history'
    _rec_name = 'bsd_residential_id'
    _description = 'Bảng ghi nhận đăng ký tạm trú cư dân'

    bsd_residential_id = fields.Many2one('bsd.residential', string="Cư dân")
    bsd_unit_id = fields.Many2one('bsd.unit', string='Unit')
    bsd_date_move_on = fields.Date(string="Ngày chuyển vào")
    bsd_date_move_out = fields.Date(string="Ngày chuyển đi")
    bsd_relationship_id = fields.Many2one('bsd.residential.relationship', string="Quan hệ chủ hộ")
    state = fields.Selection([('in', 'Đang cư trú'), ('out', 'Đã chuyển đi')], default='in', string="Trạng thái")