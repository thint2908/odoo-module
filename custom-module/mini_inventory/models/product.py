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
    cost_price = fields.Float(string="Cost Price")

    # qty_on_hand is NOT stored as a plain number.
    # It is computed by summing all quant records for this product.
    # store=True means Odoo caches the result in the DB column so
    # list views and searches are fast — but it is recomputed
    # automatically whenever any related quant.qty changes.
    qty_on_hand = fields.Float(
        string="Quantity on Hand",
        compute="_compute_qty_on_hand",
        store=True,
    )

    # One product can exist in multiple locations.
    # location_qty_ids gives us those per-location quant records.
    # 'product_id' is the field on mini_inventory.quant that points back here.
    location_qty_ids = fields.One2many(
        'mini_inventory.quant',
        'product_id',
        string="Stock by Location",
    )

    # api.depends tells Odoo: "whenever quant.qty changes for any quant
    # linked to this product, rerun this method."
    @api.depends('location_qty_ids.qty')
    def _compute_qty_on_hand(self):
        for product in self:
            # mapped() is a shorthand to extract a list of field values
            # from a recordset: equivalent to [q.qty for q in product.location_qty_ids]
            product.qty_on_hand = sum(product.location_qty_ids.mapped('qty'))