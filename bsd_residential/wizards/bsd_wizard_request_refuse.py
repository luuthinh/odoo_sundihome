# -*- coding:utf-8 -*-

from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)


class BsdWizardRequestRefuse(models.TransientModel):
    _name = 'bsd.wizard.request.refuse'

    def _default_registry_request(self):
        request = self.env['bsd.registry.request'].browse(self._context.get('active_id'))
        return request.id

    bsd_request_id = fields.Many2one('bsd.registry.request', string="Phiếu đăng ký ",
                                     default=_default_registry_request)
    bsd_note = fields.Text(string="Lý do từ chối", required=True)

    def update_note(self):
        if self.bsd_note:
            self.bsd_request_id.write({'state': 'refuse',
                                       'bsd_confirm_user': self.env.uid,
                                       'bsd_confirm_date': fields.Date.today(),
                                       'bsd_note': self.bsd_note})