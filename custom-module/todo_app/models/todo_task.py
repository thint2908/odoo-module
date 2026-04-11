from odoo import models, fields, api
from datetime import date

class TodoTask(models.Model):
    # _inherit = ['mail.thread', 'mail.activity.mixin']
    _name = 'todo.task'
    _description = 'Todo Task'

    name = fields.Char(string='Task Name', required=True, tracking=True)
    description = fields.Html(string='Description', tracking= True)
    is_done = fields.Boolean(string='Is Done', default=False, tracking= True)
    created_at = fields.Datetime(
        string='Created At', 
        default=lambda self: fields.Datetime.now(),
        readonly=True
    )
    due_date = fields.Date(string='Due Date', tracking= True)
    is_overdue = fields.Boolean(compute='_compute_is_overdue', string='Is Overdue')
    remaining_time = fields.Char(compute="_compute_remaining_time", string="Remaining")

    @api.depends('due_date', 'is_done')
    def _compute_is_overdue(self):
        today = date.today()
        for record in self:
            if record.due_date and record.due_date < today and not record.is_done:
                record.is_overdue = True
            else:
                record.is_overdue = False
                
    @api.depends("due_date", "is_done")
    def _compute_remaining_time(self):
        today = date.today()
        for record in self:
            if record.is_done:
                record.remaining_time = "Completed"
            elif not record.due_date:
                record.remaining_time = "No Deadline"
            else:
                diff = (record.due_date - today).days
                if diff > 0:
                    record.remaining_time = f"{diff} days"
                if diff == 0:
                    record.remaining_time = "Today!"
                else:
                    record.remaining_time = f"Overdue({diff} days)"