from odoo import models, fields

class Location(models.Model):
    _name = "mini_inventory.location"
    _description = "Mini Inventory Location"
    
    name = fields.Char(string="Location Name", required=True)
    code = fields.Char(string="Location Code", required=True)
    location_type = fields.Selection([
        ("internal", "Internal"),
        ('supplier', 'Supplier'),
        ('customer', 'Customer'),
        ('virtual', 'Virtual'),
    ], string="Location Type", required=True, default='internal')
    active = fields.Boolean(default=True)
    