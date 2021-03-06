# -*- coding:utf-8 -*-

import calendar, datetime

from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)


class BsdWizardGymPause(models.TransientModel):
    _name = 'bsd.wizard.gym.run'
    _description = 'Cập nhật ngày hội viên Gym tập lại'

    def _get_gym(self):
        gym = self.env['bsd.residential.gym'].browse(self._context.get('active_ids', []))
        return gym

    bsd_residential_gym_id = fields.Many2one('bsd.residential.gym', string="Hội viên", default=_get_gym, readony=True)
    bsd_date = fields.Date(string='Ngày tập lại', default=fields.Date.today())

    def action_add(self):
        pause = self.bsd_residential_gym_id.bsd_residential_gym_pause_ids.filtered(lambda x: x.state == 'active')
        if pause:
            from_date = pause.bsd_from_date
            to_date = self.bsd_date if self.bsd_date <= pause.bsd_to_date else pause.bsd_to_date

            day = to_date - from_date

        last_date = max(self.bsd_residential_gym_id.bsd_line_ids.mapped('bsd_to_date'))

        line = self.bsd_residential_gym_id.bsd_line_ids.filtered(lambda x: x.bsd_to_date == last_date)

        pause.write({
            'state': 'done'
        })
        if line:
            line.write({
                'bsd_to_date': last_date + day
            })
        self.bsd_residential_gym_id.write({
            'state': 'active'
        })
