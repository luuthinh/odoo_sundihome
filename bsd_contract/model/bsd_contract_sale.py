# -*- coding:utf-8 -*-

from odoo import models, fields, api


class BsdContractSale(models.Model):
    _name = 'bsd.contract.sale'
    _description = "Hợp đồng mua bán"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Hợp đồng")

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)

    bsd_landlord_id = fields.Many2one('res.partner', string="Chủ đầu tư")
    bsd_person_landlord_id = fields.Many2one('res.partner', string="Người đại diện")
    bsd_contract_type = fields.Selection([('1', 'Hợp đồng bán')], string="Loại Hợp Đồng", default='1')
    bsd_person_buy_id = fields.Many2one('res.partner', string="Người mua")
    bsd_unit_id = fields.Many2one('bsd.unit', string="Căn hộ", domain=[('state', '=', 'ready')])
    bsd_unit_price = fields.Monetary(string="Giá bán")
    bsd_vat = fields.Monetary(string="Thuế")
    bsd_maintenance_cost = fields.Monetary(string="Phí bảo trì")
    bsd_total_price = fields.Monetary(string="Tổng giá trị hợp đồng", compute='_compute_total_price', store=True)
    bsd_management_fee = fields.Monetary(string="Phí quản lý")
    bsd_start_date = fields.Date(string="Ngày hiệu lực")
    bsd_due_date = fields.Date(string="Ngày bàn giao")
    bsd_payment_type = fields.Selection([('bank', 'Bank'),
                                         ('cash', 'Cash')], string="Hình thức thanh toán", default='bank')
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

    # @api.onchange('bsd_unit_id')
    # def _onchange_price(self):
    #     if self.bsd_unit_id:
    #         self.bsd_unit_price = self.bsd_unit_id.bsd_property_price
    #         self.bsd_vat = self.bsd_unit_id.bsd_vat
    #         self.bsd_maintenance_cost = self.bsd_unit_id.bsd_maintenance_cost

    @api.depends('bsd_unit_price', 'bsd_vat', 'bsd_maintenance_cost')
    def _compute_total_price(self):
        for each in self:
            each.bsd_total_price = each.bsd_unit_price + each.bsd_vat + each.bsd_maintenance_cost

    @api.model
    def create(self,vals_list):
        res = super(BsdContractSale, self).create(vals_list)
        res.bsd_unit_id.write({
            'state': 'sale',
            'bsd_owner_id': res.bsd_person_buy_id.id
        })
        return res
