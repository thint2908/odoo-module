from odoo import api, fields, models


class InventoryProduct(models.Model):
    _name = "inventory.product"
    _description = "Inventory Product"

    name = fields.Char(required=True)
    code = fields.Char()
    active = fields.Boolean(default=True)
    cost_price = fields.Float(string='Cost price')
    qty_available = fields.Float(string="Available Quantity", compute="_compute_qty_available")
    quant_ids = fields.One2many("inventory.quant", "product_id", string="Quants")
    
    @api.depends("quant_ids.quantity", "quant_ids.location_id.usage")
    def _compute_qty_available(self):
        for product in self:
            # quants = self.env["inventory.quant"].search([
            #     ("product_id", "=", product.id),
            #     ("location_id.usage", "=", "internal")
            # ])
            
            # product.qty_available = sum(quants.mapped("quantity"), 0.0)
            internal_quants = product.quant_ids.filtered(
                lambda q: q.location_id.usage == "internal"
            )
            
            product.qty_available = sum(
                internal_quants.mapped("quantity")
            )