# -*- coding:utf-8 -*-

import logging

import binascii

from odoo import fields, http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request

from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager

import pytz
_logger = logging.getLogger(__name__)


local_tz = pytz.timezone('Asia/Bangkok')


def utc_to_local(utc_dt):
    local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
    # return local_tz.normalize(local_dt)
    return local_dt.strftime('%Y-%m-%d %H:%M')


class BsdResidential(CustomerPortal):

    @http.route(['/service/swim/<int:swim_id>'], auth='none', methods=["GET"], type='http', csrf=False, website=True)
    def swim(self, swim_id=None, access_token=None, **payload):
        try:
            swim_sudo = self._document_check_access('bsd.residential.swim', swim_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/web/login')
        if swim_sudo.state == 'draft':
            state = "Đợi cấp mã"
        elif swim_sudo.state == 'active':
            state = 'Đang hoạt động'
        elif swim_sudo.state == 'deactive':
            state = 'Ngừng hoạt động'
        elif swim_sudo.state == 'pause':
            state = 'Tạm ngưng'
        elif swim_sudo.state == 'cancel':
            state = 'Hủy'

        values = {
            'sequence': swim_sudo.bsd_sequence,
            'name': swim_sudo.name,
            'gender': 'Nam' if swim_sudo.bsd_gender == 'men' else 'Nữ',
            'birthday': swim_sudo.bsd_birthday,
            'mobile': swim_sudo.bsd_mobile,
            'product_id': swim_sudo.bsd_product_id.name,
            'state': state,
            'image': swim_sudo.image_1920,
        }
        _logger.debug(values)
        return request.render('bsd_service_residential.check_swim', values)

    @http.route(['/service/gym/<int:gym_id>'], auth='none', methods=["GET"], type='http', csrf=False, website=True)
    def gym(self, gym_id=None, access_token=None, **payload):
        try:
            gym_sudo = self._document_check_access('bsd.residential.gym', gym_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/web/login')
        if gym_sudo.state == 'draft':
            state = "Đợi cấp mã"
        elif gym_sudo.state == 'active':
            state = 'Đang hoạt động'
        elif gym_sudo.state == 'deactive':
            state = 'Ngừng hoạt động'
        elif gym_sudo.state == 'pause':
            state = 'Tạm ngưng'
        elif gym_sudo.state == 'cancel':
            state = 'Hủy'

        values = {
            'sequence': gym_sudo.bsd_sequence,
            'name': gym_sudo.name,
            'gender': 'Nam' if gym_sudo.bsd_gender == 'men' else 'Nữ',
            'birthday': gym_sudo.bsd_birthday,
            'mobile': gym_sudo.bsd_mobile,
            'product_id': gym_sudo.bsd_product_id.name,
            'state': state,
            'image': gym_sudo.image_1920,
        }
        _logger.debug(values)
        return request.render('bsd_service_residential.check_gym', values)

    @http.route(['/service/tennis/<int:tennis_id>'], auth='none', methods=["GET"], type='http', csrf=False, website=True)
    def tennis(self, tennis_id=None, access_token=None, **payload):
        try:
            tennis_sudo = self._document_check_access('bsd.residential.tennis', tennis_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/')
        if tennis_sudo.state == 'confirm':
            state = 'Đã xác nhận'
        elif tennis_sudo.state == 'done':
            state = 'Hoàn thành'
        elif tennis_sudo.state == 'cancel':
            state = 'Hủy'
        values = {
            'name': tennis_sudo.name,
            'residential_id': tennis_sudo.bsd_residential_id.name,
            'start_time': utc_to_local(tennis_sudo.bsd_start_time),
            'end_time': utc_to_local(tennis_sudo.bsd_end_time),
            'product_id': tennis_sudo.bsd_product_id.name,
            'state': state
        }
        _logger.debug(values)
        return request.render('bsd_service_residential.check_tennis', values)

    @http.route(['/service/bbq/<int:bbq_id>'], auth='none', methods=["GET"], type='http', csrf=False, website=True)
    def tennis(self, bbq_id=None, access_token=None, **payload):
        try:
            bba_sudo = self._document_check_access('bsd.residential.bbq', bbq_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/')
        if bba_sudo.state == 'confirm':
            state = 'Đã xác nhận'
        elif bba_sudo.state == 'done':
            state = 'Hoàn thành'
        elif bba_sudo.state == 'cancel':
            state = 'Hủy'
        values = {
            'name': bba_sudo.name,
            'residential_id': bba_sudo.bsd_residential_id.name,
            'start_time': utc_to_local(bba_sudo.bsd_start_time),
            'end_time': utc_to_local(bba_sudo.bsd_end_time),
            'product_id': bba_sudo.bsd_product_id.name,
            'state': state
        }
        _logger.debug(values)
        return request.render('bsd_service_residential.check_bbq', values)

