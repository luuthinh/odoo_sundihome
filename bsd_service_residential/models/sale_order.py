# -*- coding:utf-8 -*-

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    bsd_count_gym = fields.Integer(compute='_compute_gym')
    bsd_count_swim = fields.Integer(compute='_compute_swim')

    def _compute_gym(self):
        for each in self:
            gym_line = self.env['bsd.residential.gym.line'].search([('bsd_so_id', '=', self.id)])
            each.bsd_count_gym = len(gym_line)

    def _compute_swim(self):
        for each in self:
            swim_line = self.env['bsd.residential.swim.line'].search([('bsd_so_id', '=', self.id)])
            each.bsd_count_swim = len(swim_line)

    def create_gym_card(self):
        action = self.env.ref('bsd_service_residential.bsd_wizard_create_gym_action').read()[0]
        return action

    def create_swim_card(self):
        action = self.env.ref('bsd_service_residential.bsd_wizard_create_swim_action').read()[0]
        return action
