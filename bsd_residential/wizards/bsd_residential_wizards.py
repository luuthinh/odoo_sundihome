# -*- coding:utf-8 -*-


from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)


class BsdResidentialWizard(models.TransientModel):
    _name = 'bsd.residential.wizard'

    @api.model
    def _get_residential(self):
        res = self.env['bsd.residential'].browse(self._context.get('active_ids', []))
        _logger.debug("get res")
        _logger.debug(self._context.get('active_ids',[]))
        _logger.debug(res)
        return res

    bsd_residential_ids = fields.Many2many('bsd.residential', string="Cư dân", default=_get_residential, readonly=True)

    def update_residential(self):
        for res in self.bsd_residential_ids:
            his = res.bsd_history_ids.filtered(lambda x: x.state == 'in')
            his.write({
                'state': 'out',
                'bsd_date_move_out': fields.Date.today()
            })
