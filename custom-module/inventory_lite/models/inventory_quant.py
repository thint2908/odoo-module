from odoo.exceptions import ValidationError

from odoo import api, fields, models


class InventoryQuant(models.Model):
    _name="inventory.quant"
    _description = "Inventory Quant"
    
    _sql_constraints = [
        (
            'unique_product_location',
            'UNIQUE(product_id, location_id)',
            "A quant for this product and location already exists."
        )
    ] 

    product_id = fields.Many2one('inventory.product', string="Product", required=True,ondelete='cascade')
    location_id = fields.Many2one('inventory.location', string="Location", required=True,ondelete='cascade')
    quantity = fields.Float(string="Quantity Product")
    
    
    @api.constrains('quantity')
    def check_quantity_not_negative(self):
        for quant in self:
            if quant.quantity < 0:
                raise ValidationError(
                    f"Stock quantity cannot be negative(quantity:{quant.quantity})"
                )