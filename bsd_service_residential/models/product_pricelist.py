# -*- coding:utf-8 -*-

from odoo import models, fields, api
from itertools import chain


class BsdContractSale(models.Model):
    _inherit = 'bsd.contract.sale'

    bsd_pricelist_id = fields.Many2one('product.pricelist', string="Bảng giá dịch vụ")


class ProductPriceList(models.Model):
    _inherit = "product.pricelist"

    def name_get(self):
        res = []
        for pricelist in self:
            res.append((pricelist.id, pricelist.complete_name))
        return res

    complete_name = fields.Char(string="Bảng giá", compute="_compute_complete_name", store=True)

    @api.depends(
                 'bsd_block_id',
                 'bsd_type',
                 'name')
    def _compute_complete_name(self):
        for each in self:
            if each.bsd_block_id:
                each.complete_name = '{}-{},{}'.format(
                                                                   each.bsd_block_id.bsd_code,
                                                                   each.bsd_type,
                                                                   each.name)
    bsd_block_id = fields.Many2one('bsd.block', string="Tòa nhà", required=True)
    bsd_type = fields.Selection([('res', 'Căn hộ'), ('off', 'Văn Phòng'), ('mall', 'TTTM')], string="Loại Unit",
                                default='res')

    def check_rule_get_item(self, products_qty_partner, date=False, uom_id=False):
        self.ensure_one()
        if not date:
            date = self._context.get('date') or fields.Date.today()
        date = fields.Date.to_date(date)
        if not uom_id and self._context.get('uom'):
            uom_id = self._context['uom']
        if uom_id:
            products = [item[0].with_context(uom=uom_id) for item in products_qty_partner]
            products_qty_partner = [(products[index], data_struct[1], data_struct[2]) for index, data_struct in enumerate(products_qty_partner)]
        else:
            products = [item[0] for item in products_qty_partner]
        if not products:
            return {}

        categ_ids = {}
        for p in products:
            categ = p.categ_id
            while categ:
                categ_ids[categ.id] = True
                categ = categ.parent_id
        categ_ids = list(categ_ids)

        is_product_template = products[0]._name == "product.template"
        if is_product_template:
            prod_tmpl_ids = [tmpl.id for tmpl in products]
            prod_ids = [p.id for p in list(chain.from_iterable([t.product_variant_ids for t in products]))]
        else:
            prod_ids = [product.id for product in products]
            prod_tmpl_ids = [product.product_tmpl_id.id for product in products]

        return self._compute_price_rule_get_items(products_qty_partner, date, uom_id, prod_tmpl_ids, prod_ids, categ_ids)

    def bsd_get_product_price_rule(self, product, quantity, partner, date=False, uom_id=False):

        self.ensure_one()
        return self._compute_price_rule([(product, quantity, partner)], date=date, uom_id=uom_id)


class ProductPriceListItem(models.Model):
    _inherit = 'product.pricelist.item'

    bsd_duration = fields.Integer(string="Số tháng thu 1 lần", default=1)
