from odoo import fields, models


class InventoryProduct(models.Model):
    _name = "inventory.product"
    _description = "Inventory Product"

    name = fields.Char(required=True)
    code = fields.Char()
    active = fields.Boolean(default=True)
    cost_price = fields.Float(string='Cost price')
    qty_available = fields.Float(string="Available Quantity", compute="_compute_qty_available")
    
    
    