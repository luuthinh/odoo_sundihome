# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)


class AccountAsset(models.Model):
    _inherit = 'account.asset'
    _description = 'Unit Information'

    def name_get(self):
        res = []
        for asset in self:
            res.append((asset.id, asset.complete_name))
        return res
        # return super(AccountAsset, self).name_get()

    bsd_image = fields.Binary(string="Image")
    name = fields.Char(string='Name', required=True,
                       states={'draft': [('readonly', False)], 'model': [('readonly', False)]})
    complete_name = fields.Char('Complete Name', compute='_compute_complete_name', store=True)
    bsd_categ_id = fields.Many2one('bsd.unit.category', string="Category")
    bsd_type = fields.Selection([('res', 'Căn hộ'), ('off', 'Văn Phòng'), ('mall', 'TTTM')], string="Type", defaule='home')
    bsd_floor_id = fields.Many2one('bsd.real.estate.floor', string="Floor")
    bsd_block_id = fields.Many2one('bsd.real.estate.block', string="Block")
    bsd_area_id = fields.Many2one(related='bsd_block_id.bsd_area_id')
    bsd_project_id = fields.Many2one('bsd.real.estate.project', string="Project")

    bsd_inventor_id = fields.Many2one(related='bsd_project_id.bsd_inventor_id', string="Chủ đầu tư")
    bsd_responsible_id = fields.Many2one('res.partner', string="Chủ hộ")

    bsd_tenant_id = fields.Many2one('res.partner', string="Người thuê")
    bsd_owner_id = fields.Many2one('res.partner', string="Chủ sở hữu")

    # bsd_facing = fields.Selection([('1', 'Đông'),
    #                                   ('2', 'Tây'),
    #                                   ('3', 'Nam'),
    #                                   ('4', 'Bắc'),
    #                                   ('5', 'Đông Bắc'),
    #                                   ('6', 'Đông Nam'),
    #                                   ('7', 'Tây Bắc'),
    #                                   ('8', 'Tây Nam')], string="Facing")
    # bsd_view = fields.Many2one('bsd.unit.view', string="View")
    # Thông tin chung
    bsd_price_m2 = fields.Monetary(string="Unit Price/ m2")
    bsd_property_price = fields.Monetary(string="Property Price", compute="_compute_property_price", store=True)
    bsd_vat = fields.Monetary(string="Vat", compute="_compute_property_price")

    @api.depends('bsd_price_m2', 'bsd_use_area')
    def _compute_property_price(self):
        self.bsd_property_price = self.bsd_price_m2 * self.bsd_carpet_area
        self.bsd_vat = self.bsd_property_price / 10

    bsd_property_rent_price = fields.Monetary(string="Rent Price")
    bsd_property_type = fields.Selection([('1', 'Cư Dân'), ('2', 'Thương Mại')],
                                         string='Property Type',
                                         default='1')
    bsd_maintenance_cost = fields.Monetary(string="Maintenance Cost")

    @api.onchange('bsd_property_price')
    def _onchange_property_price(self):
        for each in self:
            each.bsd_maintenance_cost = each.bsd_property_price * 0.02

    bsd_property_for = fields.Selection([('sale', 'For Sale'),
                                         ('rent', 'For Rent'),
                                         ('lsb', 'For Lease')], string="Property For")
    bsd_new_or_resale = fields.Selection([('new', 'Mới'), ('resale', 'Bán Lại')], string="New Or Resale")
    # Thông tin chi tiết
    bsd_built_up_area = fields.Float(string="Built-up Area(m2)")
    bsd_carpet_area = fields.Float(string="Carpet Area(m2)")
    bsd_use_area = fields.Float(string="Khả dụng(m2)", compute='_compute_use_area', store=True)
    bsd_width = fields.Float(string="Width(m)")
    bsd_height = fields.Float(string="Height(m)")
    bsd_length = fields.Float(string="Length(m)")
    bsd_bedroom = fields.Integer(string="Bedrooms", default=1)
    bsd_bathroom = fields.Integer(string="Bathrooms", default=1)
    bsd_balconies = fields.Integer(string="Balconies")
    bsd_furnished = fields.Selection([('none', 'None'),
                                      ('semi', 'Semi Furnished'),
                                      ('full', 'Full Furnished')])
    bsd_additional_rooms = fields.Many2many('bsd.room.type', string="Additional Rooms")
    # Chi phí định kỳ

    bsd_duration_type = fields.Selection(related="bsd_project_id.bsd_duration_type")
    bsd_s_price = fields.Monetary(string="Management Fee/m2", related="bsd_project_id.bsd_s_price")
    bsd_management_fee = fields.Monetary(string="Management Fee", compute='_compute_management_fee', store=True)

    # Thực trạng căn hộ
    bsd_start_user = fields.Date(string="Ready To Move")
    bsd_property_ages = fields.Integer(string='Property Ages')
    bsd_ownership = fields.Selection([('1', 'Freehold'),
                                      ('2', 'Leasehold'),
                                      ('3', 'Co-operative Society'),
                                      ('4', 'Power of Attorney')], string="Ownership")
    bsd_description = fields.Text(string="Description")

    # Bãi đậu xe riêng
    bsd_reserved_parking = fields.Boolean(string="Reserved Parking")
    bsd_open_parking = fields.Integer(string="Open Parking")
    bsd_covered_parking = fields.Integer(string="Covered Parking")

    stage_id = fields.Many2one('bsd.account.asset.stage', string="Stage", ondelete='cascade', required=True)

    # Room nội thất
    bsd_room_detail_ids = fields.One2many('bsd.room.detail', 'bsd_unit_id', string="Room Detail")

    color = fields.Integer()

    @api.depends('bsd_room_detail_ids')
    def _compute_use_area(self):
        for each in self:
            each.bsd_use_area = sum(each.bsd_room_detail_ids.mapped('bsd_area'))

    @api.depends('bsd_s_price', 'bsd_carpet_area', 'bsd_duration_type')
    def _compute_management_fee(self):
        for each in self:
            each.bsd_management_fee = each.bsd_s_price * each.bsd_carpet_area * int(each.bsd_duration_type)

    @api.depends('name', 'bsd_project_id.bsd_code', 'bsd_block_id.bsd_code')
    def _compute_complete_name(self):
        for each in self:
            if each.bsd_block_id and each.bsd_project_id and each.bsd_floor_id:
                each.complete_name = '%s-%s,%s.%s' % (each.bsd_project_id.bsd_code,
                                                      each.bsd_block_id.bsd_code,
                                                      each.bsd_floor_id.name,
                                                      each.name)
            else:
                each.complete_name = each.name

    @api.onchange('bsd_project_id')
    def _onchange_project(self):
        res = {}
        res.update({
            'domain': {'bsd_block_id': [('bsd_project_id.id', '=', self.bsd_project_id.id)]}
        })
        return res

    @api.onchange('bsd_block_id')
    def _onchange_block(self):
        res = {}
        res.update({
            'domain': {'bsd_floor_id': [('bsd_block_id.id', '=', self.bsd_block_id.id)]}
        })
        return res

    bsd_location_id = fields.Many2one('stock.location', string="Vị trí", readonly=True)

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
        _logger.debug("create")
        _logger.debug(vals_list)
        location_id = False
        if 'bsd_floor_id' in vals_list.keys():
            location_id = self.env['bsd.real.estate.floor'].browse(vals_list['bsd_floor_id']).bsd_location_id.id
        elif 'bsd_block_id' in vals_list.keys():
            location_id = self.env['bsd.real.estate.block'].browse(vals_list['bsd_block_id']).bsd_location_id.id
        location = self.env['stock.location'].create({
            'name': vals_list['name'],
            'location_id': location_id if location_id else False,
            'usage': 'internal',
        }).id
        vals_list['bsd_location_id'] = location
        _logger.debug("create")
        _logger.debug(vals_list)
        return super(AccountAsset, self).create(vals_list)


class BsdRoomDetail(models.Model):
    _name = 'bsd.room.detail'
    _description = 'Thông tin căn phòng'

    bsd_unit_id = fields.Many2one('account.asset', string="Unit")
    name = fields.Char(string="Name")
    bsd_type = fields.Many2one('bsd.room.type', string="Loại Phòng")
    bsd_width = fields.Float(string="Rộng")
    bsd_length = fields.Float(string="Dài")
    bsd_area = fields.Float(string="Diện tích sử dụng", compute="_compute_area", store=True)

    @api.depends('bsd_width', 'bsd_length')
    def _compute_area(self):
        for each in self:
            each.bsd_area = each.bsd_width * each.bsd_length


class BsdAccountAssetStage(models.Model):
    _name = 'bsd.account.asset.stage'
    _description = 'Unit Stage'

    name = fields.Char(string="Stage")
