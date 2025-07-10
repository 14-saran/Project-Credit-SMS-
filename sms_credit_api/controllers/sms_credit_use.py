from odoo import http, fields
from odoo.http import request
from datetime import datetime

class SmsCreditController(http.Controller):

    @http.route('/api/sms_credit/use',auth='user', methods=['POST'], csrf=False)
    def sms_credit_use(self, **kwargs):
        partner_id = kwargs.get('partner_id')
        use_amount = kwargs.get('use_amount')
        usage_type = kwargs.get('usage_type')

        if not all([partner_id, use_amount, usage_type]):
            return {"status": "error", "message": "Missing required fields"}

        if use_amount <= 0:
            return {"status": "error", "message": "Use amount must be greater than 0"}

        credits = request.env['credit.purchase'].sudo().search([
            ('partner_id', '=', partner_id),
            ('expiry_date', '>=', fields.Date.today()),
            ('used_credit', '<', 'total_credit'),
        ], order='expiry_date asc')

        remaining_to_use = use_amount
        total_used = 0
        usage_matches = []

        for credit in credits:
            available = credit.total_credit - credit.used_credit
            if available <= 0:
                continue

            using = min(remaining_to_use, available)

            credit.sudo().write({
                'used_credit': credit.used_credit + using
            })

            total_used += using
            remaining_to_use -= using

            batch = request.env['sms.inventory.batch'].sudo().search([('name', '=', credit.lot_id.name)], limit=1)

            if batch:
                request.env['sms.usage.match'].sudo().create({
                    'inventory_batch_id': batch.id,
                    'unit_cost': batch.unit_cost,
                    'quantity_used': using,
                })

            usage_matches.append((batch.id if batch else None, using))

            if remaining_to_use <= 0:
                break

        if total_used < use_amount:
            return {
                "status": "error",
                "message": f"Insufficient credit. Requested {use_amount}, available {total_used}"
            }


        usage = request.env['credit.usage'].sudo().create({
            'partner_id': partner_id,
            'usage_datetime': datetime.now(),
            'credit_used': total_used,
            'usage_type': usage_type,
        })

        matches = request.env['sms.usage.match'].sudo().search([
            ('usage_id', '=', False),
            ('inventory_batch_id', 'in', [m[0] for m in usage_matches if m[0]]),
        ])
        matches.write({'usage_id': usage.id})

        return {
            "status": "success",
            "credit_used": total_used,
            "usage_id": usage.id,
        }
