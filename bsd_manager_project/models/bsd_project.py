# -*- coding:utf-8 -*-

from odoo import models, fields, api, tools, _
import logging
_logger = logging.getLogger(__name__)


class BsdProject(models.Model):
    _name = 'bsd.project'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Thông tin dự án'

    name = fields.Char(string="Dự án", required=True)
    bsd_code = fields.Char(string="Mã", required=True, size=3, unique=True)
    bsd_manager_id = fields.Many2one('res.users', string="Quản lý dự án")


class BsdScreen(models.Model):
    _name = 'bsd.screen'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Thông tin màn hình"

    name = fields.Char(string="Màn hình", required=True)
    bsd_project_id = fields.Many2one('bsd.project', string="Dự án")
