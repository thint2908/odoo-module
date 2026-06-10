from odoo.exceptions import ValidationError

from odoo import api, fields, models


class InventoryMove(models.Model):
    _name = 'inventory.move'
    _description = 'Inventory Move'

    product_id = fields.Many2one('inventory.product', string="Product ID", required=True, ondelete='cascade')
    src_location_id = fields.Many2one('inventory.location', string="Location ID", required=True, ondelete='cascade')
    dest_location_id = fields.Many2one('inventory.location', string="Destination ID", required=True, ondelete='cascade')
    quantity = fields.Float(string="Quantity", required=True)
    state = fields.Selection([
        ("draft", "Draft"),("done", "Done")
        ], string="State", default="draft", required=True)
    
    @api.constrains('quantity')
    def check_quantity(self):
        for quant in self:
            if quant.quantity <= 0:
                raise ValidationError(
                    f"Stock quantity cannot be negative(quantity:{quant.quantity})"
                )