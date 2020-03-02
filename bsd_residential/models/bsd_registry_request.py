# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
from odoo.exceptions import ValidationError
_logger = logging.getLogger(__name__)


class BsdRegistryRequest(models.Model):
    _name = 'bsd.registry.request'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = "Mẫu đăng ký thành viên"

    name = fields.Char(string="Phiếu đăng ký", required=True, index=True, copy=False, default='New', tracking=1)
    bsd_method = fields.Selection(selection='_method_choice', string="Loại phiếu", required=True,
                                  states={'draft': [('readonly', False)],
                                          'waiting': [('readonly', True)],
                                          'refuse': [('readonly', True)],
                                          'approve': [('readonly', True)]}, tracking=2)
    bsd_residential_id = fields.Many2one('bsd.residential', string="Chủ Hộ", states={'draft': [('readonly', False)],
                                          'waiting': [('readonly', True)],
                                          'refuse': [('readonly', True)],
                                          'approve': [('readonly', True)]}, tracking=3)
    bsd_is_multi_unit = fields.Boolean(string="Multi?", default=False,
                                       states={'draft': [('readonly', False)],
                                               'waiting': [('readonly', True)],
                                               'refuse': [('readonly', True)],
                                               'approve': [('readonly', True)]})
    bsd_unit_id = fields.Many2one('bsd.unit', string="Unit",
                               states={'draft': [('readonly', False)],
                                       'waiting': [('readonly', True)],
                                       'refuse': [('readonly', True)],
                                       'approve': [('readonly', True)]}, tracking=4)
    bsd_multi_unit_ids = fields.One2many('bsd.registry.request.unit', 'bsd_registry_request_id', string="Multi Unit")
    bsd_send_date = fields.Date(string="Ngày tạo", default=fields.Date.today(),
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
    state = fields.Selection([('draft', 'Nháp'),
                              ('waiting', 'Chờ duyệt'),
                              ('refuse', 'Từ chối'),
                              ('approve', 'Duyệt')], default='draft', tracking=8, copy=False, string="Trạng thái")
    bsd_send_user = fields.Many2one('res.users', 'Người lập phiếu', default=lambda self: self.env.uid, readonly=True, tracking=9)
    bsd_confirm_user = fields.Many2one('res.users', 'Người duyệt', readonly=True, tracking=10)

    bsd_note = fields.Text(string="Lý do từ chối", states={'waiting': [('readonly', False)]}, tracking=11)

    bsd_count_renew = fields.Integer(string='Lần chỉnh sửa', readonly=True)
    bsd_is_address = fields.Boolean(string="Cư trú")

    bsd_registry_card_count = fields.Integer('Đăng ký thẻ', compute='_compute_count_card')

    def _compute_count_card(self):
        for each in self:
            registry_card = each.env['bsd.registry.card'].search([('bsd_registry_request_id', '=', each.id)])
            each.bsd_registry_card_count = len(registry_card)

    def view_card(self):
        registry_card = self.env['bsd.registry.card'].search([('bsd_registry_request_id', '=', self.id)], limit=1)
        return {
            'name': _('Đăng ký thẻ'),
            'res_model': 'bsd.registry.card',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'context': {'default_bsd_registry_request_id': self.id},
            'res_id': registry_card.id
        }

    @api.constrains('bsd_line_ids')
    def check_line(self):
        if self.bsd_method == 'new_host':
            if len(self.bsd_line_ids) > 1:
                raise ValidationError("Đăng ký chủ hộ chỉ 1 người")

    @api.model
    def _method_choice(self):
        _logger.debug("method choice")
        _logger.debug(self.env.user)
        choices = [('create', 'Thêm thành viên'),
                   # ('delete', 'Xóa thành viên'),
                   # ('host', 'Đăng ký thay đổi chủ hộ'),
                   # ('relationship', 'Thay đổi quan hệ với chủ hộ')
                   ]
        if self.env['res.users'].has_group('bsd_residential.group_user') or \
                self.env['res.users'].has_group('bsd_residential.group_manager'):
            choices += [('new_host', 'Đăng ký chủ hộ mới')]
        return choices

    @api.onchange('bsd_method', 'bsd_residential_id', 'bsd_unit_id')
    def _onchange_unit(self):
        res = {}
        self.bsd_is_multi_unit = False
        if self.bsd_method == 'new_host':
            self.bsd_residential_id = None
            return {'domain': {'bsd_unit_id': [('bsd_responsible_id', '=', False)],
                               'bsd_multi_unit_ids': [('bsd_responsible_id', '=', False)]}}
        elif self.bsd_method == 'renew':
            return {'domain': {'bsd_multi_unit_ids': [('bsd_responsible_id', '=', self.bsd_residential_id.id)],
                               'bsd_unit_id': [('bsd_responsible_id', '=', self.bsd_residential_id.id)]}}
        else:
            if self.bsd_residential_id:
                res.update({
                    'domain': {'bsd_unit_id': [('bsd_responsible_id.id', '=', self.bsd_residential_id.id)]}
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
        action = self.env.ref('bsd_residential.bsd_wizard_request_refuse_action').read()[0]
        _logger.debug("debug")
        action.update({'context': "{'action_id':%s}" % self.id})
        _logger.debug(action)
        return action

    def _check_cmnd(self):
        cmnd_user = self.bsd_line_ids.mapped('cmnd')
        if len(cmnd_user) > 1:
            _logger.debug(cmnd_user)
            if not len(cmnd_user) == len(set(cmnd_user)):
                raise UserError('Phiếu đăng ký có cmnd trùng nhau')
        return cmnd_user

    def _action_new_host(self):
        if len(self.bsd_line_ids) != 1:
            raise UserError("Đăng ký chủ hộ chỉ 1 người")
        residential_old = self.env['bsd.residential'].search([('bsd_cmnd', 'in', self._check_cmnd())])
        if residential_old:
            self.bsd_unit_id.bsd_responsible_id = residential_old.id
            if self.bsd_is_address:
                residential_old.write({
                    'bsd_history_ids': [(0, 0, {'bsd_unit_id': self.bsd_multi_unit_ids[0].bsd_unit_id.id if self.bsd_is_multi_unit and self.bsd_multi_unit_ids else self.bsd_unit_id.id ,
                                                'bsd_date_move_on': fields.Date.today(),
                                                'bsd_relationship_id': self.bsd_line_ids[0].relationship_id.id
                                                })],
                })
            self.bsd_line_ids[0].write({'bsd_residential_id': residential_old.id})
        else:
            residential_new = self.env['bsd.residential'].create({
                'name': self.bsd_line_ids[0].name,
                'bsd_code': '-',
                'bsd_cmnd': self.bsd_line_ids[0].cmnd,
                'bsd_cmnd_date': self.bsd_line_ids[0].cmnd_date,
                'bsd_cmnd_state': self.bsd_line_ids[0].cmnd_state,
                'bsd_birthday': self.bsd_line_ids[0].birthday,
                'bsd_gender': self.bsd_line_ids[0].gender,
                'vat': self.bsd_line_ids[0].vat,
                'email': self.bsd_line_ids[0].email,
                'mobile': self.bsd_line_ids[0].mobile,
                'partner_id': self.bsd_line_ids[0].bsd_partner_id.id if self.bsd_line_ids[0].bsd_partner_id else False
            })
            self.bsd_unit_id.bsd_responsible_id = residential_new.id

            if self.bsd_is_address:
                residential_new.write({
                    'bsd_history_ids': [(0, 0, {'bsd_unit_id': self.bsd_multi_unit_ids[0].bsd_unit_id.id if self.bsd_is_multi_unit and self.bsd_multi_unit_ids else self.bsd_unit_id.id ,
                                                'bsd_date_move_on': fields.Date.today(),
                                                'bsd_relationship_id': self.bsd_line_ids[0].relationship_id.id
                                                })],
                })

            self.bsd_line_ids[0].write({'bsd_residential_id': residential_new.id})

    def _action_create(self):
        residential_old = self.env['bsd.residential'].search([('bsd_cmnd', 'in', self._check_cmnd())])
        line_residential = self.bsd_line_ids.filtered(lambda x: x.cmnd in residential_old.mapped('bsd_cmnd'))
        for line in line_residential:
            residential_old.write({
                'bsd_history_ids': [(0, 0, {'bsd_unit_id': self.bsd_unit_id.id,
                                            'bsd_date_move_on': fields.Date.today(),
                                            'bsd_relationship_id': line.relationship_id.id
                                            })],
            })
            line.write({'bsd_residential_id': residential_old.id})
        line_no_residential = self.bsd_line_ids.filtered(lambda x: x.cmnd not in residential_old.mapped('bsd_cmnd'))
        for line in line_no_residential:
            residential_new = self.env['bsd.residential'].create({
                'name': line.name,
                'bsd_code': '-',
                'bsd_cmnd': line.cmnd,
                'bsd_cmnd_date': line.cmnd_date,
                'bsd_cmnd_state': line.cmnd_state,
                'bsd_birthday': line.birthday,
                'bsd_gender': line.gender,
                'vat': line.vat,
                'email': line.email,
                'mobile': line.mobile,
                'partner_id': line.bsd_partner_id.id if line.bsd_partner_id else False,
                'bsd_history_ids': [(0, 0, {'bsd_unit_id': self.bsd_unit_id.id,
                                            'bsd_date_move_on': fields.Date.today(),
                                            'bsd_relationship_id': line.relationship_id.id
                                            })],
            })
            line.write({'bsd_residential_id': residential_new.id})

    def action_confirm(self):
        if self.env['res.users'].has_group('bsd_residential.group_user') or \
                self.env['res.users'].has_group('bsd_residential.group_manager'):
            pass
        else:
            raise UserError('Bạn không có quyền trong module quản lý cư dân')
        if self.bsd_method == 'new_host':
            self._action_new_host()
        if self.bsd_method == 'create':
            self._action_create()
        _logger.debug("cấp thẻ")
        # tạo đơn cấp thẻ
        lines = self.bsd_line_ids.filtered(lambda l: l.bsd_create_card)
        if lines:
            if self.bsd_method == 'create':
                residential = self.bsd_residential_id
                unit = self.bsd_unit_id
            elif self.bsd_method == 'new_host':
                residential = self.env['bsd.residential'].search([('bsd_cmnd', '=', lines.cmnd)])
                if self.bsd_is_multi_unit:
                    unit = self.bsd_multi_unit_ids[0]
                else:
                    unit = self.bsd_unit_id
            values = []
            for line in lines:
                values.append((0, 0, {'bsd_residential_id': line.bsd_residential_id.id}))
            self.env['bsd.registry.card'].create({
                'bsd_residential_id': residential.id,
                'bsd_unit_id': unit.id,
                'bsd_type_card': 'res',
                'bsd_request': 'new',
                'bsd_registry_request_id': self.id,
                'state': 'confirm',
                'bsd_line_ids': values,
                'bsd_confirm_user': self.env.uid,
                'bsd_confirm_date': fields.Date.today()

            })

        self.write({'state': 'approve',
                    'bsd_confirm_user': self.env.uid,
                    'bsd_confirm_date': fields.Date.today()})

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            _logger.debug("create new")
            vals['name'] = self.env['ir.sequence'].next_by_code('bsd.registry.request') or '/'
        return super(BsdRegistryRequest, self).create(vals)


class BsdRegistryRequestLine(models.Model):
    _name = 'bsd.registry.request.line'

    bsd_registry_request_id = fields.Many2one('bsd.registry.request', string='Phiếu đăng ký')
    bsd_partner_id = fields.Many2one('res.partner', string="Khách hàng")
    name = fields.Char(string="Họ tên", required=True)
    birthday = fields.Date(string="Ngày sinh", required=True)
    gender = fields.Selection([('men', 'Nam'), ('women', 'Nữ')], string='Giới tính', default='men')
    cmnd = fields.Char(string="CMND", required=True, size=12)
    cmnd_date = fields.Date(string="Ngày cấp", required=True)
    cmnd_state = fields.Char(string="Nơi cấp", required=True)
    vat = fields.Char(string='MS thuế')
    email = fields.Char(string="Email")
    mobile = fields.Char(string="Số ĐT")
    relationship_id = fields.Many2one('bsd.residential.relationship', string="Quan hệ chủ hộ")
    bsd_method = fields.Selection([('create', 'Thêm thành viên'), ('new_host', 'Đăng ký chủ hộ')])
    bsd_create_card = fields.Boolean(string="Cấp thẻ")
    bsd_residential_id = fields.Many2one('bsd.residential', string="Cư dân")

    @api.onchange('bsd_partner_id')
    def onchange_partner(self):
        self.email = self.bsd_partner_id.email
        self.mobile = self.bsd_partner_id.mobile
        self.name = self.bsd_partner_id.name


class BsdRegistryRequestResidential(models.Model):
    _name = 'bsd.registry.request.unit'
    _order = "sequence,id"
    bsd_registry_request_id = fields.Many2one('bsd.registry.request')
    bsd_unit_id = fields.Many2one('bsd.unit', string="Unit")
    sequence = fields.Integer(string="Thứ tự")
