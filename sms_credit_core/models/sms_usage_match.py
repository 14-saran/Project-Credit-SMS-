from odoo import models, fields, api

class SmsUsageMatch(models.Model):
    _name = 'sms.usage.match'
    _description = 'Match credit usage with cost batch'

    usage_id = fields.Many2one('credit.usage')
    inventory_batch_id = fields.Many2one('sms.inventory.batch')
    unit_cost = fields.Float()
    quantity_used = fields.Integer()

