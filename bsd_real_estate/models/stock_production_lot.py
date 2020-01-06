# -*- coding:utf-8 -*-

from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)


class ProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    bsd_location_id = fields.Many2one('stock.location', string="Location", compute='_compute_location', store=True)
    bsd_categ_id = fields.Many2one(related="product_id.product_tmpl_id.categ_id", string="Category", store=True)

    @api.depends('quant_ids')
    def _compute_location(self):
        _logger.debug("Compute location")
        for each in self:
            each.bsd_location_id = each.quant_ids.filtered(lambda x: x.quantity > 0).location_id.id
            _logger.debug(each.bsd_location_id)