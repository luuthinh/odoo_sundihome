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

    bsd_display_name = fields.Char(compute='_get_display_name', string="Display Name")

    def _get_display_name(self):
        for each in self:
            each.bsd_display_name = each.name + ' ' + each.bsd_rent_type


class BsdContractRental(models.Model):
    _inherit = 'account.analytic.account'

    bsd_rent_entry_chck = fields.Boolean(default=False)
    bsd_tenant_id = fields.Many2one('res.partner', string="Tenant", domain=[('bsd_is_master', '=', True)])
    bsd_unit_id = fields.Many2one('account.asset', string="Unit")

    bsd_multi_unit = fields.Boolean(string="Multi Unit", default=False)
    bsd_is_unit = fields.Boolean(string="Is Unit")
    bsd_tenancy_cancelled = fields.Boolean(string="Tenancy Cancelled")
    bsd_rent = fields.Monetary(string="Tenancy Rent")
    bsd_rent_date = fields.Date(string="Rent Date", default=fields.Date.today())

    state = fields.Selection([('template', 'Template'),
                              ('draft', 'New'),
                              ('waiting', 'Waiting to approve'),
                              ('open', 'In Progress'),
                              ('pending', 'To Renew'),
                              ('close', 'Closed'),
                              ('cancelled', 'Cancelled')], default='draft')
    bsd_deposit = fields.Monetary(string="Deposit")
    bsd_amount_return = fields.Monetary(string="Deposit Returned")
    bsd_deposit_received = fields.Boolean(string="Deposit Received?", readonly=True)
    bsd_deposit_return = fields.Boolean(string="Deposit Return?", readonly=True)
    bsd_contact_id = fields.Many2one('res.partner', string="Contact")
    bsd_pay_rec_id = fields.Many2one('account.payment', string="Payment receipt", readonly=True)
    bsd_pay_ret_id = fields.Many2one('account.payment', string="Payment return", readonly=True)

    bsd_start_date = fields.Date(string="Start Date", default=fields.Date.today())
    bsd_expiration_date = fields.Date(string="Expiration Date")
    bsd_invoice_date = fields.Selection([(str(num), 'ngày ' + str(num)) for num in range(1, 28)],
                                        string="Date Invoice",
                                        required=True)
    bsd_rent_type_id = fields.Many2one('bsd.rent.type', string="Rent Type", required=True)
    bsd_total_rent = fields.Monetary(string="Total Rent", compute='_get_total_rent')
    bsd_contract_attachment = fields.Binary(string="Tenancy Contract")
    bsd_rent_schedule_ids = fields.One2many('bsd.contract.tenancy.schedule', 'bsd_tenancy_id', string="Rent Schedule")
    bsd_account_move_line_ids = fields.One2many('account.move.line', 'analytic_account_id', string="History")
    bsd_penalty = fields.Float(string="Penalty")
    bsd_penalty_day = fields.Integer(string="Penalty count after days")

    bsd_contract_type = fields.Selection([('1', 'Thuê căn hộ'),
                                          ('2', 'Thuê TTTM'),
                                          ('3', 'Thuê Văn Phòng'),
                                          ('4', 'Thuê lại(dành cho chủ sở hữu'),
                                          ('5', 'Thuê lại(dành cho khách hàng')], default="1", string="Contract Type")
    bsd_unit_ids = fields.One2many('bsd.contract.tenancy.rent', 'bsd_tenancy_id', string="Units")

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

    @api.model
    def create(self, vals_list):
        _logger.debug("Create")
        _logger.debug(vals_list)
        if vals_list['bsd_multi_unit']:
            if 'bsd_unit_ids' not in vals_list:
                raise UserError("Kiểm tra lại bảng units")
        return super(BsdContractRental, self).create(vals_list)

    @api.onchange('bsd_multi_unit', 'bsd_unit_ids', 'bsd_unit_id')
    def _onchange_unit_ids(self):
        _logger.debug("onchange  multi unit")
        if self.bsd_multi_unit:
            self.bsd_unit_id = False
            for each in self:
                each.bsd_rent = sum(each.bsd_unit_ids.mapped('bsd_property_rent_price'))
                _logger.debug(each.bsd_rent)
        else:
            for each in self:
                each.bsd_rent = each.bsd_unit_id.bsd_property_rent_price

    def button_send(self):
        self.write({
            'state': 'waiting',
        })

    def button_start(self):
        self.write({
            'state': 'open',
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
        action = self.env.ref('bsd_real_estate.bsd_tenancy_renew_action').read()[0]
        _logger.debug("debug")
        action.update({'context': "{'action_id':%s}" % self.id})
        _logger.debug(action)
        self.bsd_rent_entry_chck = False
        return action

    def button_close(self):
        self.write({
            'state': 'close'
        })

    def button_cancel_tenancy(self):
        self.write({
            'state': 'cancelled',
            'bsd_tenancy_cancelled': True
        })

    @api.model
    def create(self, vals):
        if 'code' not in vals:
            vals['code'] = self.env['ir.sequence'].next_by_code('account.analytic.account') or '/'
        return super(BsdContractRental, self).create(vals)


class BsdContractTenancyRent(models.Model):
    _name = 'bsd.contract.tenancy.rent'

    name = fields.Many2one('account.asset', string="Unit")
    bsd_tenancy_id = fields.Many2one('account.analytic.account')
    bsd_ground_rent = fields.Monetary(string="Ground Rent")
    currency_id = fields.Many2one("res.currency", string="Currency", readonly=True, required=True,
                                  default=lambda self: self.env.company.currency_id)

    @api.onchange('name')
    def _onchange_unit(self):
        self.bsd_ground_rent = self.name.bsd_ground_rent


class BsdContractTenancySchedule(models.Model):
    _name = 'bsd.contract.tenancy.schedule'
    _rec_name = 'bsd_tenant_id'
    _order = 'bsd_start_date asc'

    bsd_cheque_detail = fields.Char(string="Cheque Detail", size=30)
    bsd_start_date = fields.Date(string="Date")
    bsd_tenancy_id = fields.Many2one('account.analytic.account', string="Tenancy")
    bsd_tenant_id = fields.Many2one('res.partner', string="Tenant")
    currency_id = fields.Many2one("res.currency", string="Currency", readonly=True, required=True,
                                  default=lambda self: self.env.company.currency_id)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)
    bsd_amount = fields.Monetary(string="Amount")
    bsd_penalty_amount = fields.Float(string="Penalty")
    bsd_pen_amt = fields.Float(string="Pending Amount")
    bsd_is_readonly = fields.Boolean(string="Readonly")
    bsd_inv = fields.Boolean(string="Invoiced?")
    bsd_move_check = fields.Boolean(string="Posted", compute='_compute_invoice')
    bsd_paid = fields.Boolean(string="Paid", compute='_compute_invoice')
    bsd_invc_id = fields.Many2one('account.move', string="Invoice")
    bsd_note = fields.Text(string="Note")

    @api.depends('bsd_invc_id')
    def _compute_invoice(self):
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
                'analytic_account_id': self.bsd_tenancy_id.id or False,
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
