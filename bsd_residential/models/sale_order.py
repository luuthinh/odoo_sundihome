# -*- coding:utf-8 -*-

from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    bsd_residential_id = fields.Many2one('bsd.residential', string="Cư dân")
    bsd_unit_id = fields.Many2one(related='bsd_residential_id.bsd_unit_id', store=True)

    @api.onchange('bsd_residential_id')
    def _onchange_residential(self):
        self.partner_id = self.bsd_residential_id.partner_id.id

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        super(SaleOrder, self).onchange_partner_id()
        if self.bsd_residential_id:
            price_list = self.env['product.pricelist'].search([('bsd_block_id', '=', self.bsd_unit_id.bsd_block_id.id),
                                                               ('bsd_type', '=', 'res')],
                                                              limit=1)
            _logger.debug(price_list)
            self.pricelist_id = price_list.id
            _logger.debug(self.pricelist_id)