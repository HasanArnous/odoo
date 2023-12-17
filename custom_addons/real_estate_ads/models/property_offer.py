from odoo import models, fields, api
import datetime


class PropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Property Offers"

    price = fields.Float(string="Price")
    status = fields.Selection([('Accepted', 'accepted'), ('Refused', 'refused',)], string="Status")
    creation_date = fields.Date(string="Creation Date", default=datetime.datetime.today())
    partner_id = fields.Many2one('res.partner', string="Customer")
    property_id = fields.Many2one('estate.property', string="Property")
    validity = fields.Integer(string="Validity")
    deadline = fields.Date(string="Deadline", compute='_compute_deadline', inverse='_inverse_deadline')

    @api.depends('creation_date', 'validity')
    def _compute_deadline(self):
        for rec in self:
            if rec.creation_date and rec.validity:
                rec.deadline = rec.creation_date + datetime.timedelta(days=rec.validity)
            else:
                rec.deadline = False

    # It will be triggered only after saving/update the record
    def _inverse_deadline(self):
        for rec in self:
            rec.validity = (rec.deadline - rec.creation_date).days
