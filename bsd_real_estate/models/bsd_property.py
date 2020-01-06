# -*- coding: utf-8 -*-

from odoo import models, fields, api


class BsdProjectType(models.Model):
    _name = 'bsd.project.type'
    _description = 'Project Type'
    _parent_name = "bsd_parent_id"
    _parent_store = True
    _rec_name = 'complete_name'
    _order = 'complete_name'

    name = fields.Char(string="Name", required=True)
    bsd_parent_id = fields.Many2one('bsd.project.type', string="Parent", index=True, ondelete='cascade')

    complete_name = fields.Char(
        'Complete Name', compute='_compute_complete_name',
        store=True)
    parent_path = fields.Char(index=True)
    child_id = fields.One2many('bsd.project.type', 'bsd_parent_id', 'Child Categories')

    @api.depends('name', 'bsd_parent_id.complete_name')
    def _compute_complete_name(self):
        for category in self:
            if category.bsd_parent_id:
                category.complete_name = '%s / %s' % (category.bsd_parent_id.complete_name, category.name)
            else:
                category.complete_name = category.name


class BsdBlockType(models.Model):
    _name = 'bsd.block.type'
    _description = 'Block Type'
    _parent_name = "bsd_parent_id"
    _parent_store = True
    _rec_name = 'complete_name'
    _order = 'complete_name'

    name = fields.Char(string="Name", required=True)
    bsd_parent_id = fields.Many2one('bsd.block.type', string="Parent", index=True, ondelete='cascade')

    complete_name = fields.Char(
        'Complete Name', compute='_compute_complete_name',
        store=True)
    parent_path = fields.Char(index=True)
    child_id = fields.One2many('bsd.block.type', 'bsd_parent_id', 'Child Categories')

    @api.depends('name', 'bsd_parent_id.complete_name')
    def _compute_complete_name(self):
        for category in self:
            if category.bsd_parent_id:
                category.complete_name = '%s / %s' % (category.bsd_parent_id.complete_name, category.name)
            else:
                category.complete_name = category.name


class BsdFloorType(models.Model):
    _name = 'bsd.floor.type'
    _description = 'Floor Type'
    _parent_name = "bsd_parent_id"
    _parent_store = True
    _rec_name = 'complete_name'
    _order = 'complete_name'

    name = fields.Char(string="Name", required=True)
    bsd_parent_id = fields.Many2one('bsd.floor.type', string="Parent", index=True, ondelete='cascade')

    complete_name = fields.Char(
        'Complete Name', compute='_compute_complete_name',
        store=True)
    parent_path = fields.Char(index=True)
    child_id = fields.One2many('bsd.floor.type', 'bsd_parent_id', 'Child Categories')

    @api.depends('name', 'bsd_parent_id.complete_name')
    def _compute_complete_name(self):
        for category in self:
            if category.bsd_parent_id:
                category.complete_name = '%s / %s' % (category.bsd_parent_id.complete_name, category.name)
            else:
                category.complete_name = category.name


class BsdUnitType(models.Model):
    _name = 'bsd.unit.category'
    _description = 'Unit Category'
    _parent_name = "bsd_parent_id"
    _parent_store = True
    _rec_name = 'complete_name'
    _order = 'complete_name'

    name = fields.Char(string="Name", required=True)
    bsd_parent_id = fields.Many2one('bsd.unit.category', string="Parent", index=True, ondelete='cascade')

    complete_name = fields.Char(
        'Complete Name', compute='_compute_complete_name',
        store=True)
    parent_path = fields.Char(index=True)
    child_id = fields.One2many('bsd.unit.category', 'bsd_parent_id', 'Child Categories')

    @api.depends('name', 'bsd_parent_id.complete_name')
    def _compute_complete_name(self):
        for category in self:
            if category.bsd_parent_id:
                category.complete_name = '%s / %s' % (category.bsd_parent_id.complete_name, category.name)
            else:
                category.complete_name = category.name


class BsdRoomType(models.Model):
    _name = 'bsd.room.type'
    _description = 'Room Type'

    name = fields.Char(string="Name", required=True)


class BsdAmenities(models.Model):
    _name = 'bsd.amenities'
    _description = "Tiên nghi"

    name = fields.Char(string="Name")
