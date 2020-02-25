# -*- coding:utf-8 -*-

from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    bsd_employee_payroll_id = fields.Many2one('bsd.employee.payroll', string='Bảng lương')

    @api.model
    def create(self,vals):
        _logger.debug("thanh toán lương")
        _logger.debug(vals)
        pay = super(AccountPayment, self).create(vals)
        self.env['bsd.employee.payroll'].search([('id', '=', pay.bsd_employee_payroll_id.id)]).write({
            'bsd_payment_id': pay.id,
            'bsd_payment_date': pay.payment_date,
            'state': 'payment'
        })
        _logger.debug(pay)
        return pay

    @api.model
    def default_get(self, default_fields):
        rec = super(AccountPayment, self).default_get(default_fields)
        _logger.debug(default_fields)
        return rec
