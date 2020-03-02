# -*- coding:utf-8 -*-

from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)


class BsdUnitCreateInvoice(models.TransientModel):
    _name = 'bsd.unit.create.invoice'

    def _get_unit(self):
        res = self.env['bsd.unit'].browse(self._context.get('active_ids', []))
        _logger.debug("get unit")
        _logger.debug(res)
        return res

    bsd_unit_ids = fields.Many2many('bsd.unit', string="Unit", readonly=True, default=_get_unit)
    bsd_year = fields.Selection([(str(num), str(num)) for num in range(2020, 2100)],
                                string='Năm',
                                default='2020', required=True)
    bsd_month = fields.Selection([(str(num), str(num)) for num in range(1, 13)],
                                 string='Tháng',
                                 default='1', required=True)
    bsd_date_invoice = fields.Date(string="Ngày in hóa đơn", default=fields.Date.today(), required=True)
    bsd_due_date = fields.Date(string="Hạn thanh toán", default=fields.Date.today())
    bsd_invoice_origin = fields.Text(string="Nội dung")

    def create_invoice(self):
        for unit in self.bsd_unit_ids.filtered(lambda x: x.state in ['rent', 'sale']):
            unit.create_invoice(invoice_date=self.bsd_date_invoice,
                                invoice_date_due=self.bsd_due_date,
                                invoice_origin=self.bsd_invoice_origin,
                                month=self.bsd_month,
                                year=self.bsd_year)

