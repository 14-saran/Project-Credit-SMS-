from odoo import models, fields, api
from datetime import date

from odoo.exceptions import ValidationError


class CreditPurchase(models.Model):
    _name = 'credit.purchase'
    _description = 'Customer Credit Purchase'

    partner_id = fields.Many2one('res.partner', string='Customer', required=True)
    lot_id = fields.Many2one('stock.production.lot', string='Lot', required=True)
    total_credit = fields.Float(string='Total Credit', required=True)
    used_credit = fields.Float(string='Used Credit', default=0.0)
    expiry_date = fields.Date(string='Expiry Date')
    price = fields.Float(string='Total Price')
    revenue_recognized = fields.Float(string='Revenue Recognized', default=0.0)
    journal_entry_id = fields.Many2one('account.move', string='Deferred Revenue Entry')

    @api.model
    def consume_credit(self, customer, amount):
        remaining = amount
        today = fields.Date.today()

        packages = self.search([
            ('partner_id', '=', customer.id),
            ('expiry_date', '>', today),
            ('total_credit', '>', 0),
        ], order='expiry_date asc')

        valid_packages = [p for p in packages if (p.total_credit - p.used_credit) > 0]

        if not valid_packages:
            raise ValidationError("No valid credit packages with available balance.")

        for pack in valid_packages:
            available = pack.total_credit - pack.used_credit

            if available >= remaining:
                pack.used_credit += remaining
                pack.revenue_recognized += pack.price * (remaining / pack.total_credit)
                remaining = 0
                break
            else:
                pack.used_credit += available
                pack.revenue_recognized += pack.price * (available / pack.total_credit)
                remaining -= available

        if remaining > 0:
            raise ValidationError("Not enough credit available for this customer.")
