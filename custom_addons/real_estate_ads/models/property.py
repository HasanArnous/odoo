from odoo import fields, models, api


class Property(models.Model):
    # THE NAME & DESCRIPTION OF THE TABLE IN THE DB (MANDATORY)
    _name = "estate.property"
    _description = "Real Estate Model"

    # HERE WE ADD THE FIELDS
    # we can use something like 'readonly' and other parameters as well
    name = fields.Char(string="Name", required=True)
    description = fields.Text(string="Description", required=True)
    tag_ids = fields.Many2many("estate.property.tag", string="Tags")
    type_id = fields.Many2one("estate.property.type", string="Type")
    post_code = fields.Char(string="Post Code")
    date_availability = fields.Date(string="Available From")
    expected_price = fields.Float(string="Expected Price")
    best_offer = fields.Float(string="Best Offer")
    selling_price = fields.Float(string="Selling Price")
    bedrooms = fields.Integer(string="Bedrooms")
    living_area = fields.Integer(string="Living Area(sqm)")
    facades = fields.Integer(string="Facades")
    garage = fields.Boolean(string="Garage", default=False)
    garden = fields.Boolean(string="Garden", default=False)
    garden_area = fields.Integer(string="Garden Area")
    # SELECTION TAKE A LIST Tuples '()', not Maps/Sets '{}'
    garden_orientation = fields.Selection([('north', 'North'), ('south', 'South'),
                                           ('west', 'West'), ('east', 'East')],
                                          string="Garden Orientation", default='east')
    offer_ids = fields.One2many("estate.property.offer", "property_id", string="Offers")
    sales_id = fields.Many2one("res.users", string="Salesman")
    buyer_id = fields.Many2one("res.partner", string="Buyer")

    @api.depends('living_area', 'garden_area')
    def _compute_total_area(self):
        for rec in self:
            rec.total_area = rec.living_area + rec.garden_area

    total_area = fields.Integer(string="Total Area", compute=_compute_total_area)
    # or we can the name of the method in the compute parameter as string => compute="_compute_total_area"

    # There is also the onchange method, the onchange method will be triggered on the level of form context
    # @api.onchange('living_area', 'garden_area')
    # def _onchange_total_area(self):
    #     self.total_area = self.living_area + self.garden_area

    # Odoo will generate some fields automatically like the following:
    # id, create_date, create_uid, write_date, write_uid


class PropertyType(models.Model):
    _name = "estate.property.type"

    name = fields.Char(string="name", required=True)
    _description = "Property Type"


class PropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Property Tag"

    name = fields.Char(string="name", required=True)
