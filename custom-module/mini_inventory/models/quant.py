from odoo import models, fields

class Quant(models.Model):
    _name = "mini_inventory.quant"
    _description = "Mini Inventory Stock Quant"
    
    product_id. fields.Many2one('mini_inventory.product', string="Product", required=True, ondelete='cascade')
    location_id = fields.Many2one('mini_inventory.location', string="Location", required=True, ondelete='cascade')
    qty = fields.Float(string="Quantity on Hand", default=0.0)