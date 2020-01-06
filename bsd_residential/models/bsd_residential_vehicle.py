# -*- coding:utf-8 -*-

from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)


class BsdResidentialVehicle(models.Model):
    _name = 'bsd.residential.vehicle'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin', 'image.mixin']
    _description = 'Phương tiện'

    bsd_residential_id = fields.Many2one('bsd.residential', string="Cư Dân")
    name = fields.Char(string="Name", compute='_get_name')
    bsd_type = fields.Many2one('product.template.attribute.value', string="Loại xe", required=True)
    bsd_brand = fields.Char(string="Hiệu Xe", required=True)
    bsd_license = fields.Char(string="Biển kiểm soát", required=True)
    bsd_partner_id = fields.Many2one('res.partner', string="Chủ Hộ")
    bsd_unit_id = fields.Many2one('account.asset', string="Căn Hộ")
    bsd_note = fields.Text(string="Ghi chú")
    active = fields.Boolean(default=True)
    state = fields.Selection([('waiting', 'Chờ xác thục'), ('active', 'Đã xác thực')], default='waiting')
    bsd_date_accuracy = fields.Date(string="Ngày xác thực", readonly=True)
    bsd_service_id = fields.Many2one('bsd.residential.service', string="Service")
    bsd_product_tmpl_id = fields.Many2one('product.template', string="Product template")
    bsd_product_id = fields.Many2one('product.product', string="Product", compute='_get_product', )

    def _get_name(self):
        for each in self:
            each.name = ''
            if each.bsd_brand and each.bsd_license:
                each.name = each.bsd_brand + ' - ' + each.bsd_license

    @api.depends('bsd_product_tmpl_id', 'bsd_type')
    def _get_product(self):
        for each in self:
            _logger.debug("Kiếm ra product")
            each.bsd_product_id = False
            product = self.env['product.product'].search([('product_tmpl_id', '=', self.bsd_product_tmpl_id.id)])
            _logger.debug(product)
            for item in product:
                _logger.debug("attribute")
                _logger.debug(item.product_template_attribute_value_ids.ids)
                _logger.debug(each.bsd_type.id)
                if each.bsd_type:
                    if set(item.product_template_attribute_value_ids.ids) == set([each.bsd_type.id]):
                        each.bsd_product_id = item.id

    def action_confirm(self):
        self.write({
            'state': 'active',
            'bsd_date_accuracy': fields.Date.today()
        })