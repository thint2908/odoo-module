from odoo import models, fields, api
from datetime import date

class TodoTask(models.Model):
    _name = 'todo.task'
    _description = 'Todo Task'

    name = fields.Char(string='Task Name', required=True)
    description = fields.Html(string='Description')
    is_done = fields.Boolean(string='Is Done', default=False)
    created_at = fields.Datetime(
        string='Created At', 
        default=lambda self: fields.Datetime.now(),
        readonly=True
    )
    due_date = fields.Date(string='Due Date')
    is_overdue = fields.Boolean(compute='_compute_is_overdue', string='Is Overdue')

    @api.depends('due_date', 'is_done')
    def _compute_is_overdue(self):
        today = date.today()
        for record in self:
            if record.due_date and record.due_date < today and not record.is_done:
                record.is_overdue = True
            else:
                record.is_overdue = False