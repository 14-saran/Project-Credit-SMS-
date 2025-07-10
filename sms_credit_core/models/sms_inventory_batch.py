from odoo import models, fields, api

class SmsInventoryBatch(models.Model):
    _name = 'sms.inventory.batch'
    _description = 'SMS Inventory by Batch'

    name = fields.Char()
    quantity = fields.Integer()
    unit_cost = fields.Float()
    expiry_date = fields.Date()
    used_quantity = fields.Integer(default=0)