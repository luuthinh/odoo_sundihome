# -*- coding:utf-8 -*-

from odoo import models, fields, api


class BsdContractSale(models.Model):
    _name = 'bsd.contract.sale'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Hợp đồng")

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Currency", readonly=True)

    bsd_landlord_id = fields.Many2one('res.partner', string="Chủ đầu tư")
    bsd_person_landlord_id = fields.Many2one('res.partner', string="Người Đại Diện")
    bsd_contract_type = fields.Selection([('1', 'Hợp đồng bán')], string="Loại Hợp Đồng", default='1')
    bsd_person_buy_id = fields.Many2one('res.partner', string="Người Mua")
    bsd_multi_unit = fields.Boolean(string="Nhiều căn hộ")
    bsd_block_id = fields.Many2one('bsd.real.estate.block', string="Block")
    bsd_unit_id = fields.Many2one('account.asset', string="Căn hộ")
    bsd_unit_price = fields.Monetary(string="Giá bán")
    bsd_vat = fields.Monetary(string="VAT")
    bsd_maintenance_cost = fields.Monetary(string="Phí bảo trì")
    bsd_total_price = fields.Monetary(string="Tổng giá trị hợp đồng", compute='_compute_total_price', store=True)
    bsd_management_fee = fields.Monetary(string="Phí quản lý")
    bsd_start_date = fields.Date(string="Hiệu lực hợp động")
    bsd_due_date = fields.Date(string="Ngày bàn giao")
    bsd_payment_type = fields.Selection([('bank', 'Bank'),
                                         ('cash', 'Cash')], string="Hình thức thanh toán", default='bank')
    bsd_payment_term_id = fields.Many2one('account.payment.term', string="Kì thanh toán")
    bsd_pay_rec_id = fields.Many2one('account.payment', string="Đặt cọc", readonly=True)
    bsd_contract_attachment = fields.Binary(string="Hợp đồng")

    # bảo hành
    bsd_warranty_int = fields.Integer(string="Bảo hành(năm)")
    bsd_warranty_from_date = fields.Date(string="Từ ngày")
    bsd_warranty_to_date = fields.Date(string="Đến ngày")

    bsd_have_commission = fields.Boolean("Hoa hồng")
    bsd_employee_id = fields.Many2one("hr.employee", string="Nhân viên")
    bsd_commission_type = fields.Selection([('static', 'Phí hoa hồng cố định'), ('percent', 'Hoa hồng theo (%) hợp đồng')], string="Cách tính hoa hồng")
    bsd_commission_percent = fields.Float(string="% hoa hồng")
    bsd_commission_total = fields.Monetary(string="Tổng tiền hoa hồng")

    bsd_unit_ids = fields.One2many('bsd.contract.sale.unit', 'bsd_sale_unit_id', string="Units")

    @api.onchange('bsd_multi_unit', 'bsd_unit_id', 'bsd_unit_ids')
    def _onchange_price(self):
        if not self.bsd_multi_unit:
            if self.bsd_unit_id:
                self.bsd_unit_price = self.bsd_unit_id.bsd_property_price
                self.bsd_vat = self.bsd_unit_id.bsd_vat
                self.bsd_maintenance_cost = self.bsd_unit_id.bsd_maintenance_cost

    @api.onchange('bsd_unit_price', 'bsd_vat', 'bsd_maintenance_cost', 'bsd_unit_ids')
    def _compute_total_price(self):
        for each in self:
            if not each.bsd_multi_unit:
                each.bsd_total_price = each.bsd_unit_price + each.bsd_vat + each.bsd_maintenance_cost
            else:
                each.bsd_total_price = sum(each.bsd_unit_ids.mapped('bsd_unit_price')) + \
                                       sum(each.bsd_unit_ids.mapped('bsd_vat')) + \
                                       sum(each.bsd_unit_ids.mapped('bsd_maintenance_cost'))


class BsdContractSaleUnit(models.Model):
    _name = 'bsd.contract.sale.unit'

    name = fields.Many2one('account.asset', string="Unit")
    bsd_vat = fields.Monetary(related='name.bsd_vat', string='VAT')
    bsd_unit_price = fields.Monetary(related='name.bsd_property_price', string="Price")
    bsd_maintenance_cost = fields.Monetary(related='name.bsd_maintenance_cost', string="Maintenance Cost")
    bsd_block_id = fields.Many2one('bsd.real.estate.block', string="Block")
    bsd_sale_unit_id = fields.Many2one('bsd.contract.sale')
    currency_id = fields.Many2one("res.currency", string="Currency", readonly=True, required=True,
                                  default=lambda self: self.env.company.currency_id)

    @api.onchange('name')
    def _onchange_unit(self):
        self.bsd_unit_price = self.name.bsd_property_price

    @api.onchange('bsd_block_id')
    def _onchange_block(self):
        res = {}
        res.update({
            'domain': {'name': [('bsd_block_id', '=', self.bsd_block_id.id)]}
        })
        return res
