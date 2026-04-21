from odoo import models, fields, api

class AssetManagement(models.Model):
    _name = 'asset.management'
    _description = 'Asset Management'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(string='Asset Name', required=True, tracking=True)
    serial_number = fields.Char(string='Serial Number', tracking=True)
    category_id = fields.Many2one('asset.category', string='Category', required=True, tracking=True)
    purchase_date = fields.Date(string='Purchase Date', tracking=True)
    cost = fields.Float(string='Cost', tracking=True)
    
    state = fields.Selection([
        ('draft', 'Available'),
        ('assigned', 'Assigned'),
        ('maintenance', 'Maintenance'),
        ('retired', 'Retired')
    ], string='Status', default='draft', tracking=True, required=True)
    
    assignee_id = fields.Many2one('res.users', string='Assigned To', tracking=True)
    notes = fields.Text(string='Notes')
    active = fields.Boolean(default=True, string='Active')
