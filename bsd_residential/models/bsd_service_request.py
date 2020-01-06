# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import logging
_logger = logging.getLogger(__name__)


class BsdResidentialServiceType(models.Model):
    _name = 'bsd.residential.service.type'
    _description = 'Service Type'

    name = fields.Char(string='Name', required=True)
    bsd_product_tmpl_id = fields.Many2one('product.template', string="Service", domain=[('type', '=', 'service')])
    bsd_description = fields.Html(string="Mô tả")
    bsd_service_master = fields.Boolean("Service Chủ Hộ ?")


class BsdResidentialService(models.Model):
    _name = 'bsd.residential.service'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = 'Register Service'

    name = fields.Char(string="Service", required=True, index=True, copy=False, default='New')
    bsd_type_id = fields.Many2one('bsd.residential.service.type', string="Dịch vụ",states={'draft': [('readonly', False)],
                                          'waiting': [('readonly', True)],
                                          'refuse': [('readonly', True)],
                                          'approve': [('readonly', True)]})
    bsd_description = fields.Html(string="Description", related='bsd_type_id.bsd_description')
    bsd_partner_id = fields.Many2one('res.partner', string="Cư Dân",states={'draft': [('readonly', False)],
                                          'waiting': [('readonly', True)],
                                          'refuse': [('readonly', True)],
                                          'approve': [('readonly', True)]})
    bsd_is_master = fields.Boolean(related='bsd_partner_id.bsd_is_master', string="Là Chủ Hộ")
    bsd_address_id = fields.Many2one(related='bsd_partner_id.bsd_temp_address', string='Address', readonly=True)
    bsd_unit_id = fields.Many2one('account.asset', string="Căn hộ")
    bsd_send_date = fields.Date(string="Ngày gửi", default=fields.Date.today(), states={'draft': [('readonly', False)],
                                          'waiting': [('readonly', True)],
                                          'refuse': [('readonly', True)],
                                          'approve': [('readonly', True)]})
    bsd_confirm_date = fields.Date(string="Ngày duyệt", readonly=True)
    active = fields.Boolean(default=True)
    state = fields.Selection([('draft', 'Tạo yêu cầu'),
                              ('waiting', 'chờ duyệt'),
                              ('refuse', 'từ chối'),
                              ('approve', 'chấp nhận')], default='draft')
    bsd_send_user = fields.Many2one('res.users', 'Người lập phiếu', default=lambda self: self.env.uid, readonly=True)
    bsd_confirm_user = fields.Many2one('res.users', 'Người duyệt', readonly=True)

    bsd_note = fields.Text(string="Lý do từ chối", states={'waiting': [('readonly', False)]})
    # bsd_from_date = fields.Date(string="From Date", required=True)
    # bsd_to_date = fields.Date(string="To Date", required=True)
    bsd_attribute_ids = fields.Many2many('product.template.attribute.value', string='Attribute',
                                         states={'draft': [('readonly', False)],
                                          'waiting': [('readonly', True)],
                                          'refuse': [('readonly', True)],
                                          'approve': [('readonly', True)]})
    bsd_product_id = fields.Many2one('product.product', string="Product", compute='_get_product')
    bsd_vehicle_ids = fields.One2many('bsd.residential.vehicle', 'bsd_service_id', string="Bảng kê phương tiện")
    bsd_product_tmpl_id = fields.Many2one(related='bsd_type_id.bsd_product_tmpl_id')
    bsd_so_id = fields.Many2one('sale.order', string="Sale order", readonly=True)
    # bsd_residential_id = fields.Many2one('bsd.residential', string="Cư dân")

    @api.onchange('bsd_partner_id')
    def _onchange_partner(self):
        res = {}
        if not self.bsd_partner_id.bsd_is_master:

            _logger.debug("onchange partner")
            res.update({
                'domain': {'bsd_type_id': [('bsd_service_master', '=', False)]}
            })
            self.bsd_unit_id = False
            _logger.debug(res)
        else:
            _logger.debug("onchange 2")
            res.update({
                'domain': {'bsd_type_id': [],
                           'bsd_unit_id': [('bsd_responsible_id.id', '=', self.bsd_partner_id.id)]}
            })
            _logger.debug(res)
        return res

    @api.onchange('bsd_type_id')
    def _onchange_service_type(self):
        res = {}
        _logger.debug("onchange type")
        res.update({
            'domain': {'bsd_attribute_ids': [('product_tmpl_id.id', '=', self.bsd_type_id.bsd_product_tmpl_id.id)]}
        })
        return res

    @api.constrains('bsd_attribute_ids')
    def _check_valid_values(self):
        for attr in self.bsd_attribute_ids:
            pass

    @api.depends('bsd_attribute_ids', 'bsd_type_id')
    def _get_product(self):
        self.bsd_product_id = False
        product = self.env['product.product'].search([('product_tmpl_id', '=', self.bsd_type_id.bsd_product_tmpl_id.id)])
        _logger.debug(product)
        for item in product:
            _logger.debug("attribute")
            _logger.debug(item.product_template_attribute_value_ids.ids)
            _logger.debug(self.bsd_attribute_ids.ids)
            if set(item.product_template_attribute_value_ids.ids) == set(self.bsd_attribute_ids.ids):
                self.bsd_product_id = item.id

    def action_send(self):
        self.write({'state': 'waiting'})

    def action_refuse(self):
        if self.bsd_note:
            self.write({'state': 'refuse',
                        'bsd_confirm_user': self.env.uid,
                        'bsd_confirm_date': fields.Date.today()})
        else:
            raise UserError("Bạn cần ghi lý do từ chối đơn ")

    def action_confirm(self):
        self.write({'state': 'approve',
                    'bsd_confirm_user': self.env.uid,
                    'bsd_confirm_date': fields.Date.today()})

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('bsd.residential.service') or '/'
        return super(BsdResidentialService, self).create(vals)
