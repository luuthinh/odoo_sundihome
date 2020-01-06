# -*- coding:utf-8 -*-

from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)


class BsdTenancyRenew(models.TransientModel):
    _name = 'bsd.tenancy.renew'

    def _get_tenancy(self):
        tenancy = self.env['account.analytic.account'].browse(self._context.get('action_id'))
        _logger.debug("tenancy")
        _logger.debug(self._context.get('action_id'))
        _logger.debug(tenancy)
        return tenancy

    bsd_tenancy_id = fields.Many2one('account.analytic.account', string="Tenancy", default=_get_tenancy)
    bsd_start_date = fields.Date(string="Start Date", required=True)
    bsd_expiration_date = fields.Date(string="Expiration Date", required=True)
    bsd_rent_type_id = fields.Many2one('bsd.rent.type', string="Rent Type", required=True)

    @api.onchange('bsd_tenancy_id')
    def _onchange_tenancy(self):
        self.bsd_start_date = self.bsd_tenancy_id.bsd_expiration_date

    def renew_contract(self):
        if self.bsd_tenancy_id:
            self.bsd_tenancy_id.write({
                'bsd_start_date': self.bsd_start_date,
                'bsd_expiration_date': self.bsd_expiration_date,
                'bsd_rent_type_id': self.bsd_rent_type_id,
                'state': 'draft',
            })

