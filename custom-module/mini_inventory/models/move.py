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
        # ondelete='restrict': prevent deleting a product that has moves
        ondelete='restrict',
    )
    location_src_id = fields.Many2one(
        'mini_inventory.location',
        string="From Location",
        required=True,
    )
    location_dest_id = fields.Many2one(
        'mini_inventory.location',
        string="To Location",
        required=True,
    )
    qty = fields.Float(string="Quantity", required=True, default=1.0)

    # State machine:
    #   draft      → move is planned but not yet executed
    #   done       → move has been validated; stock has been updated
    #   cancelled  → move was cancelled; no stock impact
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ], string="State", default='draft', required=True)

    # Many2one back to the picking that owns this move.
    # cascade: if the picking is deleted, delete its moves too.
    picking_id = fields.Many2one(
        'mini_inventory.picking',
        string="Picking",
        ondelete='cascade',
    )
    date = fields.Datetime(string="Date", default=fields.Datetime.now)

    # uom mirrors the product's unit for display convenience
    uom = fields.Selection(
        related='product_id.uom',
        string="Unit",
        readonly=True,
    )

    # --- Constraints ---

    @api.constrains('qty')
    def _check_qty_positive(self):
        for move in self:
            if move.qty <= 0:
                raise ValidationError("Quantity must be greater than 0.")

    @api.constrains('location_src_id', 'location_dest_id')
    def _check_locations_different(self):
        for move in self:
            if move.location_src_id == move.location_dest_id:
                raise ValidationError(
                    "Source and destination locations must be different."
                )

    # --- onchange helpers (UX only, not saved until user saves the form) ---

    @api.onchange('product_id')
    def _onchange_product_id(self):
        """Auto-fill description when product is selected."""
        if self.product_id:
            self.name = self.product_id.name