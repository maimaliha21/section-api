# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Section(models.Model):
    _name = 'kiosk.section'
    _description = 'Section'
    _order = 'name'

    name = fields.Char(string='Section Name', required=True)
    section_id = fields.Char(string='Section ID', required=True, index=True)
    location = fields.Char(string='Location', required=True)
    active = fields.Boolean(string='Active', default=True)
    created_at = fields.Datetime(string='Created At', default=fields.Datetime.now, readonly=True)
    updated_at = fields.Datetime(string='Updated At', default=fields.Datetime.now, readonly=True)
    
    # One2many relation to machines
    machine_ids = fields.One2many('section.machine', 'section_id', string='Machines')

    _sql_constraints = [
        ('section_id_unique', 'unique(section_id)', 'Section ID must be unique!'),
    ]

    @api.model
    def create(self, vals):
        vals['created_at'] = fields.Datetime.now()
        vals['updated_at'] = fields.Datetime.now()
        return super(Section, self).create(vals)

    def write(self, vals):
        vals['updated_at'] = fields.Datetime.now()
        return super(Section, self).write(vals)

