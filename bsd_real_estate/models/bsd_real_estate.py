# -*- coding:utf-8 -*-

from odoo import models, fields, api, tools, _
import logging
_logger = logging.getLogger(__name__)


class BsdRealEstateProject(models.Model):
    _name = 'bsd.real.estate.project'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin', 'image.mixin']
    _description = 'Project information'

    name = fields.Char(string="Name", required=True)
    bsd_type_id = fields.Many2one('bsd.project.type', string="Type")
    bsd_code = fields.Char(string="Code", required=True, size=3, unique=True)
    bsd_manager_id = fields.Many2one('hr.employee', string="Project Manager")
    bsd_inventor_id = fields.Many2one('res.partner', string="Chủ đầu tư")
    street = fields.Char(string="Street")
    street2 = fields.Char(string="Street2")
    district = fields.Char(string="District")
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict',
                               domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')
    project_latitude = fields.Float(string='Geo Latitude', digits=(16, 5))
    project_longitude = fields.Float(string='Geo Longitude', digits=(16, 5))
    bsd_built_area = fields.Float(string="Built-up Area")
    bsd_carpet_area = fields.Float(string="Carpet Area")

    bsd_duration_type = fields.Selection([('1', '1 Tháng'),
                                          ('3', '3 Tháng'),
                                          ('6', '6 Tháng'),
                                          ('12', '12 Tháng'),
                                          ('24', '24 Tháng'),
                                          ('60', '60 Tháng')], string="Duration Type", default='1')

    bsd_s_price = fields.Monetary(string="Management Fee/m2")
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Currency", readonly=True)
    bsd_apartment = fields.Integer(string="Apartment")
    bsd_shopping_mall = fields.Integer(string="Shopping Mall")
    bsd_office = fields.Integer(string="Office/Office-tel")
    bsd_available_on = fields.Date(string="Available On")
    bsd_count_block = fields.Integer('# Block', compute='_compute_info')
    bsd_count_unit = fields.Integer('# Unit', compute='_compute_info')
    bsd_block_ids = fields.One2many('bsd.real.estate.block', 'bsd_project_id')
    bsd_warehouse_id = fields.Many2one('stock.warehouse', string="Warehouse", readonly=True)
    bsd_amenities = fields.Many2many('bsd.amenities', string="Amenities")

    bsd_area_ids = fields.One2many('bsd.project.area', 'bsd_project_id', string="Phân khu")

    _sql_constraints = [
        ('bsd_warehouse_id_unique',
         'UNIQUE(bsd_warehouse_id)',
         "Warehouse đã nằm trong dự án"),
    ]

    def _compute_info(self):
        for each in self:
            _logger.debug("Debug _compute_info")
            each.bsd_count_block = len(each.bsd_block_ids)
            each.bsd_count_unit = len(each.bsd_block_ids.mapped('bsd_floor_ids').mapped('bsd_unit_ids'))

    def block_view(self):
        domain = [('bsd_project_id.id', '=', self.id)]
        return {
            'type': 'ir.actions.act_window',
            'name': _('Block'),
            'view_mode': 'kanban,tree,form',
            'view_type': 'form',
            'res_model': 'bsd.real.estate.block',
            'domain': domain,
            'context': '{"default_bsd_project_id":%s}' % self.id,
        }

    def unit_view(self):
        domain = [('bsd_project_id.id', '=', self.id)]
        action = self.env.ref('bsd_real_estate.bsd_account_asset_action').read()[0]
        action.update({'domain': str(domain)})
        action.update({'context': "{'default_bsd_project_id':%s}" % self.id})
        return action

    @api.model
    def create(self, vals_list):
        _logger.debug("create")
        _logger.debug(vals_list)
        warehouse = self.env['stock.warehouse'].create({
            'name': vals_list['name'],
            'code': vals_list['bsd_code'],
        }).id
        vals_list['bsd_warehouse_id'] = warehouse
        _logger.debug("create")
        _logger.debug(vals_list)
        return super(BsdRealEstateProject, self).create(vals_list)
    #
    # def write(self, vals_list):
    #     for vals in vals_list:
    #         tools.image_resize_images(vals)
    #     return super(BsdRealEstateProject, self).write(vals_list)


class BsdRealEstateBlock(models.Model):
    _name = 'bsd.real.estate.block'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = 'Block information'
    _rec_name = 'complete_name'

    name = fields.Char(string="Name", required=True, unique=True)
    complete_name = fields.Char('Complete Name', compute='_compute_complete_name', store=True)
    bsd_type_id = fields.Many2one('bsd.block.type', string="Type")
    bsd_code = fields.Char(string="Code", required=True, size=4, unique=True)
    bsd_project_id = fields.Many2one('bsd.real.estate.project', ondelete="cascade", string="Project", required=True)
    bsd_inventor_id = fields.Many2one(related='bsd_project_id.bsd_inventor_id', string="Chủ đầu tư")
    bsd_area_id = fields.Many2one('bsd.project.area', string="Phân khu")
    bsd_manager_id = fields.Many2one('hr.employee', string="Block Manager")
    bsd_floor_ids = fields.One2many('bsd.real.estate.floor', 'bsd_block_id', string="Floors")
    bsd_built_area = fields.Float(string="Built-up Area")
    bsd_carpet_area = fields.Float(string="Carpet Area")
    bsd_apartment = fields.Integer(string="Apartment")
    bsd_shopping_mall = fields.Integer(string="Shopping Mall")
    bsd_office = fields.Integer(string="Office/Office-tel")
    bsd_available_on = fields.Date(string="Available On")
    bsd_count_floor = fields.Integer('# Floor', compute='_compute_floor')
    bsd_count_unit = fields.Integer('# Unit', compute='_compute_floor')
    bsd_location_id = fields.Many2one('stock.location', string="Vị trí", readonly=True)

    _sql_constraints = [
        ('bsd_location_id_unique', 'UNIQUE(bsd_location_id)', "Vị trí đã được chọn")
    ]

    @api.depends('bsd_code', 'bsd_project_id.bsd_code')
    def _compute_complete_name(self):
        for each in self:
            if each.bsd_project_id:
                each.complete_name = '%s-%s' % (each.bsd_project_id.bsd_code, each.bsd_code)
            else:
                each.complete_name = each.name

    def _compute_floor(self):
        for each in self:
            _logger.debug("Debug _compute_floor")
            each.bsd_count_floor = len(each.bsd_floor_ids)
            each.bsd_count_unit = len(each.bsd_floor_ids.mapped('bsd_unit_ids'))

    def floor_view(self):
        domain = [('bsd_block_id.id', '=', self.id)]
        return {
            'type': 'ir.actions.act_window',
            'name': _('Floor'),
            'view_mode': 'kanban,tree,form',
            'view_type': 'form',
            'res_model': 'bsd.real.estate.floor',
            'domain': domain,
            'context': '{"default_bsd_block_id":%s}' % self.id,
        }

    def unit_view(self):
        domain = [('bsd_block_id.id', '=', self.id)]
        action = self.env.ref('bsd_real_estate.bsd_account_asset_action').read()[0]
        action.update({'domain': str(domain)})
        action.update({'context': "{'default_bsd_block_id':%s}" % self.id})
        return action

    @api.model
    def create(self, vals_list):
        _logger.debug("create")
        _logger.debug(vals_list['bsd_project_id'])
        _logger.debug(vals_list)
        location = self.env['stock.location'].create({
            'name': vals_list['name'],
            'location_id': self.env['bsd.real.estate.project'].browse(vals_list['bsd_project_id']).bsd_warehouse_id.view_location_id.id,
            'usage': 'internal',
        }).id
        vals_list['bsd_location_id'] = location
        _logger.debug("create")
        _logger.debug(vals_list)
        return super(BsdRealEstateBlock, self).create(vals_list)


class BsdRealEstateFloor(models.Model):
    _name = 'bsd.real.estate.floor'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = 'Floor Information'
    _rec_name = 'complete_name'

    name = fields.Char(string="Name", required=True, unique=True)
    complete_name = fields.Char('Complete Name', compute='_compute_complete_name', store=True)
    bsd_type_id = fields.Many2one('bsd.floor.type', string="Type")
    bsd_manager_id = fields.Many2one('hr.employee', string="Floor Manager")
    bsd_block_id = fields.Many2one('bsd.real.estate.block', string="Block")
    bsd_unit_ids = fields.One2many('account.asset', 'bsd_floor_id', string="Units")
    bsd_location_id = fields.Many2one('stock.location', string="Vị trí", readonly=True)
    bsd_count_unit = fields.Integer('# Unit', compute='_compute_unit')
    bsd_built_area = fields.Float(string="Built-up Area")
    bsd_carpet_area = fields.Float(string="Carpet Area")
    bsd_apartment = fields.Integer(string="Apartment")
    bsd_shopping_mall = fields.Integer(string="Shopping Mall")
    bsd_office = fields.Integer(string="Office/Office-tel")
    bsd_available_on = fields.Date(string="Available On")

    _sql_constraints = [
        ('bsd_location_id_unique',
         'UNIQUE(bsd_location_id)',
         "Vị trí đã được chọn"),
    ]

    @api.depends('name', 'bsd_block_id.bsd_code')
    def _compute_complete_name(self):
        for each in self:
            if each.bsd_block_id:
                each.complete_name = '%s-%s,%s' % (each.bsd_block_id.bsd_project_id.bsd_code, each.bsd_block_id.bsd_code, each.name)
            else:
                each.complete_name = each.name

    def _compute_unit(self):
        for each in self:
            _logger.debug("Debug _compute_unit")
            each.bsd_count_unit = len(each.bsd_unit_ids)
    # def action_get_partner(self):
    #     action = self.env.ref('bsd_residential.bsd_wizard_registry_request_action').read()[0]
    #     _logger.debug("debug")
    #     action.update({'context': "{'action_id':%s}" % self.id})
    #     _logger.debug(action)
    #     return action

    def unit_view(self):
        domain = [('bsd_floor_id.id', '=', self.id)]
        action = self.env.ref('bsd_real_estate.bsd_account_asset_action').read()[0]
        action.update({'domain': str(domain)})
        action.update({'context': "{'default_bsd_floor_id':%s}" % self.id})
        return action

    @api.model
    def create(self, vals_list):
        _logger.debug("create")
        _logger.debug(vals_list)
        location = self.env['stock.location'].create({
            'name': vals_list['name'],
            'location_id': self.env['bsd.real.estate.block'].browse(vals_list['bsd_block_id']).bsd_location_id.id,
            'usage': 'internal',
        }).id
        vals_list['bsd_location_id'] = location
        _logger.debug("create")
        _logger.debug(vals_list)
        return super(BsdRealEstateFloor, self).create(vals_list)


# class BsdRealEstateUnit(models.Model):
#     _name = 'bsd.real.estate.unit'
#     _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin', 'image.mixin']
#     _description = 'Unit Information'
#     _rec_name = 'complete_name'
#
#     name = fields.Char(string="Name", required=True, unique=True)
#     complete_name = fields.Char('Complete Name', compute='_compute_complete_name', store=True)
#     currency_id = fields.Many2one("res.currency", string="Currency", readonly=True, required=True,
#                                   default=lambda self: self.env.company.currency_id)
#     bsd_type_id = fields.Many2one('bsd.unit.type', string="Type")
#     bsd_floor_id = fields.Many2one('bsd.real.estate.floor', string="Floor")
#     bsd_block_id = fields.Many2one('bsd.real.estate.block', string="Block")
#     bsd_project_id = fields.Many2one('bsd.real.estate.project', string="Project")
#
#     bsd_owned_id = fields.Many2one('res.partner', string="Owned")
#     bsd_responsible_id = fields.Many2one('res.partner', string="Responsible")
#
#     bsd_furnished = fields.Selection([('none', 'None'),
#                                       ('semi', 'Semi Furnished'),
#                                       ('full', 'Full Furnished')])
#     bsd_bedroom = fields.Selection([('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5+')], string="Bedrooms", default='1')
#     bsd_bathroom = fields.Selection([('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5+')], string="Bathrooms", default='1')
#     bsd_facing = fields.Selection([('1', 'Đông'),
#                                       ('2', 'Tây'),
#                                       ('3', 'Nam'),
#                                       ('4', 'Bắc'),
#                                       ('5', 'Đông Bắc'),
#                                       ('6', 'Đông Nam'),
#                                       ('7', 'Tây Bắc'),
#                                       ('8', 'Tây Nam')], string="Facing")
#     bsd_parking = fields.Selection([('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5+')], string="Parking", default='1')
#     bsd_view = fields.Many2one('bsd.unit.view', string="View")
#     bsd_usage_type = fields.Selection([('1', 'Cho thuê'), ('2', 'Cho thuê lại'), ('3', 'Cho thuê thương mại')], string="Mục Đích sử dụng")
#     bsd_flat_type = fields.Selection([('1', 'Minimart/Shophouse'),
#                                       ('2', 'Flat'),
#                                       ('3', 'Maisonette'),
#                                       ('4', 'Penhouse')]
#                                      , string="Loại căn hộ")
#
#     bsd_construction_area = fields.Float(string="Diện tích xây dựng")
#     bsd_sale_area = fields.Float(string="Diện tích bán")
#     bsd_ground_rent = fields.Monetary(string="Ground Rent")
#     bsd_price = fields.Float(string="Giá bán")
#     bsd_maintenance = fields.Monetary(string="Phí bảo trì")
#     bsd_management = fields.Monetary(string="Phí quản lý")
#     bsd_state = fields.Selection([('1','1')],string="State")
#
#     @api.depends('name', 'bsd_project_id.bsd_code', 'bsd_block_id.bsd_code')
#     def _compute_complete_name(self):
#         for each in self:
#             if each.bsd_block_id and each.bsd_project_id and each.bsd_floor_id:
#                 each.complete_name = '%s-%s,%s.%s' % (each.bsd_project_id.bsd_code,
#                                                       each.bsd_block_id.bsd_code,
#                                                       each.bsd_floor_id.name,
#                                                       each.name)
#             else:
#                 each.complete_name = each.name
#
#     @api.onchange('bsd_project_id')
#     def _onchange_project(self):
#         res = {}
#         res.update({
#             'domain': {'bsd_block_id': [('bsd_project_id.id', '=', self.bsd_project_id.id)]}
#         })
#         return res
#
#     @api.onchange('bsd_block_id')
#     def _onchange_block(self):
#         res = {}
#         res.update({
#             'domain': {'bsd_floor_id': [('bsd_block_id.id', '=', self.bsd_block_id.id)]}
#         })
#         return res
#
#
#     bsd_location_id = fields.Many2one('stock.location', string="Vị trí", readonly=True)
#
#     def view_stock_quant(self):
#         domain = [('bsd_location_id.id', '=', self.bsd_location_id.id)]
#         return {
#             'type': 'ir.actions.act_window',
#             'name': _('Thiết bị'),
#             'view_mode': 'tree,form',
#             'res_model': 'stock.production.lot',
#             'domain': domain,
#         }
#
#     _sql_constraints = [
#         ('bsd_location_id_unique',
#          'UNIQUE(bsd_location_id)',
#          "Vị trí đã được chọn"),
#     ]
#
#     @api.model
#     def create(self, vals_list):
#         _logger.debug("create")
#         _logger.debug(vals_list)
#         location_id = False
#         if 'bsd_floor_id' in vals_list.keys():
#             location_id = self.env['bsd.real.estate.floor'].browse(vals_list['bsd_floor_id']).bsd_location_id.id
#         elif 'bsd_block_id' in vals_list.keys():
#             location_id = self.env['bsd.real.estate.block'].browse(vals_list['bsd_block_id']).bsd_location_id.id
#         location = self.env['stock.location'].create({
#             'name': vals_list['name'],
#             'location_id': location_id if location_id else False,
#             'usage': 'internal',
#         }).id
#         vals_list['bsd_location_id'] = location
#         _logger.debug("create")
#         _logger.debug(vals_list)
#         return super(BsdRealEstateUnit, self).create(vals_list)


class BsdUnitView(models.Model):
    _name = 'bsd.unit.view'
    _description = 'View Unit'

    name = fields.Char(string="View")


class BsdProjectArea(models.Model):
    _name = 'bsd.project.area'
    _description = "Phân khu"

    name = fields.Char(string="Phân khu")
    bsd_project_id = fields.Many2one('bsd.real.estate.project', string="Project")











