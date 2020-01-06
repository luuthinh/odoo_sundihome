# -*- coding:utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class BsdBARequestType(models.Model):
    _name = 'bsd.ba.request.type'
    _description = 'Request Type'

    name = fields.Char(string="Name", required=True)


class BsdBARequest(models.Model):
    _name = 'bsd.ba.request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "BA request"

    name = fields.Char(string="Yêu cầu", copy=False, tracking=1,
                       compute='_compute_complete_name', store=True)
    bsd_project_id = fields.Many2one('bsd.project', string="Dự Án", required=True,
                                states={'draft': [('readonly', False)],
                                        'waiting': [('readonly', True)],
                                        'refuse': [('readonly', True)],
                                        'approve': [('readonly', True)]})
    bsd_id = fields.Char(string="ID_Req", default="ID", tracking=2,
                         states={'draft': [('readonly', False)],
                                 'waiting': [('readonly', True)],
                                 'refuse': [('readonly', True)],
                                 'approve': [('readonly', True)]})
    bsd_sequence = fields.Char(string="Sequence", default='New')
    active = fields.Boolean(default=True)
    state = fields.Selection([('draft', 'Tạo yêu cầu'),
                              ('waiting', 'chờ duyệt'),
                              ('refuse', 'từ chối'),
                              ('approve', 'chấp nhận')], default='draft', tracking=8)
    bsd_send_user = fields.Many2one('res.users', 'Người yêu cầu', default=lambda self: self.env.uid, readonly=True, tracking=9)
    bsd_confirm_user = fields.Many2one('res.users', 'Quản lý dự án', readonly=True, tracking=10)
    bsd_actual_user = fields.Many2one('res.users', 'Người thực hiện')
    bsd_send_date = fields.Date(string="Ngày tạo", default=fields.Date.today(), tracking=5)
    bsd_confirm_date = fields.Date(string="Ngày duyệt", readonly=True, tracking=6)
    bsd_due_date = fields.Date(string="Ngày dự kiến hoàn thành")
    bsd_parent_id = fields.Many2one('bsd.ba.request', string="ID_Req parent",
                                    states={'draft': [('readonly', False)],
                                            'waiting': [('readonly', True)],
                                            'refuse': [('readonly', True)],
                                            'approve': [('readonly', True)]})
    bsd_type = fields.Many2one('bsd.ba.request.type', string="Loại",
                                states={'draft': [('readonly', False)],
                                        'waiting': [('readonly', True)],
                                        'refuse': [('readonly', True)],
                                        'approve': [('readonly', True)]})
    bsd_description = fields.Text(string="Mô tả",
                                  states={'draft': [('readonly', False)],
                                        'waiting': [('readonly', True)],
                                        'refuse': [('readonly', True)],
                                        'approve': [('readonly', True)]})
    bsd_screen_id = fields.Many2one('bsd.screen', string="Màn hình", required=True,
                                    states={'draft': [('readonly', False)],
                                        'waiting': [('readonly', True)],
                                        'refuse': [('readonly', True)],
                                        'approve': [('readonly', True)]})

    def action_send(self):
        self.write({'state': 'waiting'})

    def action_refuse(self):
        self.write({'state': 'refuse',
                    'bsd_confirm_user': self.env.uid,
                    'bsd_confirm_date': fields.Date.today()})

    def action_confirm(self):
        if self.env['res.users'].has_group('bsd_manager_project.group_manager'):
            pass
        else:
            raise UserError('You not manager')

        self.write({'state': 'approve',
                    'bsd_confirm_user': self.env.uid,
                    'bsd_confirm_date': fields.Date.today()})

    @api.depends('bsd_project_id', 'bsd_id', 'bsd_sequence')
    def _compute_complete_name(self):
        if self.bsd_project_id:
            for each in self:
                each.name = '[' + each.bsd_sequence + ']' + each.bsd_project_id.bsd_code + '-' + each.bsd_id
        else:
            for each in self:
                each.name = '[' + each.bsd_sequence + ']' + each.bsd_id

    @api.model
    def create(self, vals):
        if vals.get('bsd_sequence', 'New') == 'New':
            _logger.debug("create new")
            vals['bsd_sequence'] = self.env['ir.sequence'].next_by_code('bsd.ba.request') or '/'
        return super(BsdBARequest, self).create(vals)
