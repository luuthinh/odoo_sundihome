# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)


class BsdUnit(models.Model):
    _name = 'bsd.unit'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin', 'image.mixin']
    _description = 'Thông tin Unit'
    _rec_name = 'complete_name'

    name = fields.Char(string='Unit', required=True)
    complete_name = fields.Char('Mã unit', compute='_compute_complete_name', store=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Currency", readonly=True)
    bsd_block_id = fields.Many2one('bsd.block', string="Tòa nhà", required=True)
    bsd_floor_id = fields.Many2one('bsd.floor', string="Tầng")
    bsd_type = fields.Selection([('res', 'Căn hộ'), ('off', 'Văn Phòng'), ('mall', 'TTTM')], string="Loại hình",
                                default='res')
    bsd_categ_id = fields.Many2one('bsd.unit.category', string="Phân loại")

    bsd_responsible_id = fields.Many2one('res.partner', string="Chủ hộ")
    bsd_tenant_id = fields.Many2one('res.partner', string="Người thuê")
    bsd_owner_id = fields.Many2one('res.partner', string="Chủ sở hữu")
    bsd_manager_id = fields.Many2one('hr.employee', related='bsd_floor_id.bsd_manager_id', string="Nhân viên quản lý")
    state = fields.Selection([('ready', 'Sẵn sàng sử dụng'),
                             ('rent', 'Đang thuê'),
                             ('sale', 'Đã bán'),
                             ('pause', 'Tạm ngưng sử dụng')], string="Tình trạng", default='ready', tracking=1)
    # Thông tin chi tiết
    bsd_built_up_area = fields.Float(string="Diện tích thực tế")
    bsd_carpet_area = fields.Float(string="Diện tích sử dụng")
    bsd_management_fee = fields.Monetary(string="Phí quản lý")
    bsd_furnished = fields.Selection([('none', 'Không'),
                                      ('semi', 'Một phần'),
                                      ('full', 'Đầy đủ')], string='Gói bàn giao')
    bsd_car_parking = fields.Integer(string="Số chỗ giữ ô tô")
    bsd_bike_parking = fields.Integer(string="Số chỗ giữ xe 2 bánh")
    bsd_balcony = fields.Integer(string="Ban công/Ngoài trời")
    bsd_bedroom = fields.Integer(string="Phòng ngủ")
    bsd_bathroom = fields.Integer(string="Phòng tắm")
    bsd_kitchen = fields.Integer(string="Phòng ăn")
    bsd_living_room = fields.Integer(string="Phòng khách")
    bsd_balconies = fields.Integer(string="Phòng em bé")

    color = fields.Integer()

    bsd_location_id = fields.Many2one('stock.location', string="Vị trí", readonly=True)

    @api.depends('name', 'bsd_block_id.bsd_code', 'bsd_floor_id.name')
    def _compute_complete_name(self):
        for each in self:
            if each.bsd_block_id and each.bsd_floor_id:
                each.complete_name = '%s,%s.%s' % (
                                                      each.bsd_block_id.bsd_code,
                                                      each.bsd_floor_id.name,
                                                      each.name)
            else:
                each.complete_name = each.name

    def view_stock_quant(self):
        domain = [('bsd_location_id.id', '=', self.bsd_location_id.id)]
        _logger.debug("domain")
        _logger.debug(domain)
        return {
            'type': 'ir.actions.act_window',
            'name': _('Thiết bị'),
            'view_mode': 'tree,form',
            'res_model': 'stock.production.lot',
            'domain': domain,
        }

    _sql_constraints = [
        ('bsd_location_id_unique',
         'UNIQUE(bsd_location_id)',
         "Vị trí đã được chọn"),
    ]

    @api.model
    def create(self, vals_list):
        unit_name = self.env['bsd.unit'].search([('bsd_floor_id', '=', vals_list['bsd_floor_id']),
                                                 ('bsd_block_id', '=', vals_list['bsd_block_id'])]).mapped('name')
        if 'name' in vals_list.keys():
            if vals_list['name'] in unit_name:
                raise ValidationError("Tầng lầu đã có unit: %s" % vals_list['name'])

        if 'bsd_floor_id' in vals_list.keys():
            location_id = self.env['bsd.floor'].browse(vals_list['bsd_floor_id']).bsd_location_id.id
            location = self.env['stock.location'].create({
                'name': vals_list['name'],
                'location_id': location_id if location_id else False,
                'usage': 'internal',
            }).id
            vals_list['bsd_location_id'] = location
        return super(BsdUnit, self).create(vals_list)

    def write(self, vals):
        unit_name = self.env['bsd.unit'].search([('bsd_floor_id', '=', self.bsd_floor_id.id),
                                                 ('bsd_block_id', '=', self.bsd_block_id.id)]).mapped('name')
        if 'name' in vals.keys():
            if vals['name'] in unit_name:
                raise ValidationError("Unit đã tồn tại: %s" % vals['name'])
        return super(BsdUnit, self).write(vals)


class BsdRoomType(models.Model):
    _name = 'bsd.room.type'
    _description = 'Thông tin phòng'

    name = fields.Char(string="Name", required=True)


class BsdUnitCategory(models.Model):
    _name = 'bsd.unit.category'
    _description = 'Unit Category'
    _parent_name = "bsd_parent_id"
    _parent_store = True
    _rec_name = 'complete_name'
    _order = 'complete_name'

    name = fields.Char(string="Name", required=True)
    bsd_parent_id = fields.Many2one('bsd.unit.category', string="Parent", index=True, ondelete='cascade')

    complete_name = fields.Char(
        'Complete Name', compute='_compute_complete_name',
        store=True)
    parent_path = fields.Char(index=True)
    child_id = fields.One2many('bsd.unit.category', 'bsd_parent_id', 'Child Categories')

    @api.depends('name', 'bsd_parent_id.complete_name')
    def _compute_complete_name(self):
        for category in self:
            if category.bsd_parent_id:
                category.complete_name = '%s / %s' % (category.bsd_parent_id.complete_name, category.name)
            else:
                category.complete_name = category.name


class BsdUnitView(models.Model):
    _name = 'bsd.unit.view'
    _description = 'View Unit'

    name = fields.Char(string="View")
