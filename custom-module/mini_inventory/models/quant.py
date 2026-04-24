from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Quant(models.Model):
    _name = "mini_inventory.quant"
    _description = "Mini Inventory Stock Quant"
    # Each (product, location) pair should appear only once.
    # _sql_constraints enforces this at the database level.
    _sql_constraints = [
        (
            'unique_product_location',
            'UNIQUE(product_id, location_id)',
            'A quant for this product in this location already exists.'
        )
    ]

    product_id = fields.Many2one(
        'mini_inventory.product',
        string="Product",
        required=True,
        # cascade: if the product is deleted, delete its quants too
        ondelete='cascade',
    )
    location_id = fields.Many2one(
        'mini_inventory.location',
        string="Location",
        required=True,
        ondelete='cascade',
        # Only internal locations should hold physical stock
        domain=[('location_type', '=', 'internal')],
    )
    qty = fields.Float(string="Quantity on Hand", default=0.0)

    @api.constrains('qty')
    def _check_qty_not_negative(self):
        for quant in self:
            if quant.qty < 0:
                raise ValidationError(
                    f"Stock for '{quant.product_id.name}' at "
                    f"'{quant.location_id.name}' cannot be negative."
                )