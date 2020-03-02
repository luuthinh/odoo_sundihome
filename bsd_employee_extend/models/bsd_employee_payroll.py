# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)


class BsdEmployeePayroll(models.Model):
    _name = 'bsd.employee.payroll'

    name = fields.Char(string="Nội dung", required=True, readonly=True, states={'draft': [('readonly', False)]})
    bsd_year = fields.Selection([(str(num), str(num)) for num in range(2020, 2100)],
                                string='Năm',
                                default='2020', required=True, readonly=True, states={'draft': [('readonly', False)]})
    bsd_month = fields.Selection([(str(num), str(num)) for num in range(1, 12)],
                                 string='Tháng',
                                 default='1', required=True, readonly=True, states={'draft': [('readonly', False)]})
    bsd_user_id = fields.Many2one('hr.employee', string="Người phê duyệt", readonly=True, states={'draft': [('readonly', False)]})
    bsd_user_date = fields.Date(string="Ngày phê duyệt", readonly=True, states={'draft': [('readonly', False)]})
    bsd_pay_date = fields.Date(string="Ngày thanh toán", readonly=True, states={'draft': [('readonly', False)]})
    bsd_pay_total = fields.Monetary(string="Tổng số tiền", readonly=True, states={'draft': [('readonly', False)]})
    bsd_payment_id = fields.Many2one('account.payment', string="Chứng từ thanh toán", readonly=True, states={'draft': [('readonly', False)]})
    bsd_payment_date = fields.Date(string="Ngày chứng từ", readonly=True, states={'draft': [('readonly', False)]})

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Currency", readonly=True)

    state = fields.Selection([('draft', 'Nháp'),
                              ('payment', 'Đã thanh toán'),
                              ('cancel', 'Hủy')], string="Trạng thái", default='draft')

    bsd_item_ids = fields.One2many('bsd.employee.payroll.item', 'bsd_employee_payroll_id', string="Bảng lương nhân viên",
                                   readony=True, states={'draft': [('readonly', False)]})

    def action_payment(self):
        pay = {
            'type': 'ir.actions.act_window',
            'name': _('Payment'),
            'res_model': 'account.payment',
            'view_mode': 'form',
            'target': 'new',
            'context': {"default_amount": self.bsd_pay_total,
                        "default_bsd_employee_payroll_id": self.id,
                        'default_payment_type': 'outbound',
                        'default_partner_type': 'customer',
                        'default_communication': 'Thanh toán tiền lương',
                        'default_payment_method_id': self.env.ref('account.account_payment_method_manual_out').id,
                        'journal_id': 7}
        }
        _logger.debug(pay)
        return pay

    def action_cancel(self):
        self.write({
            'state': 'cancel',
        })


class BsdEmployeePayrollItem(models.Model):
    _name = 'bsd.employee.payroll.item'
    _rec_name = 'bsd_employee_id'

    bsd_employee_id = fields.Many2one('hr.employee', string="Nhân viên")
    bsd_barcode = fields.Char(string="Mã nhân viên", related='bsd_employee_id.barcode')
    bsd_department_id = fields.Many2one(related='bsd_employee_id.department_id', string="Phòng ban")
    bsd_job_id = fields.Many2one(related='bsd_employee_id.job_id', string="Chức vụ")
    bsd_salary = fields.Monetary(string='Lương')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Currency", readonly=True)
    bsd_year = fields.Selection([(str(num), str(num)) for num in range(2020, 2100)],
                                string='Năm',
                                default='2020', required=True)
    bsd_month = fields.Selection([(str(num), str(num)) for num in range(1, 13)],
                                 string='Tháng',
                                 default='1', required=True)
    bsd_employee_payroll_id = fields.Many2one('bsd.employee.payroll', string='Bảng lương tháng')
    bsd_user_id = fields.Many2one('hr.employee', string="Người phê duyệt",
                                  related='bsd_employee_payroll_id.bsd_user_id',
                                  store=True)
    bsd_user_date = fields.Date(string="Ngày phê duyệt", related='bsd_employee_payroll_id.bsd_user_date',
                                store=True)
    bsd_pay_date = fields.Date(string="Ngày thanh toán", related='bsd_employee_payroll_id.bsd_pay_date',
                               store=True)
