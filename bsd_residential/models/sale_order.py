# -*- coding:utf-8 -*-

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    bsd_request_service_id = fields.Many2one('bsd.residential.service', string="Request", readonly=True)
    bsd_temp_address = fields.Many2one(related='partner_id.bsd_temp_address')

