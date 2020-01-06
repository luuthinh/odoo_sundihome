# -*- coding:utf-8 -*-

from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)


class BsdWizardRegistryRequest(models.TransientModel):
    _name = 'bsd.wizard.registry.request'

    def _get_request(self):
        request = self.env['bsd.registry.request'].browse(self._context.get('action_id'))
        _logger.debug("get request line")
        _logger.debug(self._context.get('action_id'))
        _logger.debug(request)
        return request

    bsd_request_id = fields.Many2one('bsd.registry.request', string="Request", default=_get_request)
    bsd_partner_id = fields.Many2one('res.partner', string="Cư Dân")

    def add_partner(self):
        if self.bsd_partner_id:
            self.env['bsd.registry.request.line'].create({
                'bsd_registry_request_id': self.bsd_request_id.id,
                'name': self.bsd_partner_id.name,
                'birthday': self.bsd_partner_id.bsd_birthday,
                'cmnd': self.bsd_partner_id.bsd_cmnd,
                'vat': self.bsd_partner_id.vat,
                'function': self.bsd_partner_id.function,
                'email': self.bsd_partner_id.email,
                'mobile': self.bsd_partner_id.mobile,
                'is_residential': True,
            })
