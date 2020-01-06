# -*- coding:utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class BsdRegistryRequest(models.Model):
    _name = 'bsd.registry.request'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = "Mẫu đăng ký thành viên"

    name = fields.Char(string="Request", required=True, index=True, copy=False, default='New', tracking=1)
    bsd_method = fields.Selection(selection='_method_choice', string="Phương Thức", required=True,
                                  states={'draft': [('readonly', False)],
                                          'waiting': [('readonly', True)],
                                          'refuse': [('readonly', True)],
                                          'approve': [('readonly', True)]}, tracking=2)
    bsd_partner_id = fields.Many2one('res.partner', string="Chủ Hộ", states={'draft': [('readonly', False)],
                                          'waiting': [('readonly', True)],
                                          'refuse': [('readonly', True)],
                                          'approve': [('readonly', True)]}, tracking=3)
    bsd_is_multi_unit = fields.Boolean(string="Multi?", default=False,
                                       states={'draft': [('readonly', False)],
                                               'waiting': [('readonly', True)],
                                               'refuse': [('readonly', True)],
                                               'approve': [('readonly', True)]})
    bsd_unit_id = fields.Many2one('account.asset', string="Unit",
                               states={'draft': [('readonly', False)],
                                       'waiting': [('readonly', True)],
                                       'refuse': [('readonly', True)],
                                       'approve': [('readonly', True)]}, tracking=4)
    bsd_multi_unit_ids = fields.Many2many('account.asset', string="Multi Unit")
    bsd_send_date = fields.Date(string="Ngày gửi", default=fields.Date.today(),
                                states={'draft': [('readonly', False)],
                                        'waiting': [('readonly', True)],
                                        'refuse': [('readonly', True)],
                                        'approve': [('readonly', True)]}, tracking=5)
    bsd_confirm_date = fields.Date(string="Ngày duyệt", readonly=True, tracking=6)
    bsd_line_ids = fields.One2many('bsd.registry.request.line', 'bsd_registry_request_id', string="Cư dân mới",
                                   states={'draft': [('readonly', False)],
                                           'waiting': [('readonly', True)],
                                           'refuse': [('readonly', True)],
                                           'approve': [('readonly', True)]}, tracking=7)
    active = fields.Boolean(default=True)
    state = fields.Selection([('draft', 'Tạo yêu cầu'),
                              ('waiting', 'chờ duyệt'),
                              ('refuse', 'từ chối'),
                              ('approve', 'chấp nhận')], default='draft', tracking=8)
    bsd_send_user = fields.Many2one('res.users', 'Người lập phiếu', default=lambda self: self.env.uid, readonly=True, tracking=9)
    bsd_confirm_user = fields.Many2one('res.users', 'Người duyệt', readonly=True, tracking=10)

    bsd_note = fields.Text(string="Lý do từ chối", states={'waiting': [('readonly', False)]}, tracking=11)
    bsd_note2 = fields.Text(string="Địa chỉ tạm trú", readonly=True)
    bsd_residential_ids = fields.One2many('bsd.registry.request.residential', 'bsd_registry_request_id', string="Cư dân tạm trú", tracking=12)

    bsd_count_renew = fields.Integer(string='Lần chỉnh sửa', readonly=True)
    bsd_is_address = fields.Boolean(string="Địa chỉ tạm trú")

    @api.model
    def _method_choice(self):
        _logger.debug("method choice")
        _logger.debug(self.env.user)
        choices = [('create', 'Thêm thành viên'),
                   ('delete', 'Xóa thành viên'),
                   ('host', 'Đăng ký thay đổi chủ hộ'),
                   ('relationship', 'Thay đổi quan hệ với chủ hộ')]
        if self.env['res.users'].has_group('bsd_real_estate.group_user') or \
                self.env['res.users'].has_group('bsd_real_estate.group_manager'):
            choices += [('new_host', 'Đăng ký chủ hộ mới'), ('renew', 'Thu hồi căn hộ')]
        return choices

    @api.onchange('bsd_method', 'bsd_partner_id', 'bsd_unit_id')
    def _onchange_unit(self):
        res = {}
        self.bsd_is_multi_unit = False
        if self.bsd_method == 'new_host':
            self.bsd_partner_id = None
            return {'domain': {'bsd_unit_id': [('bsd_responsible_id', '=', False)],
                               'bsd_multi_unit_ids': [('bsd_responsible_id', '=', False)]}}
        elif self.bsd_method == 'renew':
            return {'domain': {'bsd_multi_unit_ids': [('bsd_responsible_id', '=', self.bsd_partner_id.id)],
                               'bsd_unit_id': [('bsd_responsible_id', '=', self.bsd_partner_id.id)]}}
        else:
            if self.bsd_partner_id:
                res.update({
                    'domain': {'bsd_unit_id': [('bsd_responsible_id.id', '=', self.bsd_partner_id.id)]}
                })
            _logger.debug("get unit")
            _logger.debug(res)
            return res

    @api.onchange('bsd_is_multi_unit')
    def _onchange_is_multi_unit(self):
        self.bsd_unit_id = False
        self.bsd_multi_unit_ids = False

    def action_renew(self):
        self.bsd_count_renew += 1
        if self.bsd_count_renew > 5:
            raise UserError("Quá số lần chỉnh sửa cho phép")
        else:
            self.write({
                'state': 'draft',
                'bsd_confirm_date': False,
                'bsd_confirm_user': False,
                'bsd_note': False,
            })

    def action_send(self):
        self.write({'state': 'waiting'})

    def action_refuse(self):
        if self.bsd_note:
            self.write({'state': 'refuse',
                        'bsd_confirm_user': self.env.uid,
                        'bsd_confirm_date': fields.Date.today()})
        else:
            raise UserError("Bạn cần ghi lý do từ chối đơn ")

    def _action_new_host(self):
        if len(self.bsd_line_ids) != 1:
            raise UserError("Đăng ký chủ hộ chỉ 1 người")
        elif self.bsd_unit_id.bsd_responsible_id:
            raise UserError("Căn hộ đã có chủ hộ")
        elif self.env['res.partner'].search([('bsd_cmnd', '=', self.bsd_line_ids.cmnd)]) and not self.bsd_line_ids.bsd_partner_id:
            raise UserError("Số CMND đã được sử dụng")
        elif self.env['res.users'].search([('login', '=', self.bsd_line_ids.email)]) and not self.bsd_line_ids.bsd_partner_id:
            raise UserError("Email đã có người dùng")
        elif self.bsd_line_ids.bsd_partner_id:
            partner = self.env['res.partner'].search([('bsd_cmnd', '=', self.bsd_line_ids.cmnd)])
            # if partner.bsd_partner_id or partner.is_master:
            #     residential = self.env['bsd.residential'].search([('name.id', '=', partner.id)])
            #     residential.write({
            #         'bsd_unit_id': self.bsd_unit_id.id
            #     })
            if self.bsd_is_multi_unit:
                for unit in self.bsd_multi_unit_ids:
                    # partner.write({
                    #     'bsd_is_master': True
                    # })
                    unit.bsd_responsible_id = partner.id
                    self.env['bsd.residential.responsible.history'].create({
                        'name': partner.name,
                        'bsd_unit_id': unit.id,
                        'bsd_cmnd': partner.bsd_cmnd,
                        'bsd_from_date': fields.Date.today(),
                    })
            else:
                self.bsd_unit_id.bsd_responsible_id = partner.id
                # partner.write({
                #     'bsd_is_master': True
                # })

                self.env['bsd.residential.responsible.history'].create({
                    'name': partner.name,
                    'bsd_unit_id': self.bsd_unit_id.id,
                    'bsd_cmnd': partner.bsd_cmnd,
                    'bsd_from_date': fields.Date.today(),
                })
            if self.bsd_is_address:
                if self.env['bsd.residential'].search([('name.id', '=', partner.id), ('state', '=', 'in')]):
                    raise UserError("người đăng ký đã có địa chỉ tạm trú")
                if self.bsd_multi_unit_ids:
                    self.env['bsd.residential'].create({
                        'bsd_unit_id': self.bsd_multi_unit_ids[0].id,
                        'name': partner.id,
                        'bsd_date_move_on': fields.Date.today(),
                        'bsd_relationship_id': self.bsd_line_ids[0].relationship_id.id,
                    })
                if self.bsd_unit_id:
                    self.env['bsd.residential'].create({
                        'bsd_unit_id': self.bsd_unit_id.id,
                        'name': partner.id,
                        'bsd_date_move_on': fields.Date.today(),
                        'bsd_relationship_id': self.bsd_line_ids[0].relationship_id.id,
                    })
        else:
            user = self.env['res.users'].sudo().create({
                    'name': self.bsd_line_ids.name,
                    'login': self.bsd_line_ids.email,
                    'password': '123456',
                    'sel_groups_1_8_9': 8,
            })
            user.partner_id.write({
                    'bsd_birthday': self.bsd_line_ids.birthday,
                    'bsd_cmnd': self.bsd_line_ids.cmnd,
                    'vat': self.bsd_line_ids.vat,
                    'function': self.bsd_line_ids.function,
                    'email': self.bsd_line_ids.email,
                    'mobile': self.bsd_line_ids.mobile,
                    # 'bsd_is_master': True,
                })

            if self.bsd_is_address:
                if self.bsd_unit_id:
                    self.env['bsd.residential'].create({
                        'bsd_unit_id': self.bsd_unit_id.id,
                        'name': user.partner_id.id,
                        'bsd_date_move_on': fields.Date.today(),
                        'bsd_relationship_id': self.bsd_line_ids[0].relationship_id.id,
                    })
                if self.bsd_multi_unit_ids:
                    self.env['bsd.residential'].create({
                        'bsd_unit_id': self.bsd_multi_unit_ids[0].id,
                        'name': user.partner_id.id,
                        'bsd_date_move_on': fields.Date.today(),
                        'bsd_relationship_id': self.bsd_line_ids[0].relationship_id.id,
                    })

            if self.bsd_is_multi_unit:
                for unit in self.bsd_multi_unit_ids:
                    unit.bsd_responsible_id = user.partner_id.id
                    self.env['bsd.residential.responsible.history'].create({
                        'name': user.partner_id.name,
                        'bsd_unit_id': unit.id,
                        'bsd_cmnd': user.partner_id.bsd_cmnd,
                        'bsd_from_date': fields.Date.today(),
                    })
            else:
                self.bsd_unit_id.bsd_responsible_id = user.partner_id.id
                self.env['bsd.residential.responsible.history'].create({
                    'name': user.partner_id.name,
                    'bsd_unit_id': self.bsd_unit_id.id,
                    'bsd_cmnd': user.partner_id.bsd_cmnd,
                    'bsd_from_date': fields.Date.today(),
                })

    def _action_create(self):
        cmnd_user = self.bsd_line_ids.mapped('cmnd')
        partner = self.env['res.partner'].search([('bsd_cmnd', 'in', cmnd_user)])
        cmnd = partner.filtered(lambda r: r.bsd_temp_address).mapped('bsd_cmnd')
        if cmnd:
            raise UserError('Số chứng minh đã là cư dân {}'.format(cmnd))
        else:
            partner_ids = partner.filtered(lambda r: not r.bsd_temp_address)
            for new_person in partner_ids:
                residential = self.env['bsd.residential'].create({
                        'bsd_unit_id': self.bsd_unit_id.id,
                        'name': new_person.id,
                        'bsd_date_move_on': fields.Date.today(),
                        'bsd_relationship_id': self.bsd_line_ids.filtered(lambda x: x.cmnd == new_person.bsd_cmnd).relationship_id.id,
                })
        cmnd_partner = partner.mapped('bsd_cmnd')
        cmnd_no_partner = list(set(cmnd_user) - set(cmnd_partner))
        user_need_create = self.bsd_line_ids.filtered(lambda x: x.cmnd in cmnd_no_partner)
        for user_create in user_need_create:
            user = self.env['res.users'].sudo().create({
                'name': user_create.name,
                'login': user_create.email,
                'password': '123456',
                'sel_groups_1_8_9': 8,
            })
            user.partner_id.write({
                'bsd_birthday': user_create.birthday,
                'bsd_cmnd': user_create.cmnd,
                'vat': user_create.vat,
                'function': user_create.function,
                'email': user_create.email,
                'mobile': user_create.mobile,
            })
            residential = self.env['bsd.residential'].create({
                'bsd_unit_id': self.bsd_unit_id.id,
                'name': user.partner_id.id,
                'bsd_date_move_on': fields.Date.today(),
                'bsd_relationship_id': user_create.relationship_id.id,
            })

    def _action_delete(self):
        for res in self.bsd_residential_ids:
            res.bsd_residential_id.write({
                'state': 'out',
                'bsd_date_move_out': fields.Date.today(),
            })

    def _action_change_host(self):
        if len(self.bsd_line_ids) != 1:
            raise UserError("Đăng ký chủ hộ chỉ 1 người")
        elif self.env['res.partner'].search([('bsd_cmnd', '=', self.bsd_line_ids.cmnd)]) and not self.bsd_line_ids.bsd_partner_id:
            raise UserError("Số CMND đã được sử dụng")
        elif self.env['res.users'].search([('login', '=', self.bsd_line_ids.email)]) and not self.bsd_line_ids.bsd_partner_id:
            raise UserError("Email đã có người dùng")
        elif self.bsd_line_ids.bsd_partner_id:
            partner = self.env['res.partner'].search([('bsd_cmnd', '=', self.bsd_line_ids.cmnd)])
            # if partner.bsd_partner_id or partner.is_master:
            #     residential = self.env['bsd.residential'].search([('name.id', '=', partner.id)])
            #     residential.write({
            #         'bsd_unit_id': self.bsd_unit_id.id
            #     })
            self.bsd_unit_id.bsd_responsible_id = partner.id
            old = self.env['bsd.residential.responsible.history'].search([('bsd_cmnd', '=', self.bsd_partner_id.bsd_cmnd)])
            old.write({'bsd_to_date': fields.Date.today()})
            self.env['bsd.residential.responsible.history'].create({
                'name': partner.name,
                'bsd_unit_id': self.bsd_unit_id.id,
                'bsd_cmnd': partner.bsd_cmnd,
                'bsd_from_date': fields.Date.today(),
            })
        else:
            user = self.env['res.users'].sudo().create({
                    'name': self.bsd_line_ids.name,
                    'login': self.bsd_line_ids.email,
                    'password': '123456',
                    'sel_groups_1_8_9': 8,
            })
            self.bsd_unit_id.bsd_responsible_id = user.partner_id.id
            user.partner_id.write({
                    'bsd_birthday': self.bsd_line_ids.birthday,
                    'bsd_cmnd': self.bsd_line_ids.cmnd,
                    'vat': self.bsd_line_ids.vat,
                    'function': self.bsd_line_ids.function,
                    'email': self.bsd_line_ids.email,
                    'mobile': self.bsd_line_ids.mobile,
                    # 'bsd_is_master': True,
                })
            residential = self.env['bsd.residential'].create({
                    'bsd_unit_id': self.bsd_unit_id.id,
                    'name': user.partner_id.id,
                    'bsd_date_move_on': fields.Date.today(),
                    'bsd_relationship_id': self.bsd_line_ids.relationship_id.id,
            })
            old = self.env['bsd.residential.responsible.history'].search([('bsd_cmnd', '=', self.bsd_partner_id.bsd_cmnd)])
            old.write({'bsd_to_date': fields.Date.today()})
            self.env['bsd.residential.responsible.history'].create({
                'name': user.partner_id.name,
                'bsd_unit_id': self.bsd_unit_id.id,
                'bsd_cmnd': user.partner_id.bsd_cmnd,
                'bsd_from_date': fields.Date.today(),
            })

    def _action_change_relationship(self):
        for res in self.bsd_residential_ids:
            res.bsd_residential_id.write({
                'bsd_relationship_id': res.bsd_relationship_id.id,
            })

    def _action_renew(self):
        if self.bsd_is_multi_unit:
            for unit in self.bsd_multi_unit_ids:
                unit.bsd_responsible_id = False
                old = self.env['bsd.residential.responsible.history'].search([('bsd_cmnd', '=', self.bsd_partner_id.bsd_cmnd), ('bsd_unit_id', '=', unit.id)])
                old.write({'bsd_to_date': fields.Date.today()})
        else:
            self.bsd_unit_id.bsd_responsible_id = False
            old = self.env['bsd.residential.responsible.history'].search([('bsd_cmnd', '=', self.bsd_partner_id.bsd_cmnd), ('bsd_unit_id', '=', self.bsd_unit_id.id)])
            old.write({'bsd_to_date': fields.Date.today()})

    def action_confirm(self):
        if self.env['res.users'].has_group('bsd_real_estate.group_user') or \
                self.env['res.users'].has_group('bsd_real_estate.group_manager'):
            pass
        else:
            raise UserError('You not manager or user')
        if self.bsd_method == 'new_host':
            self._action_new_host()
        if self.bsd_method == 'create':
            self._action_create()
        if self.bsd_method == 'host':
            self._action_change_host()
        if self.bsd_method == 'renew':
            self._action_renew()
        if self.bsd_method == 'delete':
            self._action_delete()
        if self.bsd_method == 'relationship':
            self._action_change_relationship()

        self.write({'state': 'approve',
                    'bsd_confirm_user': self.env.uid,
                    'bsd_confirm_date': fields.Date.today()})

    def action_get_partner(self):
        action = self.env.ref('bsd_residential.bsd_wizard_registry_request_action').read()[0]
        _logger.debug("debug")
        action.update({'context': "{'action_id':%s}" % self.id})
        _logger.debug(action)
        return action

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            _logger.debug("create new")
            vals['name'] = self.env['ir.sequence'].next_by_code('bsd.registry.request') or '/'
        return super(BsdRegistryRequest, self).create(vals)


class BsdRegistryRequestLine(models.Model):
    _name = 'bsd.registry.request.line'

    bsd_registry_request_id = fields.Many2one('bsd.registry.request')
    bsd_partner_id = fields.Many2one('res.partner', string="Cư dân")
    name = fields.Char(string="Name", required=True)
    birthday = fields.Date(string="Birthday")
    cmnd = fields.Char(string="CMND", required=True)
    vat = fields.Char(string='Tax ID')
    function = fields.Char(string='Job Position')
    email = fields.Char(string="Email", required=True)
    mobile = fields.Char(string="Mobile")
    relationship_id = fields.Many2one('bsd.residential.relationship', string="Quan hệ chủ hộ")

    @api.onchange('bsd_partner_id')
    def _onchange_partner(self):
        self.name = self.bsd_partner_id.name
        self.birthday = self.bsd_partner_id.bsd_birthday
        self.cmnd = self.bsd_partner_id.bsd_cmnd
        self.vat = self.bsd_partner_id.vat
        self.function = self.bsd_partner_id.function
        self.email = self.bsd_partner_id.email
        self.mobile = self.bsd_partner_id.mobile


class BsdRegistryRequestResidential(models.Model):
    _name = 'bsd.registry.request.residential'
    _description = 'Thông tin cư dân trong căn hộ'

    bsd_registry_request_id = fields.Many2one('bsd.registry.request')
    bsd_residential_id = fields.Many2one('bsd.residential', string="Cư dân")
    bsd_relationship_id = fields.Many2one('bsd.residential.relationship', string="Quan hệ chủ hộ")
    bsd_unit_id = fields.Many2one('account.asset', string="Unit")

    @api.onchange('bsd_unit_id')
    def _get_residential(self):
        _logger.debug("_get_residential")
        res = {}
        res.update({
            'domain': {'bsd_residential_id': [('bsd_unit_id.id', '=', self.bsd_unit_id.id), ('state', '=', 'in')]}
        })
        _logger.debug(res)
        return res

    @api.onchange('bsd_residential_id')
    def _get_relationship(self):
        self.bsd_relationship_id = self.bsd_residential_id.bsd_relationship_id.id
