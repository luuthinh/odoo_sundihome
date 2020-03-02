# -*- coding:utf-8 -*-

import datetime
import calendar

from odoo.tools.profiler import profile

from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
import logging
_logger = logging.getLogger(__name__)


class BsdUnit(models.Model):
    _inherit = 'bsd.unit'

    bsd_vehicle_ids = fields.One2many('bsd.residential.vehicle', 'bsd_unit_id', string="Giữ xe")
    bsd_count_vehicle = fields.Integer(string="Số phương tiên", compute='_compute_vehicle', store=True)
    bsd_invoice_ids = fields.One2many('account.move', 'bsd_unit_id', string="Hóa đơn")
    bsd_electric_ids = fields.One2many('bsd.residential.electric', 'bsd_unit_id', string="Chỉ số Điện")
    bsd_water_ids = fields.One2many('bsd.residential.water', 'bsd_unit_id', string="Chỉ số Nước")

    @api.depends('bsd_vehicle_ids', 'bsd_vehicle_ids.state')
    def _compute_vehicle(self):
        for each in self:
            vehicle = each.bsd_vehicle_ids.filtered(lambda x: x.state == 'card')
            each.bsd_count_vehicle = len(vehicle)

    def _bsd_get_price(self, invoice_date, month, year):
        list_product = []

        def _add_month(months, years, int_add):
            m = (months + int_add) % 12
            y = int(years + (months + int_add) / 12)
            return (m, y)

        product_pricelist = self.env['product.pricelist'].search(
            [('bsd_block_id', '=', self.bsd_block_id.id),
             ('bsd_type', '=', self.bsd_type)], limit=1)
        price_list_block = product_pricelist.filtered(
            lambda p: p.bsd_block_id.id == self.bsd_block_id.id)

        for veh in self.bsd_vehicle_ids.filtered(lambda x: x.state == 'card'):
            item_veh = price_list_block.check_rule_get_item([(veh.bsd_product_id, 1, False)], date=invoice_date)
            if item_veh:
                list_product.append(price_list_block.bsd_get_product_price_rule(veh.bsd_product_id, 1, False))

        # fees = self.bsd_block_id.bsd_fee_ids.filtered(lambda x: x.bsd_type == self.bsd_type)
        # product_fee = self.bsd_unit_fee_ids.mapped('bsd_product_id') if self.bsd_unit_fee_ids else []
        # _logger.debug(product_fee)
        # _logger.debug("product_fee")
        for fee in self.bsd_unit_fee_ids:
            item_fee = price_list_block.check_rule_get_item([(fee.bsd_product_id, 1, False)], date=invoice_date)
            if item_fee:
                if fee.bsd_year == year and fee.bsd_month == month:
                    price_fee = price_list_block.bsd_get_product_price_rule(fee.bsd_product_id, 1, False, date=invoice_date)
                    if fee.bsd_product_id.product_tmpl_id.uom_id.id == self.env.ref('bsd_block.product_uom_m2_month').id:
                        temp = {}
                        for key, value in price_fee.items():
                            temp.update({
                                    key: (value[0] * self.bsd_carpet_area, value[1])
                            })
                        list_product.append(temp)
                    else:
                        list_product.append(price_fee)

                    date = _add_month(int(fee.bsd_month), int(fee.bsd_year), item_fee.bsd_duration)
                    fee.write({
                        'bsd_month': str(date[0]),
                        'bsd_year': str(date[1]),
                    })
                elif int(fee.bsd_year) < int(year) or (int(fee.bsd_year) == int(year) and int(fee.bsd_month)< int(month)):
                    price_fee = price_list_block.bsd_get_product_price_rule(fee.bsd_product_id, 1, False, date=invoice_date)
                    if fee.bsd_product_id.product_tmpl_id.uom_id.id == self.env.ref('bsd_block.product_uom_m2_month').id:
                        temp = {}
                        for key, value in price_fee.items():
                            temp.update({
                                    key: (value[0] * self.bsd_carpet_area, value[1])
                            })
                        list_product.append(temp)
                    else:
                        list_product.append(price_fee)
                    date = _add_month(int(month), int(year), item_fee.bsd_duration)
                    fee.write({
                        'bsd_month': str(date[0]),
                        'bsd_year': str(date[1]),
                    })
                else:
                    pass
        return list_product

    def _get_price_electric(self, month=None, year=None):
        rec_electric = self.bsd_electric_ids.filtered(lambda x: x.bsd_year == year and x.bsd_month == month)
        if rec_electric:
            value_electric = (0, 0, {
                'product_id': rec_electric.bsd_product_id.id,
                'quantity': 1,
                'product_uom_id': rec_electric.bsd_product_id.uom_id.id,
                'price_unit': rec_electric.bsd_price,
            })
            return value_electric
        return False

    def _get_price_water(self, month=None, year=None):
        rec_water = self.bsd_water_ids.filtered(lambda x: x.bsd_year == year and x.bsd_month == month)
        if rec_water:
            value_water = (0, 0, {
                'product_id': rec_water.bsd_product_id.id,
                'quantity': 1,
                'product_uom_id': rec_water.bsd_product_id.uom_id.id,
                'price_unit': rec_water.bsd_price,
            })
            return value_water
        return False

    def _prepare_invoice_values(self, invoice_date=fields.Date.today(),
                                invoice_date_due=fields.Date.today(),
                                invoice_origin=None,
                                month=None,
                                year=None):
        list_product_price = self._bsd_get_price(invoice_date, month, year)
        lines = []
        for line in list_product_price:
            for key, value in line.items():
                id_uom = self.env['product.product'].browse(key).uom_id.id
                id_pricelist = self.env['product.pricelist.item'].browse(value[1])
                temp = (0, 0, {'product_id': key,
                               'quantity': id_pricelist.bsd_duration,
                               'product_uom_id': id_uom,
                               'bsd_pricelist_id': id_pricelist.pricelist_id.id,
                               'price_unit': value[0],
                               })
                lines.append(temp)
        electric = self._get_price_electric(month=month, year=year)
        if electric:
            lines.append(electric)
        water = self._get_price_water(month=month, year=year)
        if water:
            lines.append(water)
        _logger.debug(lines)
        if not invoice_origin:
            invoice_origin = 'Thu phí dịch vụ tháng ' + fields.Date.today().strftime("%m/%Y")
        value = {
            'type': 'out_invoice',
            'partner_id': self.bsd_responsible_id.partner_id.id,
            'invoice_date': invoice_date,
            'invoice_date_due': invoice_date_due,
            'bsd_unit_id': self.id,
            'currency_id': self.currency_id.id,
            'invoice_line_ids': lines,
            'invoice_origin': invoice_origin
        }
        return value

    @profile
    def create_invoice(self, invoice_date=fields.Date.today(),
                       invoice_date_due=fields.Date.today(),
                       invoice_origin=None,
                       month=None,
                       year=None):

        values = self._prepare_invoice_values(invoice_date=invoice_date,
                                              invoice_date_due=invoice_date_due, invoice_origin=invoice_origin,
                                              month=month, year=year)
        self.env['account.move'].create(values)