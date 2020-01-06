# -*- coding:utf-8 -*-

from odoo.tools.profiler import profile

from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
import logging
_logger = logging.getLogger(__name__)


class AccountAsset(models.Model):
    _inherit = 'account.asset'

    bsd_service_ids = fields.One2many('bsd.unit.service', 'bsd_unit_id', string="Service")
    bsd_contract_sale_id = fields.Many2one('bsd.contract.sale', string="Hợp đồng mua bán")
    bsd_contract_rent_id = fields.Many2one('account.analytic.account', string="Hợp đồng thuê")

    bsd_invoice_ids = fields.One2many('account.move', 'bsd_unit_id', string="Invoices")

    def _bsd_get_price(self):
        list_product = []
        if self.bsd_property_for == 'sale' and self.bsd_owner_id and self.bsd_contract_sale_id:
            price_list = self.bsd_contract_sale_id.bsd_pricelist_id

        if (
                self.bsd_property_for == 'rent' or self.bsd_property_for == 'lease') and self.bsd_tenant_id and self.bsd_contract_rent_id:
            price_list = self.bsd_contract_rent_id.bsd_pricelist_id

        for ser in self.bsd_service_ids:
            if price_list and price_list.check_rule_get_item([(ser.bsd_product_id, 1, False)]):
                _logger.debug("Khách hàng có bảng giá")
                list_product.append(price_list.bsd_get_product_price_rule(ser.bsd_product_id, 1, False))
                continue
            else:
                product_pricelist = self.env['product.pricelist'].search(
                    [('bsd_project_id', '=', self.bsd_project_id.id),
                     ('bsd_type', '=', self.bsd_type),
                     ('bsd_property_for', '=', self.bsd_property_for),
                     ('bsd_from_date', '<', fields.Date.today()),
                     ('bsd_to_date', '>=', fields.Date.today())])
                price_list_block = product_pricelist.filtered(
                    lambda p: p.bsd_block_id.id == self.bsd_block_id.id)
                if price_list_block and price_list_block[0].check_rule_get_item([(ser.bsd_product_id, 1, False)]):
                    list_product.append(price_list_block[0].bsd_get_product_price_rule(ser.bsd_product_id, 1, False))
                    continue
                # price_list_area = product_pricelist.filtered(
                #     lambda p: not p.bsd_block_id and p.bsd_area_id.id == self.bsd_area_id.id)
                # if price_list_area and price_list_area.check_rule_get_item([(ser.bsd_product_id, 1, False)]):
                #     list_product.append(price_list_area.bsd_get_product_price_rule(ser.bsd_product_id, 1, False))
                #     continue
                price_list_project = product_pricelist.filtered(
                    lambda p: not p.bsd_block_id and p.bsd_project_id.id == self.bsd_project_id.id)
                if price_list_project and price_list_project[0].check_rule_get_item([(ser.bsd_product_id, 1, False)]):
                    list_product.append(price_list_project[0].bsd_get_product_price_rule(ser.bsd_product_id, 1, False))
        return list_product

    @profile
    def create_invoice(self):
        list_product_price = self._bsd_get_price()
        _logger.debug('bảng giá')
        _logger.debug(list_product_price)
        lines = []
        for line in list_product_price:
            for key, value in line.items():
                id_pricelist = self.env['product.pricelist.item'].browse(value[1]).pricelist_id.id
                temp = (0, 0, {'product_id': key,
                               'quantity': 1,
                               'bsd_pricelist_id': id_pricelist,
                               'price_unit': value[0],
                               'name': 'thu tiền dịch vụ',
                               })
                lines.append(temp)
        _logger.debug(lines)
        self.env['account.move'].create({
            'type': 'out_invoice',
            'partner_id': self.bsd_responsible_id.id,
            'invoice_date': fields.Date.today(),
            'bsd_unit_id': self.id,
            'currency_id': self.currency_id.id,
            'invoice_line_ids': lines,
        })


class BsdUnitService(models.Model):
    _name = 'bsd.unit.service'

    bsd_partner_id = fields.Many2one('res.partner', string="Chủ hộ")
    bsd_unit_id = fields.Many2one('account.asset', string="Unit")
    name = fields.Char(string="Description")
    bsd_note = fields.Char(string="Ghi chú")
    bsd_residential_id = fields.Many2one('bsd.residential', string="Cư dân")
    bsd_product_id = fields.Many2one('product.product', string="Dịch vụ")
    bsd_product_tmpl_id = fields.Many2one('product.template', domain=[('type', '=', 'service')], string="Template")
    bsd_registry_service_id = fields.Many2one('bsd.residential.service', string="Phiếu đăng ký")
    bsd_cancel_registry_service_id = fields.Many2one('bsd.residential.service', string="Phiếu hủy")
    bsd_start_date = fields.Date(string="Start date")
    bsd_end_date = fields.Date(string="End date")
    state = fields.Selection([('active', 'Hiệu lực'), ('deactivate', 'Hết hiệu lực')], string="State")

