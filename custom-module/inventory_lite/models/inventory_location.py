from odoo import fields, models


class InventoryLocation(models.Model):
    _name = "inventory.location"
    _description = "Inventory Location"

    name = fields.Char(string="Location Name", required=True)
    usage = fields.Selection([
        ('internal', "Internal"),
        ('vendor', 'Vendor'),
        ('customer', 'Customer'),
        ('inventory', 'Inventory'),
    ], string="Location type", required=True, default='internal')