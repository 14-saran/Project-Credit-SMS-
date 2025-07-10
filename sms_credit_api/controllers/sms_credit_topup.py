# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import json

class SmsCreditController(http.Controller):

    @http.route('/api/sms_credit/topup', type='json', auth='user', methods=['POST'], csrf=False)
    def sms_credit_topup(self, **kwargs):
        partner_id = kwargs.get('partner_id')
        total_credit = kwargs.get('total_credit')
        expiry_date = kwargs.get('expiry_date')
        price = kwargs.get('price')
        lot_name = kwargs.get('lot_name')

        if not all([partner_id, total_credit, expiry_date, price]):
            return {"status": "error", "message": "Missing required fields"}

        try:
            unit_cost = float(price) / float(total_credit)
        except ZeroDivisionError:
            return {"status": "error", "message": "Total credit must be > 0"}

        product = request.env.ref('your_module.product_sms_credit')  # ← ชื่อโมดูลของคุณ
        lot = request.env['stock.production.lot'].sudo().create({
            'name': lot_name or f'SMS-{date.today().isoformat()}',
            'product_id': product.id,
        })

        batch = request.env['sms.inventory.batch'].sudo().create({
            'name': lot.name,
            'quantity': total_credit,
            'unit_cost': unit_cost,
            'expiry_date': expiry_date,
        })

        credit = request.env['credit.purchase'].sudo().create({
            'partner_id': partner_id,
            'lot_id': lot.id,
            'total_credit': total_credit,
            'used_credit': 0.0,
            'expiry_date': expiry_date,
            'price': price,
        })

        return {
            "status": "success",
            "credit_purchase_id": credit.id,
            "batch_id": batch.id,
            "lot_id": lot.id,
        }

