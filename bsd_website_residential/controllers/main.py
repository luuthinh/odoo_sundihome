# -*- coding:utf-8 -*-

import logging
import json
from datetime import date
from odoo import http, _
from odoo.addons.web.controllers.main import ensure_db
from odoo.addons.auth_signup.models.res_users import SignupError
from odoo.exceptions import UserError
from odoo.http import request


_logger = logging.getLogger(__name__)


class BsdResidential(http.Controller):

    @http.route('/residential/signup', auth='none', methods=["POST"], type='json', csrf=False)
    def post(self, **payload):
        qcontext = self.get_auth_signup_qcontext()
        _logger.debug("Debug post")
        _logger.debug(type(payload))
        _logger.debug(payload)
        try:
            self.do_signup(qcontext)
        except UserError as e:
            _logger.debug(type(e))
            return json.dumps({'error': e.name})
        except (SignupError, AssertionError) as e:
            _logger.debug("loi 1")
            if request.env["res.users"].sudo().search([("login", "=", qcontext.get("login"))]):
                qcontext["error"] = "Another user is already registered using this email address."
                return json.dumps({'error': "Another user is already registered using this email address."})
            else:
                _logger.debug("loi 2")
                qcontext['error'] = "Could not create a new account."
                return json.dumps({'error': "Could not create a new account."})
        return json.dumps(payload)

    def get_auth_signup_config(self):
        """retrieve the module config (which features are enabled) for the login page"""

        get_param = request.env['ir.config_parameter'].sudo().get_param
        return {
            'signup_enabled': request.env['res.users']._get_signup_invitation_scope() == 'b2c',
            'reset_password_enabled': get_param('auth_signup.reset_password') == 'True',
        }

    def get_auth_signup_qcontext(self):
        """ Shared helper returning the rendering context for signup and reset password """
        qcontext = request.params.copy()
        qcontext.update(self.get_auth_signup_config())
        _logger.debug("get_auth_signup_qcontext")
        _logger.debug(request.session)
        if not qcontext.get('token') and request.session.get('auth_signup_token'):
            qcontext['token'] = request.session.get('auth_signup_token')
        if qcontext.get('token'):
            try:
                # retrieve the user info (name, login or email) corresponding to a signup token
                token_infos = request.env['res.partner'].sudo().signup_retrieve_info(qcontext.get('token'))
                for k, v in token_infos.items():
                    qcontext.setdefault(k, v)
            except:
                qcontext['error'] = _("Invalid signup token")
                qcontext['invalid_token'] = True
        return qcontext

    def do_signup(self, qcontext):
        """ Shared helper that creates a res.partner out of a token """
        values = {key: qcontext.get(key) for key in ('login', 'name', 'password')}
        if not values:
            raise UserError(_("The form was not properly filled in."))
        if values.get('password') != qcontext.get('confirm_password'):
            raise UserError(_("Passwords do not match; please retype them."))
        supported_langs = [lang['code'] for lang in request.env['res.lang'].sudo().search_read([], ['code'])]
        if request.lang in supported_langs:
            values['lang'] = request.lang
        self._signup_with_values(qcontext.get('token'), values)
        request.env.cr.commit()

    def _signup_with_values(self, token, values):
        db, login, password = request.env['res.users'].sudo().signup(values, token)
        request.env.cr.commit()     # as authenticate will use its own cursor we need to commit the current transaction
        uid = request.session.authenticate(db, login, password)
        if not uid:
            raise SignupError(_('Authentication Failed.'))

    @http.route('/registry', auth='user', website=True)
    def registry(self, **kw):
        Registry = http.request.env['bsd.registry.request']
        User = http.request.env.user
        Unit = http.request.env['account.asset'].search([])
        methods = Registry.fields_get('bsd_method')['bsd_method']['selection']
        _logger.debug(methods)
        # if kw and request.httprequest.method == 'POST':
        #     _logger.debug("odoo post")
        #     _logger.debug(kw)
        #     return request.redirect('/my/home')
        values = {
            'bsd_partner_id': User.partner_id.name,
            'bsd_method': methods,
            'bsd_unit_id': Unit,
            'error': {},
            'error_message': [],
            'page_name': 'my_registry'}
        _logger.debug(values)
        return http.request.render('bsd_website_residential.registry', values)

    @http.route('/registry/post', auth='user', type='json')
    def registry_post(self, **values):
        _logger.debug("odoo post")

        values.update({'bsd_partner_id': http.request.env.user.partner_id.id})
        values.update({'bsd_send_user': http.request.env.user.id})
        values.update({'bsd_unit_id': int(values.pop('bsd_unit_id', 0))})
        values.update({'bsd_send_date': date.today()})

        _logger.debug(values)
        registry = http.request.env['bsd.registry.request'].sudo().create(values)
        registry.action_send()
        return {'registry': registry.id}

    @http.route('/registry/success', auth='user', type='http', website=True)
    def registry_success(self, **values):

        return http.request.render('bsd_website_residential.registry_success')

    @http.route('/registry/residential', auth='user', type='json')
    def get_residential(self, **values):
        _logger.debug('get_residential')
        _logger.debug(values)
        domain = [('state', '=', 'in')]
        if 'bsd_unit_id' in values.keys():
            domain.append(('bsd_unit_id', '=', values['bsd_unit_id']))
        residential = request.env['bsd.residential'].search(domain)
        _logger.debug(residential)
        result = []
        for res in residential:
            temp = {}
            temp.update({
                'id': res.id,
                'name': res.name.sudo().name,
                'bsd_relationship_id': res.bsd_relationship_id.id,
            })
            result.append(temp)
        return result

    @http.route('/registry/relationship', auth='user', type='json', website=True)
    def get_relationship(self, **values):
        return http.request.env['bsd.residential.relationship'].search([]).name_get()

    @http.route('/service', auth='user', website=True)
    def service(self, **kw):
        Service = http.request.env['bsd.residential.service.type']
        User = request.env.user
        Units = http.request.env['account.asset'].search([])
        is_master = User.partner_id.bsd_is_master
        _logger.debug(is_master)
        if is_master:
            types = Service.search([])
        else:
            types = Service.search([('bsd_service_master', '=', False)])
        bsd_address_id = User.partner_id.bsd_temp_address
        values = {
            'bsd_partner_id': User.partner_id,
            'bsd_type_id': types,
            'bsd_unit_id': Units,
            'bsd_address_id': bsd_address_id,
            'page_name': 'my_service',
            'error': {},
            'error_message': [],
        }
        _logger.debug(values)
        return http.request.render('bsd_website_residential.service', values)

    @http.route('/service/type', auth='user', type='json', website=True)
    def service_type(self, **values):
        _logger.debug("post type")
        _logger.debug(values)
        service_type = request.env['bsd.residential.service.type'].browse(values['bsd_type_id'])
        id_product_tmpl = service_type.bsd_product_tmpl_id.sudo().id
        attribute_line_ids = request.env['product.template.attribute.value'].sudo().search([('product_tmpl_id', '=', id_product_tmpl)])
        _logger.debug(attribute_line_ids)

        result = []
        for att in attribute_line_ids:
            temp = {}
            temp.update({
                'id': att.id,
                'attribute_id': att.attribute_id.name_get(),
                'name': att.name,
                'product_tmpl_id': id_product_tmpl,
            })
            result.append(temp)
        return result

    @http.route('/service/parking', auth='user', type='json')
    def service_parking(self,**kw):
        # _logger.debug("parking")
        # _logger.debug(request.env.ref('bsd_residential.parking_service').id)
        return {'parking_service': request.env.ref('bsd_residential.parking_service').id}

    @http.route('/service/unit', auth='user', type='json')
    def service_unit(self,**kw):
        unit = http.request.env['account.asset'].search([]).name_get()
        return {'unit': unit}

    @http.route('/service/post', auth='user', type='json')
    def service_post(self, **values):
        _logger.debug("service post")
        values.update({'bsd_partner_id': http.request.env.user.partner_id.id})
        values.update({'bsd_send_user': http.request.env.user.id})
        values.update({'bsd_send_date': date.today()})

        _logger.debug(values)
        service = http.request.env['bsd.residential.service'].sudo().create(values)
        service.action_send()
        return {'service': service.id}


