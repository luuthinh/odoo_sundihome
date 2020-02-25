# -*- coding:utf-8 -*-

import datetime
import calendar

from odoo import models, fields, api, _
from odoo.exceptions import Warning
from odoo.tools.profiler import profile
import logging
_logger = logging.getLogger(__name__)


class BsdBlockCreateInvoice(models.TransientModel):
    _name = 'bsd.block.create.invoice'

    bsd_block_id = fields.Many2one('bsd.block', string="Tòa nhà")
    bsd_unit_type = fields.Selection([('res', 'Căn hộ'), ('off', 'Văn Phòng'), ('mall', 'TTTM')], string="Loại unit")
    bsd_year = fields.Selection([(str(num), str(num)) for num in range(2020, 2100)],
                                string='Năm',
                                default='2020', required=True)
    bsd_month = fields.Selection([(str(num), str(num)) for num in range(1, 12)],
                                 string='Tháng',
                                 default='1', required=True)
    bsd_date_invoice = fields.Date(string="Ngày in hóa đơn", default=fields.Date.today(), required=True)
    bsd_due_date = fields.Date(string="Hạn thanh toán", default=fields.Date.today())
    bsd_invoice_origin = fields.Text(string="Memo")

    @profile
    def create_invoice(self):
        units = self._get_unit()
        _logger.debug("units cần tạo hóa đơn")
        _logger.debug(units)
        values = []
        for unit in units:
            value = unit._prepare_invoice_values(invoice_date=self.bsd_date_invoice,
                                                 invoice_date_due=self.bsd_due_date,
                                                 invoice_origin=self.bsd_invoice_origin,
                                                 month=self.bsd_month, year=self.bsd_year)
            values.append(value)
        self.env['account.move'].create(values)
        # cập nhật lại ngày xuất hóa đơn
        for unit in units:
            unit.write({
                'bsd_date_invoice': self.bsd_date_invoice
            })

    def _get_unit(self):
        self.ensure_one()
        item_ids = []
        if not self.bsd_block_id and not self.bsd_unit_type:
            self.env.cr.execute(
                """
                select id,bsd_date_invoice from bsd_unit WHERE state IN ('sale','rent');  
                """
            )
            item_ids = self.env.cr.fetchall()
        elif self.bsd_block_id and self.bsd_unit_type:
            self.env.cr.execute(
                """
                select id,bsd_date_invoice from bsd_unit WHERE state IN ('sale','rent') AND bsd_block_id = %s AND bsd_type = %s;  
                """,
                (self.bsd_block_id.id, self.bsd_unit_type))
            item_ids = self.env.cr.fetchall()
        elif self.bsd_block_id and not self.bsd_unit_type:
            self.env.cr.execute(
                """
                select id,bsd_date_invoice from bsd_unit WHERE state IN ('sale','rent') AND bsd_block_id = %s;  
                """,
                (self.bsd_block_id.id,))
            item_ids = self.env.cr.fetchall()
        elif not self.bsd_block_id and self.bsd_unit_type:
            self.env.cr.execute(
                """
                select id,bsd_date_invoice from bsd_unit WHERE state IN ('sale','rent') AND bsd_type = %s;  
                """,
                (self.bsd_unit_type,))
            item_ids = self.env.cr.fetchall()

        _logger.debug(item_ids)

        def add_months(sourcedate, months):
            month = sourcedate.month - 1 + months
            year = sourcedate.year + month // 12
            month = month % 12 + 1
            day = min(sourcedate.day, calendar.monthrange(year, month)[1])
            return datetime.date(year, month, day)
        int_year = int(self.bsd_year)
        int_month = int(self.bsd_month)
        last_day = calendar.monthrange(int_year, int_month)[1]
        first_day_of_month = datetime.date(int_year, int_month, 1)
        first_day_of_month_prev = add_months(first_day_of_month, -1)
        last_day_of_month = datetime.date(int_year, int_month, last_day)
        last_day_of_month_prev = add_months(last_day_of_month, -1)

        id_unit_no_invoice_date = [item[0] for item in item_ids if not item[1]]
        id_unit_invoice_date = [item for item in item_ids if item[1]]
        id_unit_no_invoice_last_month = [item[0] for item in id_unit_invoice_date if item[1] <= first_day_of_month_prev]
        id_unit_invoice_last_month = [item[0] for item in id_unit_invoice_date if first_day_of_month_prev <= item[1] <= last_day_of_month_prev]
        _logger.debug("id no date invoice")
        _logger.debug(id_unit_no_invoice_date)
        _logger.debug("id no invoice last month")
        _logger.debug(id_unit_no_invoice_last_month)
        _logger.debug("id invoice last month")
        _logger.debug(id_unit_invoice_last_month)
        # if id_unit_no_invoice_last_month:
        #     unit_no_invoice_last_month = self.env['bsd.unit'].browse(id_unit_no_invoice_last_month).mapped('complete_name')
        #     raise Warning(_("Các unit không có hóa đơn tháng trước: %s" % unit_no_invoice_last_month))
        return self.env['bsd.unit'].browse(id_unit_invoice_last_month + id_unit_no_invoice_date)
