# -*- coding: UTF-8 -*-
from budget_app.loaders import PaymentsLoader
from budget_app.models import Budget


payments_mapping = {
    'default': {'fc_code': 1, 'date': 4, 'payee': 5, 'description': 7, 'amount': 8},
    '2016': {'fc_code': 3, 'date': 6, 'payee': 4, 'description': 5, 'amount': 2}
}


class PaymentsCsvMapper:
    def __init__(self, year):
        mapping = payments_mapping.get(str(year))

        if not mapping:
            mapping = payments_mapping.get('default')

        self.fc_code = mapping.get('fc_code')
        self.date = mapping.get('date')
        self.payee = mapping.get('payee')
        self.description = mapping.get('description')
        self.amount = mapping.get('amount')


class ChestePaymentsLoader(PaymentsLoader):
    # Parse an input line into fields
    def parse_item(self, budget, line):
        # Mapper
        mapper = PaymentsCsvMapper(budget.year)

        # First two digits of the programme make the policy id
        policy_id = line[mapper.fc_code].strip()[:2]

        # But what we want as area is the policy description
        policy = Budget.objects.get_all_descriptions(budget.entity)['functional'][policy_id]

        # We got an iso date
        date = line[mapper.date]

        # Payee data
        payee = line[mapper.payee].strip()

        # We got some anonymized entries
        anonymized = False
        anonymized = (True if payee == 'ANONIMIZADO' else anonymized)

        # Description
        description = line[mapper.description].strip()

        # Amount
        amount = line[mapper.amount]
        amount = self._read_english_number(amount)

        return {
            'area': policy,
            'programme': None,
            'ic_code': None,
            'fc_code': None,
            'ec_code': None,
            'date': date,
            'payee': payee,
            'anonymized': anonymized,
            'description': description,
            'amount': amount
        }
