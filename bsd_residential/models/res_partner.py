# -*- coding:utf-8 -*-

from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # bsd_type = fields.Many2many('bsd.partner.type', string='Type')
    bsd_birthday = fields.Date(string="Birthday")
    bsd_cmnd = fields.Char(string="CMND")
    bsd_is_master = fields.Boolean(string="Là chủ hộ", compute='_compute_master', store=True)
    bsd_owned_ids = fields.One2many('account.asset', 'bsd_owner_id', string="Căn hộ sở hữu", readonly=True)
    bsd_master_ids = fields.One2many('account.asset', 'bsd_responsible_id', string="Chủ hộ", readonly=True)
    bsd_temp_address = fields.Many2one('account.asset', string="Địa chỉ tạm trú", compute='_get_unit')

    def _get_unit(self):
        for each in self:
            residential = self.env['bsd.residential'].search([('name', '=', self.id), ('state', '=', 'in'), ('active', '=', True)], limit=1)
            each.bsd_temp_address = residential.bsd_unit_id.id

    @api.depends('bsd_master_ids')
    def _compute_master(self):
        for each in self:
            if each.bsd_master_ids:
                each.bsd_is_master = True
            else:
                each.bsd_is_master = False
        _logger.debug("tính lại master")

    _sql_constraints = [
        ('bsd_cmnd_unique',
         'UNIQUE(bsd_cmnd)',
         "Số CMND đã được đăng ký"),
    ]

