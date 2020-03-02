# -*- coding:utf-8 -*-

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    bsd_room_type_id = fields.Many2one('bsd.room.type', string="Loại phòng")
    bsd_type = fields.Selection([('residential_service', 'Dịch vụ cư dân'),
                                 ('parking_service', 'Dịch vụ giữ xe'),
                                 ('fee', 'Phí'),
                                 ('block_fee', 'Chi phí tòa nhà'),
                                 ('furniture', 'Nội thất')], string='Phân loại')