# -*- coding:utf-8 -*-

import calendar, datetime

from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)


class BsdWizardGymPause(models.TransientModel):
    _name = 'bsd.wizard.gym.pause'
    _description = 'Cập nhật trạng thái bảo lưu hội viên Gym'

    def _get_gym(self):
        gym = self.env['bsd.residential.gym'].browse(self._context.get('active_ids', []))
        return gym

    bsd_residential_gym_id = fields.Many2one('bsd.residential.gym', string="Hội viên", default=_get_gym, readony=True)

    bsd_reason = fields.Text(string="Lý do", required=True)
    bsd_int_month = fields.Integer(string="Số tháng bảo lưu", required=True)
    bsd_from_date = fields.Date(string="Từ ngày", default=fields.Date.today())
    bsd_to_date = fields.Date(string="Đến ngày", required=True)

    def _add_months(self, sourcedate, months):
        month = sourcedate.month - 1 + months
        year = sourcedate.year + month // 12
        month = month % 12 + 1
        day = min(sourcedate.day, calendar.monthrange(year, month)[1])
        return datetime.date(year, month, day)

    @api.onchange('bsd_int_month', 'bsd_from_date')
    def _onchange_int_month(self):
        self.bsd_to_date = self._add_months(self.bsd_from_date, self.bsd_int_month) - datetime.timedelta(days=1)

    def action_create(self):
        self.bsd_residential_gym_id.write({
            'bsd_residential_gym_pause_ids': [(0, 0, {'bsd_from_date': self.bsd_from_date,
                                                      'bsd_to_date': self.bsd_to_date,
                                                      'bsd_reason': self.bsd_reason,
                                                      })],
            'state': 'pause',
        })
