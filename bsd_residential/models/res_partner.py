# -*- coding:utf-8 -*-

from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    bsd_is_master = fields.Boolean(string="Là chủ hộ", compute='_compute_master', store=True)
    bsd_is_residential = fields.Boolean(string="Là cư dân", compute='_get_unit', store=True)
    bsd_is_tenant_off = fields.Boolean(string="Là khách thuê văn phòng", compute='_compute_tenant', store=True)
    bsd_is_tenant_mall = fields.Boolean(string="Là khách thuê TTTM", compute='_compute_tenant', store=True)
    bsd_is_tenant_res = fields.Boolean(string="Là khách thuê căn hộ", compute='_compute_tenant', store=True)
    bsd_is_owner = fields.Boolean(string="Là chủ sở hữu", compute='_compute_owner', store=True)
    bsd_owner_ids = fields.One2many('bsd.unit', 'bsd_owner_id', string="Căn hộ sở hữu", readonly=True)
    bsd_tenant_ids = fields.One2many('bsd.unit', 'bsd_tenant_id', string="Căn hộ thuê", readonly=True)
    bsd_master_ids = fields.One2many('bsd.unit', 'bsd_responsible_id', string="Chủ hộ", readonly=True)
    # bsd_residential_ids = fields.One2many('bsd.residential', 'bsd_partner_id', readonly=True, string="Cư dân")

    # @api.depends('bsd_residential_ids', 'bsd_residential_ids.state')
    # def _get_unit(self):
    #     _logger.debug("địa chỉ tạm trú")
    #     for each in self:
    #         _logger.debug(each.bsd_residential_ids)
    #         res = each.bsd_residential_ids.filtered(lambda r: r.state == 'in')
    #         _logger.debug(res)
    #         if res:
    #             each.bsd_is_residential = True
    #         else:
    #             each.bsd_is_residential = False

    @api.depends('bsd_master_ids')
    def _compute_master(self):
        for each in self:
            if each.bsd_master_ids:
                each.bsd_is_master = True
            else:
                each.bsd_is_master = False
        _logger.debug("tính lại master")

    @api.depends('bsd_owner_ids')
    def _compute_owner(self):
        for each in self:
            if each.bsd_owner_ids:
                each.bsd_is_owner = True
            else:
                each.bsd_is_owner = False
        _logger.debug("tính lại master")

    @api.depends('bsd_tenant_ids', 'bsd_tenant_ids.bsd_type')
    def _compute_tenant(self):
        for each in self:
            contract_tenancy = each.bsd_tenant_ids
            tenancy_res = contract_tenancy.filtered(lambda x: x.bsd_type == 'res')
            tenancy_off = contract_tenancy.filtered(lambda x: x.bsd_type == 'off')
            tenancy_mall = contract_tenancy.filtered(lambda x: x.bsd_type == 'mall')
            if tenancy_res:
                each.bsd_is_tenant_res = True
            else:
                each.bsd_is_tenant_res = False

            if tenancy_off:
                each.bsd_is_tenant_off = True
            else:
                each.bsd_is_tenant_off = False

            if tenancy_mall:
                each.bsd_is_tenant_mall = True
            else:
                each.bsd_is_tenant_mall = False