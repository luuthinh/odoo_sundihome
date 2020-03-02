# -*- coding:utf-8 -*-

from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    bsd_owner_ids = fields.One2many('bsd.unit', 'bsd_owner_id', string="Căn hộ sở hữu", readonly=True)
    bsd_tenant_ids = fields.One2many('bsd.unit', 'bsd_tenant_id', string="Căn hộ thuê", readonly=True)
    bsd_master_ids = fields.One2many('bsd.unit', 'bsd_responsible_id', string="Chủ hộ", readonly=True)
