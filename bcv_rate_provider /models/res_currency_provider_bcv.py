# -*- coding: utf-8 -*-
import logging
import requests
from odoo import models, fields, api

_logger = logging.getLogger(__name__)

class ResCurrencyProviderBcv(models.Model):
    _inherit = 'res.currency.provider'

    provider = fields.Selection(
        selection_add=[('bcv', 'Banco Central de Venezuela')],
        ondelete={'bcv': 'set default'}
    )

    def _get_bcv_rates(self, currencies, to_currency, date_start, date_end):
        rates = {}
        # URL de la API intermediaria que usemos para extraer el JSON limpio
        url = "https://api.bcv-venezuela.com/v1/tasa" 
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                today_str = fields.Date.today().strftime('%Y-%m-%d')
                rates[today_str] = {}

                for currency in currencies:
                    if currency in data:
                        tasa_bcv = float(data[currency])
                        if tasa_bcv > 0:
                            # Odoo guarda la tasa inversa si la moneda base es el Bolívar
                            rates[today_str][currency] = 1.0 / tasa_bcv
            else:
                _logger.error("Error de conexión con el BCV. Código: %s", response.status_code)
        except Exception as e:
            _logger.error("Error obteniendo tasas del BCV: %s", str(e))
            
        return rates

    def _fetch_rates(self):
        if self.provider == 'bcv':
            currencies = self.env['res.currency'].search([]).mapped('name')
            to_currency = self.company_id.currency_id.name
            return self._get_bcv_rates(currencies, to_currency, self.last_successful_fetch, fields.Date.today())
        return super(ResCurrencyProviderBcv, self)._fetch_rates()
