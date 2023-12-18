from odoo import models, fields, api, _
import datetime
from odoo.exceptions import ValidationError


class PropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Property Offers"
    _sql_constraints = [
        ("check_validity", "check(validity > 0)", "Deadline cannot be before or equal to the creation date"),
    ]

    price = fields.Float(string="Price")
    status = fields.Selection([('Accepted', 'accepted'), ('Refused', 'refused',)], string="Status")
    creation_date = fields.Date(string="Creation Date")
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
            if rec.deadline and rec.creation_date:
                rec.validity = (rec.deadline - rec.creation_date).days
            else:
                rec.validity = False

    @api.model_create_multi
    def create(self, vals):
        for rec in vals:
            if not rec.get('creation_date'):
                rec['creation_date'] = fields.Date.today()
        return super(PropertyOffer, self).create(vals)

    # @api.constrains('validity')
    # def _check_validity(self):
    #     for rec in self:
    #         if rec.deadline and rec.deadline <= rec.creation_date:
    #             raise ValidationError(_("Deadline cannot be before or equal to the creation date"))

    # Will run every day (it can be configured from the scheduled Actions)
    @api.autovacuum
    def _clean_offers(self):
        self.search([('status', '=', 'refused')]).unlink()
