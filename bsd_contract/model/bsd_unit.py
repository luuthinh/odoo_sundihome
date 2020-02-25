# -*- coding:utf-8 -*-

from odoo import models, fields, api


class BsdUnit(models.Model):
    _inherit = 'bsd.unit'

    bsd_contract_sale_ids = fields.One2many('bsd.contract.sale', 'bsd_unit_id', string="Hợp đồng bán")
    bsd_contract_tenancy_ids = fields.One2many('bsd.contract.tenancy', 'bsd_unit_id', string="Hợp đồng thuê")
    bsd_tenant_id = fields.Many2one('res.partner', string="Người thuê", compute='_compute_tenant', store=True)

    @api.depends('bsd_contract_tenancy_ids.state', 'bsd_contract_tenancy_ids')
    def _compute_tenant(self):
        for each in self:
            if each.bsd_contract_tenancy_ids:
                tenancy = each.bsd_contract_tenancy_ids.filtered(lambda x: x.state == 'open')
                if tenancy:
                    each.bsd_tenant_id = tenancy[0].bsd_tenant_id.id
                else:
                    each.bsd_tenant_id = False
