from odoo import models, fields, api
from datetime import date
from odoo.exceptions import ValidationError


class TodoTag(models.Model):
    _name="todo.tag"
    _description = "Todo tag"
    
    name = fields.Char(string='name', required=True)
    color = fields.Integer(string='Color')

class TodoTask(models.Model):
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _name = 'todo.task'
    _description = 'Todo Task'
    
    tag_ids = fields.Many2many(
        'todo.tag',
        strings="Tags",
        help="Classify your tasks using tags."
    )
    
    user_id = fields.Many2one(
        'res.users',
        string='Assignee',
        default=lambda self: self.env.user, # default is who create
        tracking=True
    )
    
    name = fields.Char(string='Task Name', required=True, tracking=True)
    description = fields.Html(string='Description')
    # is_done = fields.Boolean(string='Is Done', default=False, group_expand='_read_group_is_done', tracking= True)
    created_at = fields.Datetime(
        string='Created At', 
        default=lambda self: fields.Datetime.now(),
        readonly=True
    )
    due_date = fields.Datetime(string='Due Date', tracking=True)
    # due_date = fields.Date(string='Due Date', tracking=True)
    is_overdue = fields.Boolean(compute='_compute_is_overdue', string='Is Overdue', store=True)
    remaining_time = fields.Char(compute="_compute_remaining_time", string="Remaining")
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Medium'),
        ('2', 'High'),
        ('3', 'Very High'),
    ], string='Priority', default='0', tracking=True)
    
    state = fields.Selection([
        ('todo', 'To Do'),
        ('doing', 'In Progress'),
        ('done', "Completed")
    ], string="Status", default='todo', required=True, tracking=True, group_expand='_read_group_states')
    
    parent_id = fields.Many2one(
        'todo.task',
        string='Parent task',
        index=True,
        onedelete='cascade'
    )
    
    child_ids = fields.One2many(
        'todo.task',
        'parent_id',
        string='Sub task'
    )
    
    subtask_count = fields.Integer(
        compute='_compute_subtask_count',
        string='Sub-task Count',
        store=True
    )
    
    @api.depends('child_ids')
    def _compute_subtask_count(self):
        for record in self:
            record.subtask_count = len(record.child_ids)
    
    @api.model
    def _read_group_states(self, stages, domain):
        return ['todo', 'doing', 'done']

    @api.depends('due_date', 'state')
    def _compute_is_overdue(self):
        now = fields.Datetime.now()
        # today = date.today()
        for record in self:
            if record.state != 'done' and record.due_date and record.due_date < now:
                record.is_overdue = True
            else:
                record.is_overdue = False
                
    @api.depends("due_date", "state")
    def _compute_remaining_time(self):
        now = fields.Datetime.now()
        for record in self:
            if record.state == 'done':
                record.remaining_time = "Completed"
            elif not record.due_date:
                record.remaining_time = "No Deadline"
            else:
                # Tính toán khoảng cách thời gian
                diff = record.due_date - now
                days = diff.days
                seconds = diff.seconds
                minutes = seconds // 60
                hours = seconds // 3600

                if diff.total_seconds() > 0:
                    if days > 0:
                        record.remaining_time = f"{days}d {hours}h left"
                    else:
                        record.remaining_time = f"{hours}h:{minutes}m:{seconds % 60}s"
                else:
                    record.remaining_time = "Overdue!"
                    
    @api.constrains('parent_id', 'child_ids')
    def _check_subtask_level(self):
        for record in self:
            # 1. Chặn không cho Sub-task đi nhận thêm Sub-task (Chặn cấp 3 từ dưới lên)
            if record.parent_id and record.parent_id.parent_id:
                raise ValidationError("Odoo Todo App only supports 2 levels of tasks!")
            
            # 2. Chặn không cho một thằng đang là Cha đi làm con thằng khác (Chặn cấp 3 từ trên xuống)
            if record.parent_id and record.child_ids:
                raise ValidationError("This task already has sub-tasks. It cannot be assigned to a parent!")