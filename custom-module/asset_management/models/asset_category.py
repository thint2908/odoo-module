from odoo import models, fields

class AssetCategory(models.Model):
    _name = 'asset.category'
    _description = 'Asset Category'
    _order = 'name'

    name = fields.Char(string='Category Name', required=True)
    description = fields.Text(string='Description')
    active = fields.Boolean(default=True, string='Active')
    asset_ids = fields.One2many('asset.management', 'category_id', string='Assets')
