# # -*- conding:utf-8 -*-
#
# from odoo import models, fields, api
#
#
# class BsdWizardCreateFee(models.Model):
#     _name = 'bsd.wizard.create.fee'
#     _description = 'Cập nhật các loại phí cho unit'
#
#     def _get_block(self):
#         block = self.env['bsd.block'].browse(self._context('active_id'))
#         return block
#
#     bsd_block_id = fields.Many2one('bsd.block', string="Tòa nhà", default=_get_block)
