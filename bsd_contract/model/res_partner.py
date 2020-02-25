# -*- coding:utf-8 -*-

from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    bsd_contract_sale_ids = fields.One2many('bsd.contract.sale', 'bsd_person_buy_id',
                                            string="Hợp đồng bán", readonly=True)
    bsd_contract_tenancy_ids = fields.One2many('bsd.contract.tenancy',
                                               'bsd_tenant_id', string="Hợp đồng thuê", readonly=True)
