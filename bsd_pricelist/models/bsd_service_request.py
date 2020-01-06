# -*- coding:utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError

import logging
_logger = logging.getLogger(__name__)


class BsdServiceRequest(models.Model):
    _inherit = 'bsd.residential.service'

    def action_confirm(self):
        if self.env['res.users'].has_group('bsd_real_estate.group_user') or \
                self.env['res.users'].has_group('bsd_real_estate.group_manager'):
            pass
        else:
            raise UserError('You not manager or user')
        parking_service_id = self.env.ref('bsd_residential.parking_service').id
        if self.bsd_type_id.bsd_service_master:
            if self.bsd_type_id.id == parking_service_id:
                _logger.debug("gửi xe")
                for vehicle in self.bsd_vehicle_ids:
                    self.env['bsd.unit.service'].create({
                        'bsd_product_id': vehicle.bsd_product_id.id,
                        'bsd_product_tmpl_id': vehicle.bsd_product_id.product_tmpl_id.id,
                        'bsd_registry_service_id': self.id,
                        'bsd_start_date': fields.Date.today(),
                        'state': 'active',
                        'name': vehicle.bsd_note + ' ' + vehicle.bsd_license if vehicle.bsd_note else vehicle.bsd_license,
                        'bsd_unit_id': self.bsd_unit_id.id,
                        'bsd_residential_id': vehicle.bsd_residential_id.id,
                        'bsd_partner_id': self.bsd_partner_id.id,
                    })
            else:
                self.env['bsd.unit.service'].create({
                        'bsd_product_id': self.bsd_product_id.id,
                        'bsd_product_tmpl_id': self.bsd_product_id.product_tmpl_id.id,
                        'bsd_registry_service_id': self.id,
                        'bsd_start_date': fields.Date.today(),
                        'state': 'active',
                        'bsd_unit_id': self.bsd_unit_id.id,
                        'bsd_residential_id': self.bsd_residential_id.id,
                        'bsd_partner_id': self.bsd_partner_id.id,
                    })
        else:
            if self.bsd_address_id:
                pass
            else:
                pass
            order = self.env['sale.order'].create({
                'partner_id': self.bsd_partner_id.id,
                'bsd_request_service_id': self.id,
                'pricelist_id': 1,
                'order_line': [(0, 0, {'product_id': self.bsd_product_id.id,
                                       'product_uom_qty': 1})]
            })
            self.bsd_so_id = order.id

        self.write({'state': 'approve',
                    'bsd_confirm_user': self.env.uid,
                    'bsd_confirm_date': fields.Date.today()})