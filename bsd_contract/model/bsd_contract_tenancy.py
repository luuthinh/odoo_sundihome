# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import logging
import datetime

_logger = logging.getLogger(__name__)


class BsdRentType(models.Model):
    _name = 'bsd.rent.type'
    _description = 'Kiểu Thuê'
    _rec_name = 'bsd_display_name'
    _order = 'bsd_display_name'

    name = fields.Selection([('1', '1'),
                             ('2', '2'),
                             ('3', '3'),
                             ('4', '4'),
                             ('5', '5'),
                             ('6', '6'),
                             ('7', '7'),
                             ('8', '8'),
                             ('9', '9'),
                             ('10', '10'),
                             ('11', '11'),
                             ('12', '12')], string="Name", required=True)
    bsd_rent_type = fields.Selection([('monthly', 'Monthly'), ('yearly', 'Yearly')],
                                     string="Rent Type")

    bsd_display_name = fields.Char(compute='_get_display_name', string="Kiểu thuê")

    def _get_display_name(self):
        for each in self:
            each.bsd_display_name = each.name + ' ' + each.bsd_rent_type


class BsdContractTenancy(models.Model):
    _name = 'bsd.contract.tenancy'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Thông tin hợp đồng thuê'

    name = fields.Char(string="Hợp đồng")
    bsd_code = fields.Char(string="Mã hợp đồng")
    company_id = fields.Many2one('res.company', string='Công ty', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Tiền tệ", readonly=True)
    bsd_rent_entry_chck = fields.Boolean(default=False)
    bsd_tenant_id = fields.Many2one('res.partner', string="Người thuê")
    bsd_unit_id = fields.Many2one('bsd.unit', string="Unit")

    bsd_tenancy_cancelled = fields.Boolean(string="Hủy hợp đồng")
    bsd_rent = fields.Monetary(string="Tiền thuê/tháng")
    bsd_rent_date = fields.Date(string="Ngày thuê", default=fields.Date.today())

    state = fields.Selection([('template', 'Template'),
                              ('draft', 'Tạo mới'),
                              ('waiting', 'Chờ xét duyệt'),
                              ('open', 'Đang thực hiện'),
                              ('pending', 'Gia hạn'),
                              ('close', 'Đóng hợp đồng'),
                              ('cancelled', 'Hủy hợp đồng')], default='draft', string='Trạng thái')
    bsd_deposit = fields.Monetary(string="Tiền đặt cọc")
    bsd_amount_return = fields.Monetary(string="Tiền trả cọc")
    bsd_deposit_received = fields.Boolean(string="Đã nhận cọc", readonly=True)
    bsd_deposit_return = fields.Boolean(string="Đã trả cọc", readonly=True)
    bsd_contact_id = fields.Many2one('res.partner', string="Liên hệ")
    bsd_pay_rec_id = fields.Many2one('account.payment', string="Phiếu thu cọc", readonly=True)
    bsd_pay_ret_id = fields.Many2one('account.payment', string="Phiếu trả cọc", readonly=True)

    bsd_start_date = fields.Date(string="Ngày bắt đầu", default=fields.Date.today())
    bsd_expiration_date = fields.Date(string="Ngày kết thúc")
    bsd_invoice_date = fields.Selection([(str(num), 'ngày ' + str(num)) for num in range(1, 28)],
                                        string="Ngày xuất hóa đơn",
                                        required=True)
    bsd_rent_type_id = fields.Many2one('bsd.rent.type', string="Chu kỳ tính tiền", required=True)
    bsd_total_rent = fields.Monetary(string="Tổng tiền thuê", compute='_get_total_rent')
    bsd_contract_attachment = fields.Binary(string="Bản hợp đồng đính kèm")
    bsd_rent_schedule_ids = fields.One2many('bsd.contract.tenancy.schedule', 'bsd_tenancy_id', string="Lịch thu tiền")
    bsd_penalty = fields.Float(string="Phạt ")
    bsd_penalty_day = fields.Integer(string="Số ngày bắt đầu phạt")

    bsd_contract_type = fields.Selection([('res', 'Thuê căn hộ'),
                                          ('off', 'Thuê TTTM'),
                                          ('mall', 'Thuê Văn Phòng')], related='bsd_unit_id.bsd_type', string="Loại hợp đồng thuê", store=True)

    @api.constrains('bsd_expiration_date')
    def _constrains_date(self):
        if self.bsd_expiration_date <= self.bsd_start_date:
            raise ValidationError('Ngày kết thúc phải sau ngày bắt đầu')

    @api.constrains('bsd_rent')
    def _constrains_rent(self):
        if self.bsd_rent <= 0:
            raise ValidationError('Tiền thuê nhà phải lớn hơn 0')

    @api.depends('bsd_rent_schedule_ids')
    def _get_total_rent(self):
        for each in self:
            each.bsd_total_rent = sum(each.bsd_rent_schedule_ids.mapped('bsd_amount'))

    # @api.model
    # def create(self, vals_list):
    #     _logger.debug("Create")
    #     _logger.debug(vals_list)
    #     return super(BsdContractTenancy, self).create(vals_list)

    @api.onchange('bsd_unit_id')
    def _onchange_unit_ids(self):
        pass

    def button_send(self):
        self.write({
            'state': 'waiting',
        })

    def button_start(self):
        self.write({
            'state': 'open',
        })
        self.bsd_unit_id.write({
            'state': 'rent',
        })

    def create_rent_schedule(self):
        def add_months(source_date, months, day):
            month = source_date.month - 1 + months
            year = source_date.year + month // 12
            month = month % 12 + 1
            return datetime.date(year, month, day)

        def add_year(source_date, years, day):
            year = source_date.year + years
            month = source_date.month
            return datetime.date(year, month, day)

        self.env['bsd.contract.tenancy.schedule'].create({
            'bsd_start_date': self.bsd_start_date,
            'bsd_tenancy_id': self.id,
            'bsd_tenant_id': self.bsd_tenant_id.id,
            'bsd_amount': self.bsd_rent * int(self.bsd_rent_type_id.name)
        })

        if self.bsd_rent_type_id.bsd_rent_type == 'monthly':
            date = add_months(self.bsd_start_date, int(self.bsd_rent_type_id.name), int(self.bsd_invoice_date))
            while date < self.bsd_expiration_date:
                if self.bsd_expiration_date.year - date.year == 1:
                    if self.bsd_expiration_date.month - date.month + 13 >= int(self.bsd_rent_type_id.name):
                        amount = self.bsd_rent * int(self.bsd_rent_type_id.name)
                    else:
                        amount = self.bsd_rent * int(self.bsd_expiration_date.month - date.month + 13)
                elif self.bsd_expiration_date.year == date.year:
                    if self.bsd_expiration_date.month - date.month + 1 >= int(self.bsd_rent_type_id.name):
                        amount = self.bsd_rent * int(self.bsd_rent_type_id.name)
                    else:
                        amount = self.bsd_rent * int(self.bsd_expiration_date.month - date.month + 1)
                else:
                    amount = self.bsd_rent * int(self.bsd_rent_type_id.name)
                self.env['bsd.contract.tenancy.schedule'].create({
                        'bsd_start_date': date,
                        'bsd_tenancy_id': self.id,
                        'bsd_tenant_id': self.bsd_tenant_id.id,
                        'bsd_amount': amount
                        })
                date = add_months(date, int(self.bsd_rent_type_id.name), int(self.bsd_invoice_date))

        if self.bsd_rent_type_id.bsd_rent_type == 'yearly':
            date = add_months(self.bsd_start_date, int(self.bsd_rent_type_id.name), int(self.bsd_invoice_date))
            while date < self.bsd_expiration_date:
                self.env['bsd.contract.tenancy.schedule'].create({
                    'bsd_start_date': date,
                    'bsd_tenancy_id': self.id,
                    'bsd_tenant_id': self.bsd_tenant_id.id,
                    'bsd_amount': amount,
                })
                date = add_year(date, int(self.bsd_rent_type_id.name), int(self.bsd_invoice_date))
                _logger.debug(date)
        self.bsd_rent_entry_chck = True
        return True

    def button_receive(self):
        if self.bsd_deposit == 0:
            raise UserError("Nhập tiền cọc")
        pay_id = self.env['account.payment'].create({
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'partner_id': self.bsd_tenant_id.id,
            'amount': self.bsd_deposit,
            'communication': 'Deposit Received',
            'bsd_tenancy_id': self.id,
            'payment_method_id': self.env.ref('account.account_payment_method_manual_in').id,
            'journal_id': 7,
        })
        self.bsd_pay_rec_id = pay_id.id,
        return {
            'type': 'ir.actions.act_window',
            'name': _('Payment'),
            'res_model': 'account.payment',
            'res_id': pay_id.id,
            'view_mode': 'form',
        }

    def button_return(self):
        pay_id = self.env['account.payment'].create({
            'payment_type': 'outbound',
            'partner_type': 'customer',
            'partner_id': self.bsd_tenant_id.id,
            'amount': self.bsd_deposit,
            'communication': 'Deposit Return',
            'bsd_tenancy_id': self.id,
            'payment_method_id': self.env.ref('account.account_payment_method_manual_out').id,
            'journal_id': 7,
        })
        self.bsd_pay_ret_id = pay_id.id,
        return {
            'type': 'ir.actions.act_window',
            'name': _('Payment'),
            'res_model': 'account.payment',
            'res_id': pay_id.id,
            'view_mode': 'form',
        }

    def button_set_to_renew(self):
        check_paid = self.bsd_rent_schedule_ids.mapped('bsd_paid')
        _logger.debug(check_paid)
        if not all(check_paid):
            raise UserError("Kiểm tra lại lịch thu tiền")
        action = self.env.ref('bsd_contract.bsd_tenancy_renew_action').read()[0]
        _logger.debug("debug")
        action.update({'context': "{'action_id':%s}" % self.id})
        _logger.debug(action)
        self.bsd_rent_entry_chck = False
        return action

    def button_close(self):
        self.write({
            'state': 'close'
        })
        self.bsd_unit_id.write({
            'state': 'ready',
            'bsd_date_invoice': False,
        })

    def button_cancel_tenancy(self):
        self.write({
            'state': 'cancelled',
            'bsd_tenancy_cancelled': True
        })
        self.bsd_unit_id.write({
            'state': 'ready',
            'bsd_date_invoice': False,
        })


class BsdContractTenancySchedule(models.Model):
    _name = 'bsd.contract.tenancy.schedule'
    _rec_name = 'bsd_tenant_id'
    _order = 'bsd_start_date asc'

    bsd_cheque_detail = fields.Char(string="Mô tả", size=30)
    bsd_start_date = fields.Date(string="Ngày")
    bsd_tenancy_id = fields.Many2one('bsd.contract.tenancy', string="Hợp đồng")
    bsd_tenant_id = fields.Many2one('res.partner', string="Người thuê")
    currency_id = fields.Many2one("res.currency", string="Tiền tệ", readonly=True, required=True,
                                  default=lambda self: self.env.company.currency_id)
    company_id = fields.Many2one('res.company', 'Công ty', required=True, index=True, default=lambda self: self.env.company)
    bsd_amount = fields.Monetary(string="Số tiền")
    bsd_penalty_amount = fields.Float(string="tiền phạt")
    bsd_is_readonly = fields.Boolean(string="Chỉ đọc")
    bsd_inv = fields.Boolean(string="Đã tạo hóa đơn")
    bsd_move_check = fields.Boolean(string="Đã kiểm tra", compute='_compute_invoice', store=True)
    bsd_paid = fields.Boolean(string="Đã thanh toán", compute='_compute_invoice', store=True)
    bsd_invc_id = fields.Many2one('account.move', string="Hóa đơn")
    bsd_note = fields.Text(string="Ghi chú")

    @api.depends('bsd_invc_id.state', 'bsd_invc_id.invoice_payment_state')
    def _compute_invoice(self):
        _logger.debug("cập nhật tình trạng thanh toàn")
        for each in self:
            each.bsd_move_check = True if each.bsd_invc_id.state == 'posted' else False
            each.bsd_paid = True if each.bsd_invc_id.invoice_payment_state == 'paid' else False

    def create_invoice(self):
        invoice_vals = {
            'type': 'out_invoice',
            'invoice_origin': self.bsd_cheque_detail,
            'narration': self.bsd_note,
            'partner_id': self.bsd_tenant_id.id,
            'currency_id': self.currency_id.id,
            'invoice_line_ids': [(0, 0, {
                'name': 'Tenancy(rent) Cost',
                'price_unit': self.bsd_amount,
                'quantity': 1.0,
            })],
        }
        invoice = self.env['account.move'].create(invoice_vals)
        self.write({
            'bsd_inv': True,
            'bsd_invc_id': invoice.id,
        })

    def open_invoice(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Invoices'),
            'res_model': 'account.move',
            'res_id': self.bsd_invc_id.id,
            'view_mode': 'form',
        }
