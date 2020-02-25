# -*- coding:utf-8 -*-
import datetime, calendar
from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)


class BsdWizardCreateSwim(models.TransientModel):
    _name = 'bsd.wizard.create.swim'
    _description = 'Tạo mới hội viên hoặc gia hạn'

    def _get_so(self):
        so = self.env['sale.order'].browse(self._context.get('active_ids', []))
        _logger.debug("get so")
        _logger.debug(so)
        return so

    bsd_so_id = fields.Many2one('sale.order', string="Đơn bán", default=_get_so)
    bsd_type = fields.Selection([('new', "Đăng ký mới"), ('add', 'Gia hạn')], string="Loại", default='new')
    bsd_residential_id = fields.Many2one('bsd.residential', string="Cư dân")
    bsd_residential_swim_id = fields.Many2one('bsd.residential.swim', string='Hội viên Hồ bơi')
    bsd_int_month = fields.Integer(string="Thời hạn")
    bsd_from_date = fields.Date(string="Từ ngày", default=fields.Date.today())
    bsd_to_date = fields.Date(string="Đến ngày", default=fields.Date.today())
    bsd_product_id = fields.Many2one('product.product', string="Dịch vụ")

    def _add_months(self, sourcedate, months):
        month = sourcedate.month - 1 + months
        year = sourcedate.year + month // 12
        month = month % 12 + 1
        day = min(sourcedate.day, calendar.monthrange(year, month)[1])
        return datetime.date(year, month, day)

    @api.onchange('bsd_residential_swim_id')
    def _onchange_residential_gym(self):
        if self.bsd_residential_gym_id:
            self.bsd_from_date = max(self.bsd_residential_gym_id.bsd_line_ids.mapped('bsd_to_date')) + \
                                 datetime.timedelta(days=1)

    @api.onchange('bsd_int_month', 'bsd_from_date')
    def _onchange_int_month(self):
        self.bsd_to_date = self._add_months(self.bsd_from_date, self.bsd_int_month) - datetime.timedelta(days=1)

    @api.onchange('bsd_type')
    def _onchange_type(self):
        if self.bsd_type == 'new':
            self.bsd_residential_gym_id = False
        else:
            self.bsd_residential_id = False

    def action_create(self):
        if self.bsd_type == 'new':
            self.env['bsd.residential.swim'].create({
                'bsd_sequence': 'New',
                'bsd_residential_id': self.bsd_residential_id.id,
                'bsd_partner_id': self.bsd_residential_id.partner_id.id,
                'name': self.bsd_residential_id.name,
                'bsd_gender': self.bsd_residential_id.bsd_gender,
                'bsd_birthday': self.bsd_residential_id.bsd_birthday,
                'bsd_email': self.bsd_residential_id.email,
                'bsd_mobile': self.bsd_residential_id.mobile,
                'bsd_registry_date': self.bsd_so_id.date_order,
                'bsd_product_id': self.bsd_product_id.id,
                'bsd_line_ids': [(0, 0, {'name': self.bsd_type,
                                         'bsd_from_date': self.bsd_from_date,
                                         'bsd_to_date': self.bsd_to_date,
                                         'bsd_so_id': self.bsd_so_id.id})]
            })
        else:
            self.bsd_residential_swim_id.write({
                'bsd_line_ids': [(0, 0, {'name': self.bsd_type,
                                         'bsd_from_date': self.bsd_from_date,
                                         'bsd_to_date': self.bsd_to_date,
                                         'bsd_so_id': self.bsd_so_id.id})]
            })
