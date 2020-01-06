# -*-coding:utf-8 -*-

from odoo import models, fields, api, _


class AccountAsset(models.Model):
    _inherit = 'account.asset'

    bsd_residential_ids = fields.One2many('bsd.residential', 'bsd_unit_id', string="Residential", readonly=True)

    def view_history_residential(self):
        domain = [('state', '=', 'out'), ('bsd_unit_id.id', '=', self.id)]
        return {
            'type': 'ir.actions.act_window',
            'name': _('Lịch sử cư dân'),
            'view_mode': 'tree,form',
            'res_model': 'bsd.residential',
            'domain': domain
        }

    def view_history_responsible(self):
        domain = [('bsd_unit_id.id', '=', self.id)]
        return {
            'type': 'ir.actions.act_window',
            'name': _('Lịch sử chủ hộ'),
            'view_mode': 'tree,form',
            'res_model': 'bsd.residential.responsible.history',
            'domain': domain
        }


class BsdResidential(models.Model):
    _name = 'bsd.residential'

    bsd_unit_id = fields.Many2one('account.asset', string="Unit")
    name = fields.Many2one('res.partner', string='Residential')
    # bsd_partner_id = fields.Many2one('res.partner', string="Chủ hộ")
    bsd_image = fields.Binary(related='name.image_1920')
    bsd_mobile = fields.Char(related="name.mobile", string="Mobile")
    bsd_email = fields.Char(related="name.email", string="Email")
    bsd_function = fields.Char(related="name.function", string="Job Position")
    bsd_relationship_id = fields.Many2one('bsd.residential.relationship', string="Relationship")
    bsd_date_move_on = fields.Date(string="Date Move On", readonly=True)
    bsd_date_move_out = fields.Date(string="Date Move Out", readonly=True)
    active = fields.Boolean(string='Active', default=True)
    state = fields.Selection([('in', 'tạm trú'), ('out', 'Đã chuyển đi')], default='in')


class BsdResidentialRelationship(models.Model):
    _name = 'bsd.residential.relationship'

    name = fields.Char(string="Relationship", required=True)


class BsdResidentialHistory(models.Model):
    _name = 'bsd.residential.responsible.history'

    name = fields.Char(string="Name")
    bsd_unit_id = fields.Many2one('account.asset')
    bsd_cmnd = fields.Char(string="CMND")
    bsd_from_date = fields.Date(string="From Date")
    bsd_to_date = fields.Date(string="To Date")