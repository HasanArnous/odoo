from odoo import models, fields, api, _
import datetime
from odoo.exceptions import ValidationError


class PropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Property Offers"
    # _sql_constraints = [
    #     ("check_validity", "check(validity > 0)", "Deadline cannot be before or equal to the creation date"),
    # ]

    @api.depends('partner_id', 'property_id')
    def _compute_name(self):
        for rec in self:
            if rec.partner_id and rec.property_id:
                rec.name = f"{rec.property_id.name} - {rec.partner_id.name}'s Offer"
            else:
                rec.name = False

    name = fields.Char(string="description", compute='_compute_name')
    price = fields.Float(string="Price")
    status = fields.Selection([
        ('new', 'New'), ('accepted', 'Accepted'), ('refused', 'Refused',)
    ], string="Status", default='new')
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

    @api.constrains('validity')
    def _check_validity(self):
        for rec in self:
            if rec.deadline and rec.deadline <= rec.creation_date:
                raise ValidationError(_("Deadline cannot be before or equal to the creation date"))

    # Will run every day (it can be configured from the scheduled Actions)
    @api.autovacuum
    def _clean_offers(self):
        self.search([('status', '=', 'refused')]).unlink()  # => Delete the record

    def write(self, vals):
        # will print the changes..... ex. => {'price': 150000}
        print(vals)
        # get only companies
        print(self.env.cr)  # will print the current cursor ex. <odoo.sql_db.Cursor object at 0x000001FCDEDC99F0>
        print(self.env.uid)  # will print the current model id ex. 2
        print(self.env.context)  # will print the current context info
        #  ex:
        #  {
        #  'lang': 'en_US',
        #  'tz': 'Asia/Riyadh',
        #  'uid': 2,
        #  'allowed_company_ids': [1],
        #  'params': {
        #       'id': 1,
        #       'cids': 1,
        #       'menu_id': 300,
        #       'action': 358,
        #       'model':
        #       'estate.property',
        #       'view_type':
        #       'form'
        #     }
        #   }
        companies = self.env['res.partner'].search([
            ('is_company', '=', 'True'),
        ], limit=3, order='name asc')
        print(companies)  # => res.partner(14, 10, 11)
        companies_count = self.env['res.partner'].search_count([
            ('is_company', '=', 'True'),
        ])
        print(companies_count)  # => 8
        print(type(companies))  # => <class 'odoo.api.res.partner'>
        if len(companies) > 0:
            a_company = self.env['res.partner'].browse(companies[0].id)
            print(a_company)  # => res.partner(14,)
            print(a_company.name)  # => Azure Interior
            phone_numbers = companies.mapped('phone')
            print(phone_numbers)  # => ['(870)-931-0505', '(603)-996-3829', '(941)-284-4875']
            print(companies.filtered(lambda c: c.phone == "(870)-931-0505"))  # => res.partner(14,)

        result = super(PropertyOffer, self).write(vals)
        if result:
            # Setting the Status of the Property based on the Offers
            offerProperty = self.env['estate.property'].search([
                ('id', '=', self.property_id.id),
            ])
            if offerProperty:
                if (len(offerProperty.offer_ids) == 0 or
                        (offerProperty.state == 'new' and len(offerProperty.offer_ids) > 0)):
                    offerProperty.write({
                        'state': 'received'
                    })

        return result

    def unlink(self):
        # We can override the unlink method in case we need to check or remove anything else before
        # removing the record
        offer_property = self.env['estate.property'].search([
            ('id', '=', self.property_id.id),
        ])
        result = super(PropertyOffer, self).unlink()
        if result:
            if offer_property:
                if len(offer_property.offer_ids) == 0:
                    offer_property.state = 'new'
        return result

    def validate_accept_offer(self):
        offers = self.env['estate.property.offer'].search([
            ('property_id', '=', self.property_id.id),
            ('status', '=', 'accepted')
        ])
        if offers:
            raise ValidationError("You have an accepted offer already!")

    def action_accept(self):
        self.validate_accept_offer()
        self.status = 'accepted'
        for rec in self:
            rec.property_id.write({
                'selling_price': rec.price,
                'state': 'accepted'
            })

    def action_refuse(self):
        self.status = 'refused'
        accepted_offers = self.env['estate.property.offer'].search([
            ('property_id', '=', self.property_id.id),
            ('status', '=', 'accepted')
        ])
        if not accepted_offers:
            self.property_id.write({
                'state': 'received',
                'selling_price': 0
            })
