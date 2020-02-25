# -*- coding:utf-8 -*-

from odoo import models, fields, api


class AccountPayment(models.Model):
    _inherit = "account.payment"

    bsd_tenancy_id = fields.Many2one('bsd.contract.tenancy', string="Tenancy")

    def post(self):
        super(AccountPayment, self).post()
        if self.bsd_tenancy_id:
            if self.payment_type == 'inbound':
                self.bsd_tenancy_id.bsd_deposit_received = True
            if self.payment_type == 'outbound':
                self.bsd_tenancy_id.bsd_deposit_return = True
                self.bsd_tenancy_id.bsd_amount_return = self.amount
