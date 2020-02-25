# -*- coding:utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)


class BsdFloorFor(models.Model):
    _name = 'bsd.floor.for'

    name = fields.Char(string="Mục đích sử dụng", required=True)


class BsdFloorType(models.Model):
    _name = 'bsd.floor.type'
    _description = 'Loại tầng'
    _parent_name = "bsd_parent_id"
    _parent_store = True
    _rec_name = 'complete_name'
    _order = 'complete_name'

    name = fields.Char(string="Tầng/Dãy", required=True)
    bsd_parent_id = fields.Many2one('bsd.floor.type', string="Danh mục cha", index=True, ondelete='cascade')

    complete_name = fields.Char(
        'Loại', compute='_compute_complete_name',
        store=True)
    parent_path = fields.Char(index=True, string="Cây thư mục")
    child_id = fields.One2many('bsd.floor.type', 'bsd_parent_id', 'Danh mục con')

    @api.depends('name', 'bsd_parent_id.complete_name')
    def _compute_complete_name(self):
        for category in self:
            if category.bsd_parent_id:
                category.complete_name = '%s / %s' % (category.bsd_parent_id.complete_name, category.name)
            else:
                category.complete_name = category.name


class BsdFloor(models.Model):
    _name = 'bsd.floor'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Thông tin tầng lầu'
    _rec_name = 'complete_name'

    name = fields.Char(string="Tầng", required=True, unique=True)
    complete_name = fields.Char('Mã tầng', compute='_compute_complete_name', store=True)
    bsd_type_id = fields.Many2one('bsd.floor.type', string="Loại")
    bsd_for_id = fields.Many2one('bsd.floor.for', string="Mục đích sử dụng")
    bsd_block_id = fields.Many2one('bsd.block', string="Tòa nhà", required=True)
    bsd_manager_id = fields.Many2one('hr.employee', string="Nhân viên quản lý")
    bsd_s_floor = fields.Float(string="Diện tích sàn")
    bsd_unit_ids = fields.One2many('bsd.unit', 'bsd_floor_id', string="Units")
    bsd_location_id = fields.Many2one('stock.location', string="Phân kho", readonly=True)
    bsd_count_unit = fields.Integer('# Unit', compute='_compute_unit')

    _sql_constraints = [
        ('bsd_location_id_unique',
         'UNIQUE(bsd_location_id)',
         "Vị trí đã được chọn"),
    ]

    # @api.constrains('name')
    # def _check_name(self):
    #     for record in self:
    #         floor_name = self.env['bsd.floor'].search([('bsd_block_id', '=', record.bsd_block_id.id)]).mapped('name')
    #         _logger.debug(floor_name)
    #         if record.name in floor_name:
    #             raise ValidationError("Tầng lầu đã có: %s" % record.name)

    @api.depends('name', 'bsd_block_id.bsd_code')
    def _compute_complete_name(self):
        for each in self:
            if each.bsd_block_id:
                each.complete_name = '%s-%s' % (each.bsd_block_id.bsd_code, each.name)
            else:
                each.complete_name = each.name

    def _compute_unit(self):
        for each in self:
            _logger.debug("Debug _compute_unit")
            each.bsd_count_unit = len(each.bsd_unit_ids)

    def unit_view(self):
        domain = [('bsd_floor_id.id', '=', self.id)]
        action = self.env.ref('bsd_block.bsd_unit_action').read()[0]
        action.update({'domain': str(domain)})
        action.update({'context': "{'default_bsd_floor_id':%s}" % self.id})
        return action

    @api.model
    def create(self, vals_list):
        floor_name = self.env['bsd.floor'].search([('bsd_block_id', '=', vals_list['bsd_block_id'])]).mapped('name')
        _logger.debug(floor_name)
        if vals_list['name'] in floor_name:
            raise ValidationError("Tầng lầu đã có: %s" % vals_list['name'])

        location = self.env['stock.location'].create({
            'name': vals_list['name'],
            'location_id': self.env['bsd.block'].browse(vals_list['bsd_block_id']).bsd_warehouse_id.view_location_id.id,
            'usage': 'internal',
        }).id
        vals_list['bsd_location_id'] = location
        return super(BsdFloor, self).create(vals_list)

    def write(self, vals):
        _logger.debug(self)
        _logger.debug(vals)
        floor_name = self.env['bsd.floor'].search([('bsd_block_id', '=', self.bsd_block_id.id)]).mapped('name')
        _logger.debug(floor_name)
        if 'name' in vals.keys():
            if vals['name'] in floor_name:
                raise ValidationError("Tầng lầu đã có: %s" % vals['name'])
        return super(BsdFloor, self).write(vals)
