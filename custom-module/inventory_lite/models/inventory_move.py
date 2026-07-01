from odoo.exceptions import ValidationError

from odoo import api, fields, models


class InventoryMove(models.Model):
    _name = 'inventory.move'
    _description = 'Inventory Move'

    name = fields.Char(default="New", readonly=True, string="Reference", required=True, copy=False)
    product_id = fields.Many2one('inventory.product', string="Product ID", required=True, ondelete='cascade')
    source_location_id = fields.Many2one('inventory.location', string="Location ID", required=True, ondelete='cascade')
    dest_location_id = fields.Many2one('inventory.location', string="Destination ID", required=True, ondelete='cascade')
    quantity = fields.Float(string="Quantity", required=True)
    state = fields.Selection([
        ("draft", "Draft"),("done", "Done")
        ], string="State", default="draft", required=True)
    
    picking_id = fields.Many2one('inventory.picking', string="Picking", ondelete="cascade")
    
    @api.constrains('quantity')
    def check_quantity(self):
        for move in self:
            if move.quantity <= 0:
                raise ValidationError(
                    "Quantity must be greater than 0."
                )
                
    @api.constrains("source_location_id", "dest_location_id")
    def _check_loctions(self):
        for move in self:
            if move.source_location_id == move.dest_location_id:
                raise ValidationError("Source Location and Destination Location must be different.")
            
            source_usage = move.source_location_id.usage
            dest_usage = move.dest_location_id.usage
            
            if source_usage in ["vendor", "customer"] and dest_usage in ["vendor", "customer"]:
                raise ValidationError("Source and Destinatino Locations can not Vendor or Customer")
                
    @api.model
    def create(self, vals):
        if vals.get("name", "New") == "New":
            vals["name"] = self.env["ir.sequence"].next_by_code(
                "inventory.move"
            ) or "New"
        return super().create(vals)
                
                
    # ACTION 
    def action_done(self):
        for move in self:
            
            # make sure done one time
            if move.state == "done":
                continue
            
            # finding quant source
            source_quant = self.env["inventory.quant"].search(
                [
                    ("product_id", "=", move.product_id.id),
                    ("location_id", "=", move.source_location_id.id)
                ],
                limit = 1
            )
            
            # check quant is exists
            if not source_quant:
                raise ValidationError("Source stock does not exist")
            
            #check quant quantity enough
            if source_quant.quantity < move.quantity:
                raise ValidationError(f"Not enough stock. Available: {source_quant.quantity}")

            # minus stock source
            source_quant.quantity -= move.quantity
            
            # find destination quant
            dest_quant = self.env["inventory.quant"].search(
                [
                    ("product_id", "=", move.product_id.id),
                    ("location_id", "=", move.dest_location_id.id)
                ],
                limit = 1
            )
            
            # if dest not exist, create new one
            if not dest_quant:
                dest_quant = self.env["inventory.quant"].create(
                    {
                        "product_id": move.product_id.id,
                        "location_id": move.dest_location_id.id,
                        "quantity": 0,
                    }
                )
                
            # add quantity to dest_quant
            dest_quant.quantity += move.quantity
            
            # mark state is done
            move.state = "done"