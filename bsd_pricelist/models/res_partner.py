# -*- coding:utf-8 -*-

from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    bsd_contract_sale_ids = fields.One2many('bsd.contract.sale', 'bsd_person_buy_id', string="Hợp đồng mua")
    bsd_contract_rent_ids = fields.One2many('account.analytic.account', 'bsd_tenant_id', string="Hợp đồng thuê")
