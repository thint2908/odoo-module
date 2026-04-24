from odoo import models, fields, api

class Product(models.Model):
    _name = "mini_inventory.product"
    _description = "Mini Inventory Product"
    
    name = fields.Char(string="Product Name", required=True)
    code = fields.Char(string="SKU Code", required=True)
    uom = fields.Selection([
        ('unit', 'Unit'),
        ('kg', 'Kilogram'),
        ('liter', 'Liter'),
        ('box', 'Box'),
    ], string="Unit of Measure", default='unit', required=True)
    cost_price = fields.Float(string="Cost of Product")
    qty_on_hand = fields.Float(string="Quantity on hand", compute="_compute_qty_on_hand", store=False)
    location_qty_ids = fields.One2many('mini.stock.quant', 'product_id', string="stock by warehouse")
    
    @api.depends("location_qty_ids.qty")
    def _compute_qty_on_hand(self):
        for product in self:
            product.qty_on_hand = sum(product.location_qty_ids.mapped("qty"))