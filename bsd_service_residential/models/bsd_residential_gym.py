# -*- coding:utf-8 -*-

try:
    import qrcode
except ImportError:
    qrcode = None
try:
    import base64
except ImportError:
    base64 = None
from io import BytesIO
import uuid

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class BsdResidentialGym(models.Model):
    _name = 'bsd.residential.gym'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin', 'image.mixin']
    _description = 'Hội viên Gym'

    bsd_residential_id = fields.Many2one('bsd.residential', string="Cư dân",
                                         states={'draft': [('readonly', False)],
                                                 'active': [('readonly', True)],
                                                 'deactivate': [('readonly', True)],
                                                 'done': [('readonly', True)],
                                                 'cancel': [('readonly', True)]})
    bsd_unit_id = fields.Many2one(related='bsd_residential_id.bsd_unit_id', store=True, string="Căn hộ")
    bsd_partner_id = fields.Many2one('res.partner', string="Khách hàng",
                                     states={'draft': [('readonly', False)],
                                             'active': [('readonly', True)],
                                             'deactivate': [('readonly', True)],
                                             'done': [('readonly', True)],
                                             'cancel': [('readonly', True)]}
                                     )
    bsd_sequence = fields.Char(string="Số thứ tự", required=True, index=True, copy=False, default='New')
    name = fields.Char(string="Họ và tên", required=True,
                       states={'draft': [('readonly', False)],
                               'active': [('readonly', True)],
                               'deactivate': [('readonly', True)],
                               'done': [('readonly', True)],
                               'cancel': [('readonly', True)]}
                       )
    bsd_qr_code = fields.Binary(string="Mã QR code", readonly=True)
    bsd_birthday = fields.Date(string="Ngày sinh",
                               states={'draft': [('readonly', False)],
                                       'active': [('readonly', False)],
                                       'deactivate': [('readonly', False)],
                                       'done': [('readonly', False)],
                                       'cancel': [('readonly', True)]}
                               )
    bsd_gender = fields.Selection([('men', 'Nam'), ('women', 'Nữ')], string='Giới tính', default='men',
                                  states={'draft': [('readonly', False)],
                                          'active': [('readonly', False)],
                                          'deactivate': [('readonly', False)],
                                          'done': [('readonly', False)],
                                          'cancel': [('readonly', True)]}
                                  )
    bsd_mobile = fields.Char(string="Số điện thoại",
                             states={'draft': [('readonly', False)],
                                     'active': [('readonly', False)],
                                     'deactivate': [('readonly', False)],
                                     'done': [('readonly', False)],
                                     'cancel': [('readonly', True)]}
                             )
    bsd_email = fields.Char(string="Thư điện tử",
                            states={'draft': [('readonly', False)],
                                    'active': [('readonly', False)],
                                    'deactivate': [('readonly', False)],
                                    'done': [('readonly', False)],
                                    'cancel': [('readonly', True)]}
                            )
    bsd_note = fields.Text(string="Ghi chú")
    bsd_product_id = fields.Many2one('product.product', required=True, string="Dịch vụ",
                                     states={'draft': [('readonly', False)],
                                             'active': [('readonly', True)],
                                             'deactivate': [('readonly', True)],
                                             'done': [('readonly', True)],
                                             'cancel': [('readonly', True)]}
                                     )
    bsd_registry_date = fields.Date(string="Ngày đăng ký",
                                    states={'draft': [('readonly', False)],
                                            'active': [('readonly', True)],
                                            'deactivate': [('readonly', True)],
                                            'done': [('readonly', True)],
                                            'cancel': [('readonly', True)]}
                                    )
    bsd_user_id = fields.Many2one('res.users', string="Nhân viên tiếp nhận", default=lambda self: self.env.uid,
                                  states={'draft': [('readonly', False)],
                                          'active': [('readonly', True)],
                                          'deactivate': [('readonly', True)],
                                          'done': [('readonly', True)],
                                          'cancel': [('readonly', True)]}
                                  )
    bsd_count_so = fields.Integer("# Đơn bán", compute='_compute_so')
    state = fields.Selection([('draft', 'Nháp'),
                              ('active', 'Đang tập'),
                              ('deactivate', 'Ngưng tập'),
                              ('pause', 'Bảo lưu'),
                              ('cancel', 'Hủy')], string='Trạng thái', default="draft")
    bsd_line_ids = fields.One2many('bsd.residential.gym.line', 'bsd_residential_gym_id', string="Thời gian tập",
                                   states={'draft': [('readonly', False)],
                                           'active': [('readonly', True)],
                                           'deactivate': [('readonly', True)],
                                           'done': [('readonly', True)],
                                           'cancel': [('readonly', True)]}
                                   )
    bsd_residential_gym_pause_ids = fields.One2many('bsd.residential.gym.pause', 'bsd_residential_gym_id',
                                                    string="Bảo lưu")

    def _sync_user(self, partner):
        vals = dict(
            image_1920=partner.image_1920,
        )
        return vals

    @api.onchange('bsd_partner_id')
    def _onchange_partner(self):
        if self.bsd_partner_id:
            self.update(self._sync_user(self.bsd_partner_id))

    @api.onchange('bsd_residential_id')
    def _onchange_residential(self):
        self.name = self.bsd_residential_id.partner_id.name
        self.bsd_partner_id = self.bsd_residential_id.partner_id.id
        self.bsd_email = self.bsd_residential_id.email
        self.bsd_mobile = self.bsd_residential_id.mobile
        self.bsd_birthday = self.bsd_residential_id.bsd_birthday
        self.bsd_gender = self.bsd_residential_id.bsd_gender

    @api.depends('bsd_line_ids')
    def _compute_so(self):
        for each in self:
            so = each.bsd_line_ids.mapped('bsd_so_id')
            each.bsd_count_so = len(so)

    def view_sale_order(self):
        so = self.bsd_line_ids.mapped('bsd_so_id')
        return {
            'type': 'ir.actions.act_window',
            'name': _('Đơn bán'),
            'res_model': 'sale.order',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', so.ids)]
        }

    def _generate_access_token(self):
        return str(uuid.uuid4())

    def action_card(self):
        self.write({
            'access_token': self._generate_access_token()
        })
        url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        _logger.debug("action_card")
        _logger.debug(url)
        _logger.debug(self.access_token)
        if qrcode and base64:
            str_qrcode = url + '/service/gym/' + str(self.id) + '?access_token=' + self.access_token
            qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
            )
            qr.add_data(str_qrcode)
            qr.make(fit=True)
            img = qr.make_image()
            temp = BytesIO()
            img.save(temp, format="PNG")
            qr_image = base64.b64encode(temp.getvalue())
            self.write({'bsd_qr_code': qr_image,
                        'state': 'active'})
        else:
            raise UserError(_('Cài đặt các thư viện cần thiết tạo mã qr code'))

    def action_pause(self):
        action = self.env.ref('bsd_service_residential.bsd_wizard_gym_pause_action').read()[0]
        return action

    def action_run(self):
        action = self.env.ref('bsd_service_residential.bsd_wizard_gym_run_action').read()[0]
        return action

    def action_done(self):
        self.write({
            'state': 'deactivate',
        })

    def action_add(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _("Đơn bán"),
            'res_model': 'sale.order',
            'view_mode': 'form',
            'context': {'default_partner_id': self.bsd_partner_id.id}
        }

    def action_cancel(self):
        self.write({
            'state': 'cancel',
        })

    @api.model
    def _compute_status(self):
        _logger.debug("tính lại trạng thái record")

    @api.model
    def create(self, vals):
        if vals.get('bsd_sequence', 'New') == 'New':
            vals['bsd_sequence'] = self.env['ir.sequence'].next_by_code('bsd.residential.gym') or '/'
        _logger.debug("create gym")
        _logger.debug(vals)
        return super(BsdResidentialGym, self).create(vals)


class BsdResidentialGymLine(models.Model):
    _name = "bsd.residential.gym.line"
    _description = "Thời gian tập của hội viên Gym"
    _order = 'bsd_to_date desc'

    name = fields.Selection([('new', 'Đăng ký mới'), ('add', 'Gia hạn')], string="Loại")
    bsd_from_date = fields.Date(string="Từ ngày", required=True)
    bsd_to_date = fields.Date(string="Đến ngày", required=True)
    bsd_residential_gym_id = fields.Many2one('bsd.residential.gym', string="Hội viên")
    bsd_so_id = fields.Many2one('sale.order', string="Đơn bán", readonly=True)
    state = fields.Selection([('active', 'Còn hạn'), ('deactivate', 'Hết hạn')], default='active', string="Trạng thái")


class BsdResidentialGymPause(models.Model):
    _name = "bsd.residential.gym.pause"
    _description = "Thời gian bảo lưu của hội viên Gym"
    _rec_name = "bsd_residential_gym_id"

    bsd_residential_gym_id = fields.Many2one('bsd.residential.gym', string='Hội viên')
    bsd_reason = fields.Text(string="Lý do")
    bsd_from_date = fields.Date(string="Từ ngày")
    bsd_to_date = fields.Date(string="Đến ngày")
    state = fields.Selection([('active', 'Hiệu lực'), ('done', 'Kết thúc')], string="Trạng thái", default="active")
