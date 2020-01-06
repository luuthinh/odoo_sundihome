# -*- coding:utf-8 -*-

from odoo import models, fields


class AccountMove(models.Model):
    _inherit = 'account.move'

    bsd_unit_id = fields.Many2one('account.asset', string='Unit')


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    bsd_pricelist_id = fields.Many2one('product.pricelist', string="Price list")