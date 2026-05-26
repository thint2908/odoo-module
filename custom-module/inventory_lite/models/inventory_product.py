from odoo import fields, models


class InventoryProduct(models.Model):
    _name = "inventory.product"
    _description = "Inventory Product"

    name = fields.Char(required=True)
    code = fields.Char()