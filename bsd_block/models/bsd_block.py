# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)


class BsdAmenities(models.Model):
    _name = 'bsd.amenities'
    _description = "Tiên nghi"

    name = fields.Char(string="Name")


class BsdProject(models.Model):
    _name = 'bsd.project'
    _description = 'Dự án'

    name = fields.Char(string="Dự án", required=True)
    bsd_code = fields.Char(string="Mã dự án", required=True)
    bsd_inventor_id = fields.Many2one('res.partner', string="Chủ đầu tư")
    bsd_partner_id = fields.Many2one('res.partner', string="Người đại diện")
    bsd_address = fields.Text(string="Địa chỉ")


class BsdBlockFee(models.Model):
    _name = 'bsd.block.fee'
    _description = 'Các loại phí tòa nhà'
    _rec_name = 'bsd_type'

    bsd_block_id = fields.Many2one('bsd.block', string="Tòa nhà")
    bsd_type = fields.Selection([('res', 'Căn hộ'), ('off', 'Văn Phòng'), ('mall', 'TTTM')], string="Loại unit",
                                defaule='res')

    bsd_product_ids = fields.Many2many('product.product', string='Phí định kỳ', required=True,
                                       domain=[('product_tmpl_id.bsd_type', '=', 'fee')])


class BsdBlock(models.Model):
    _name = 'bsd.block'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']
    _description = 'Thông tin tòa nhà'

    name = fields.Char(string="Tòa nhà", required=True, unique=True)
    bsd_code = fields.Char(string="Mã tòa nhà", required=True, size=7)
    bsd_type_id = fields.Many2one('bsd.block.type', string="Phân loại")
    bsd_project_id = fields.Many2one('bsd.project', string="Dự án", required=True)
    bsd_manager_id = fields.Many2one('hr.employee', string="Nhân viên quản lý")
    bsd_available_on = fields.Date(string="Ngày đưa vào sử dụng")
    bsd_fee_ids = fields.One2many('bsd.block.fee', 'bsd_block_id', string="Phí định kỳ")

    # Thông tin chi tiết
    bsd_height = fields.Integer(string='Chiều cao')
    bsd_int_employee = fields.Integer(string='Số lượng nhân viên')
    bsd_total_floor = fields.Integer(string='Tổng số tầng')
    bsd_total_b_floor = fields.Integer(string='Tổng số tầng hầm')
    bsd_s_b_floor = fields.Float(string='Diện tích tầng hầm sử dụng')
    bsd_floor_mall = fields.Integer(string='Tổng số tầng TTTM')
    bsd_s_floor_mall = fields.Float(string='Tổng diện tích cho thuê TTTM')
    bsd_floor_off = fields.Integer(string='Tổng số tầng cho thuê VP')
    bsd_s_floor_off = fields.Float(string='Tổng diện tích cho thuê VP')
    bsd_floor_res = fields.Integer(string='Tổng số tầng căn hộ')
    bsd_apartment = fields.Integer(string="Số căn hộ")
    bsd_parking_motor = fields.Integer(string="số lượng vị trí giữ xe máy")
    bsd_parking_car = fields.Integer(string="Số lượng vị trí giữ xe ô tô")
    bsd_thang_may = fields.Integer(string='Số lượng thang máy')

    bsd_warehouse_id = fields.Many2one('stock.warehouse', string="Kho", readonly=True)
    bsd_amenities_ids = fields.Many2many('bsd.amenities', string="Tiện ích nội khu")
    bsd_floor_ids = fields.One2many('bsd.floor','bsd_block_id', string="Tầng")
    bsd_area_ids = fields.Many2many('bsd.area', string="Khu vực")

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
        return super(BsdBlock, self).create(vals_list)

    def action_update_fee(self):
        units = self.env['bsd.unit'].search([('bsd_block_id', '=', self.id)])
        res_units = units.filtered(lambda x: x.bsd_type == 'res')
        res_fee = self.bsd_fee_ids.filtered(lambda x: x.bsd_type == 'res')
        res_product = set(res_fee.bsd_product_ids.ids)
        for unit in res_units:
            list_product = set()
            if unit.bsd_unit_fee_ids:
                list_product = set(unit.bsd_unit_fee_ids.mapped('bsd_product_id').ids)
            product_diffs = res_product.difference(list_product)
            for product in product_diffs:
                unit.write({
                    'bsd_unit_fee_ids': [(0, 0, {'bsd_product_id': product})]
                })


class BsdBlockType(models.Model):
    _name = 'bsd.block.type'
    _description = 'Danh mục tòa nhà'
    _parent_name = "bsd_parent_id"
    _parent_store = True
    _rec_name = 'complete_name'
    _order = 'complete_name'

    name = fields.Char(string="Tên", required=True)
    bsd_parent_id = fields.Many2one('bsd.block.type', string="Danh mục cha", index=True, ondelete='cascade')

    complete_name = fields.Char(
        'Tên hiện thị', compute='_compute_complete_name',
        store=True)
    parent_path = fields.Char(index=True)
    child_id = fields.One2many('bsd.block.type', 'bsd_parent_id', 'Danh mục con')

    @api.depends('name', 'bsd_parent_id.complete_name')
    def _compute_complete_name(self):
        for category in self:
            if category.bsd_parent_id:
                category.complete_name = '%s / %s' % (category.bsd_parent_id.complete_name, category.name)
            else:
                category.complete_name = category.name


class BsdArea(models.Model):
    _name = 'bsd.area'
    _description = 'Thông tin khu vực'

    name = fields.Char(string="Khu vực", required=True)