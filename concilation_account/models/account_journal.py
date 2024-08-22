import datetime
from odoo import api, fields, models, Command
from odoo.exceptions import ValidationError
import requests
import json

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    def get_status_account_tt(self):
        token_url = "https://sso-sso-project.apps.desplakur3.desintra.banesco.com/auth/realms/realm-api-qa/protocol/openid-connect/token"

        # Credenciales proporcionadas por Banesco
        client_id = "1be28428"  # Reemplaza con tu Client ID
        client_secret = "209d0798893f3d98c2f1e1a34a55b73b"  # Reemplaza con tu Client Secret
        token_data = {
            "grant_type": "password",
            "client_id": client_id,
            "client_secret": client_secret,
            "username": client_id,
            "password": client_secret,
            "Client Authentication": "Send client credentials in body",
        }
        token_headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        response = requests.post(token_url, data=token_data)
        if response.status_code == 200:
            # Extrae el token de acceso del cuerpo de la respuesta
            token = response.json().get('access_token')
            print("Token de acceso obtenido:", token)

            # URL de la API de Banesco
            api_url = "https://sid-validador-consulta-de-transacciones-api-qa-production.apps.desplakur3.desintra.banesco.com/transactions/financial-account/transactions"

            # Datos para la solicitud a la API
            payload = {
                "dataRequest": {
                    "device": {
                        "type": "Notebook",
                        "description": "LENOVO",
                        "ipAddress": "181.225.47.130"
                    },
                    "securityAuth": {
                        "sessionId": ""
                    },
                    "transaction": {
                        "referenceNumber": "",
                        "amount": 0.00,
                        "accountId": "01340214132141039511",
                        "startDt": "2023-07-01",
                        "endDt": "2023-07-31",
                        "phoneNum": "",
                        "bankId": ""
                    }
                }
            }

            # Encabezados de la solicitud a la API
            api_headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }

            # Solicitud POST a la API
            api_response = requests.post(api_url, headers=api_headers, data=json.dumps(payload))

            if api_response.status_code == 200:
                response_json = api_response.json()
                transactions = response_json.get('dataResponse', {}).get('transactionDetail', [])
                saldo = 0
                for transaction in transactions:

                    if transaction['trnType'] in ['ID','DB']:
                        amount = transaction['amount'] * -1
                    else:
                        amount = transaction['amount']
                    saldo += amount
                    print(transaction['trnType'])
                    print(transaction['amount'])
                print(f'SALDO FINAL: {saldo}')

    def get_status_account(self):
        journal_ids = self.env['account.journal'].search([('type', '=', 'bank')])
        print(f"Journal IDs encontrados: {journal_ids}")
        token = ''
        response  = ''
        for journal in journal_ids:

            bank_account = journal.bank_account_id
            print(f"Bank Account ID: {bank_account}")

            if bank_account:
                bank = bank_account.bank_id
                print(f"Bank ID: {bank}")

                client_id = bank.client_id
                client_secret = bank.client_secret
                print(f"client_id: {client_id}")
                print(f"client_secret: {client_secret}")
                token_url = "https://sso-sso-project.apps.desplakur3.desintra.banesco.com/auth/realms/realm-api-qa/protocol/openid-connect/token"
                token_data = {
                    "grant_type": "password",
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "username": client_id,
                    "password": client_secret,
                    "Client Authentication": "Send client credentials in body",
                }
                token_headers = {
                    "Content-Type": "application/x-www-form-urlencoded"
                }
                if bank and token == '':
                    response = requests.post(token_url, data=token_data)
                    print(f"Respuesta del token: {response.status_code} - {response.text}")

                if response.status_code == 200:
                    token = response.json().get('access_token')
                    print(f"Token de acceso obtenido: {token}")

                    api_url = "https://sid-validador-consulta-de-transacciones-api-qa-production.apps.desplakur3.desintra.banesco.com/transactions/financial-account/transactions"

                    payload = {
                        "dataRequest": {
                            "device": {
                                "type": "Notebook",
                                "description": "LENOVO",
                                "ipAddress": "181.225.47.130"
                            },
                            "securityAuth": {
                                "sessionId": ""
                            },
                            "transaction": {
                                "referenceNumber": "",
                                "amount": 0.00,
                                "accountId": "01340214132141039511",
                                "startDt": "2023-07-01",
                                "endDt": "2023-07-31",
                                "phoneNum": "",
                                "bankId": ""
                            }
                        }
                    }

                    api_headers = {
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json"
                    }

                    api_response = requests.post(api_url, headers=api_headers, data=json.dumps(payload))
                    print(f"Respuesta de la API: {api_response.status_code} - {api_response.text}")

                    if api_response.status_code == 200:
                        response_json = api_response.json()
                        transactions = response_json.get('dataResponse', {}).get('transactionDetail', [])
                        print(f"Transacciones encontradas: {transactions}")

                        previous_statements = self.env['account.bank.statement'].search([
                            ('journal_id', '=', journal.id)
                        ], order='date DESC', limit=1)

                        balance_start = previous_statements.balance_end_real if previous_statements else 0.0
                        balance_end_real = balance_start

                        count_balances = 0

                        for transaction in transactions:
                            if transaction['trnType'] in ['ID', 'DB']:
                                amount = transaction['amount'] * -1
                            else:
                                amount = transaction['amount']

                            reference_number = transaction.get('referenceNumber')
                            trnDate = transaction.get('trnDate')

                            if count_balances == 0:
                                balance_end_real += amount
                                self.sudo().env['account.bank.statement'].create({
                                    'name': f'{journal.name} - 20-08-2024/01',
                                    'balance_end_real': balance_end_real,
                                    'balance_start': balance_start,
                                    'line_ids': [
                                        Command.create({
                                            'journal_id': journal.id,
                                            'payment_ref': f'{reference_number}',
                                            'amount': amount,
                                            'date': f'{trnDate}',
                                            'partner_id': 2,
                                        }),
                                    ]
                                })
                                count_balances += 1
                                print(f"Extracto bancario creado para {reference_number}")
                                self.env.cr.commit()

                            if count_balances > 0:
                                balance_start = balance_end_real
                                balance_end_real += amount
                                self.sudo().env['account.bank.statement'].create({
                                    'name': f'{journal.name} - 20-08-2024/01',
                                    'balance_end_real': balance_end_real,
                                    'balance_start': balance_start,
                                    'line_ids': [
                                        Command.create({
                                            'journal_id': journal.id,
                                            'payment_ref': f'{reference_number}',
                                            'amount': amount,
                                            'date': f'{trnDate}',
                                            'partner_id': 2,
                                        }),
                                    ]
                                })
                                count_balances += 1
                                print(f"Extracto bancario actualizado para {reference_number}")
                                self.env.cr.commit()
                    else:
                        print("Error en la solicitud a la API:", api_response.status_code, api_response.text)