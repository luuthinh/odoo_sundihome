# -*- coding:utf-8 -*-

from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)


class BsdWizardCreateCard(models.TransientModel):
    _name = 'bsd.wizard.create.card'

    def _get_registry_card(self):
        card = self.env['bsd.registry.card'].browse(self._context.get('active_id'))
        list_res = []
        for line in card.bsd_line_ids:
            _logger.debug(line)
            list_res.append(self.env['bsd.wizard.create.card.line'].create({
                    'bsd_wizard_id': self.id,
                    'bsd_residential_id': line.bsd_residential_id.id,
            }))
        return [ids.id for ids in list_res]

    def _default_registry_card(self):
        card = self.env['bsd.registry.card'].browse(self._context.get('active_id'))
        return card.id

    bsd_registry_card_id = fields.Many2one('bsd.registry.card', string="Phiếu đăng ký thẻ",
                                           default=_default_registry_card)
    bsd_line_ids = fields.One2many('bsd.wizard.create.card.line', 'bsd_wizard_id',
                                   string="Bảng cư dân",
                                   default=_get_registry_card)

    def create_card(self):
        for line in self.bsd_line_ids:
            line.bsd_residential_id.write({
                'bsd_card_id': line.bsd_card_id.id,
                'bsd_card_date': line.bsd_card_date,
            })
        self.bsd_registry_card_id.write({
            'state': 'card',
        })
        for line in self.bsd_line_ids:
            line.bsd_card_id.write({
                'state': 'active',
            })


class BsdWizardCreateCardLine(models.TransientModel):
    _name = 'bsd.wizard.create.card.line'

    bsd_wizard_id = fields.Many2one('bsd.wizard.create.card')
    bsd_residential_id = fields.Many2one('bsd.residential', string='Cư dân')
    bsd_card_id = fields.Many2one('bsd.residential.card', string='Thẻ cư dân')
    bsd_card_date = fields.Date(string="Ngày cấp", default=fields.Date.today())

