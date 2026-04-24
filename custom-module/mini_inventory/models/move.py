from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Move(models.Model):
    _name = "mini_inventory.move"
    _description = "Mini Inventory Stock Move"
    
    name = fields.Char(string="Description", required=True)
    product_id = fields.Many2one(
        'mini_inventory.product',
        string="Product",
        required=True,
    )
    location_src_id = fields.Many2one('mini_inventory.location', string="From location", required=True)
    location_dest_id = fields.Many2one('mini_inventory.location', string="To Location", required=True)
    qty = fields.Float(string="Quantity", required=True)
    state = fields.Selection([
        ('draft', "Draft"),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ], string="State", default='draft', required=True)
    picking_id = fields.Many2one('mini_inventory.picking', string="Picking", ondelete='cascade')
    
    date = fields.Datetime(string="Date", default=fields.Datime.now)
    
    @api.constrains('qty')
    def _check_qty_positive(self):
        for move in self:
            if move.qty <= 0:
                raise ValidationError("Quantity must be greater than 0.")

    @api.constrains('location_src_id', 'location_dest_id')
    def _check_locations_defferent(self):
        for move in self:
            if move.location_src_id == move.location_dest_id:
                raise ValidationError("Source and destinatino locations must be different.")
    