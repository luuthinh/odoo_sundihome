# -*- coding:utf-8 -*-

from odoo import models, fields, api


class ProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    bsd_location_id = fields.Many2one('stock.location', string="Location", compute='_compute_location', store=True)
    bsd_room_type_id = fields.Many2one(related="product_id.product_tmpl_id.bsd_room_type_id", string="Room type", store=True)
    bsd_in_block = fields.Boolean(string="Thiết bị tòa nhà")
    bsd_area_id = fields.Many2one('bsd.area', string='Khu vực')

    @api.depends('quant_ids')
    def _compute_location(self):
        # _logger.debug("Compute location")
        for each in self:
            each.bsd_location_id = each.quant_ids.filtered(lambda x: x.quantity > 0).location_id.id
            # _logger.debug(each.bsd_location_id)
