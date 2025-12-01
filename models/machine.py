# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Machine(models.Model):
    _name = 'section.machine'
    _description = 'Machine'
    _order = 'name'

    name = fields.Char(string='Machine Name', required=True)
    section_id = fields.Many2one('kiosk.section', string='Section', required=True, ondelete='cascade')
    section_name = fields.Char(related='section_id.name', string='Section Name', readonly=True, store=True)
    section_location = fields.Char(related='section_id.location', string='Section Location', readonly=True, store=True)
    active = fields.Boolean(string='Active', default=True)
    created_at = fields.Datetime(string='Created At', default=fields.Datetime.now, readonly=True)
    updated_at = fields.Datetime(string='Updated At', default=fields.Datetime.now, readonly=True)

    @api.model
    def create(self, vals):
        vals['created_at'] = fields.Datetime.now()
        vals['updated_at'] = fields.Datetime.now()
        return super(Machine, self).create(vals)

    def write(self, vals):
        vals['updated_at'] = fields.Datetime.now()
        return super(Machine, self).write(vals)

