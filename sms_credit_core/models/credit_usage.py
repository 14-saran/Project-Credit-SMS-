from odoo import models, fields, api

class CreditUsage(models.Model):
    _name = 'credit.usage'
    _description = 'Credit Usage Log'

    partner_id = fields.Many2one('res.partner')
    usage_datetime = fields.Datetime(default=fields.Datetime.now)
    used_credit = fields.Integer()
    usage_type = fields.Selection([('sms', 'SMS'), ('tracking', 'SMS + Tracking')])
    revenue_recognized = fields.Boolean(default=False)