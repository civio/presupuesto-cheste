# -*- coding: UTF-8 -*-
from budget_app.loaders import SimpleBudgetLoader


expenses_mapping = {
    'default': {'ic_code': None, 'fc_code': 1, 'full_ec_code': 2, 'description': 3, 'forecast_amount': 9, 'actual_amount': 10},
}

income_mapping = {
    'default': {'full_ec_code': 2, 'description': 3, 'forecast_amount': 6, 'actual_amount': 7},
}

programme_mapping = {
    # old programme: new programme
    '1340': '1350',     # Protección Civil
    '1350': '1360',     # Servicio de prevención y extinción de incendios
    '1530': '1520',     # Vivienda
    '1550': '1532',     # Pavimentación de vías públicas
    '1620': '1621',     # Recogida de residuos
    '1790': '1720',     # Protección y mejora del medio ambiente
    '2340': '2310',     # Asistencia social primaria
    '2350': '2310',     # Asistencia social primaria
    '3130': '3110',     # Protección de la salubridad pública
    '3210': '3230',     # Funcionamiento de centros docentes de enseñanza infantil y primaria
    '3220': '3240',     # Funcionamiento de centros docentes de enseñanza secundaria
    '3230': '3260',     # Servicios complementarios de educación
    '3240': '3260',     # Servicios complementarios de educación
    '3350': '3340',     # Promoción cultural
    '3390': '3340',     # Promoción cultural
    '4310': '4312',     # Mercados, abastos y lonjas
    '1690': '9200',     # Administración general (cambia la política, pero es lo que mejor se adapta)
}


class BudgetCsvMapper:
    def __init__(self, year, is_expense):
        column_mapping = income_mapping

        if is_expense:
            column_mapping = expenses_mapping

        mapping = column_mapping.get(str(year))

        if not mapping:
            mapping = column_mapping.get('default')

        self.ic_code = mapping.get('ic_code')
        self.fc_code = mapping.get('fc_code')
        self.full_ec_code = mapping.get('full_ec_code')
        self.description = mapping.get('description')
        self.forecast_amount = mapping.get('forecast_amount')
        self.actual_amount = mapping.get('actual_amount')


class ChesteBudgetLoader(SimpleBudgetLoader):
    # make year data available in the class and call super
    def load(self, entity, year, path, status):
        self.year = year
        SimpleBudgetLoader.load(self, entity, year, path, status)

    # Parse an input line into fields
    def parse_item(self, filename, line):
        # Type of data
        is_expense = (filename.find('gastos.csv') != -1)
        is_actual = (filename.find('/ejecucion_') != -1)

        # Mapper
        mapper = BudgetCsvMapper(self.year, is_expense)

        # Institutional code
        # All expenses go to the root node
        ic_code = '000'

        # Economic code
        full_ec_code = line[mapper.full_ec_code].strip()

        # Concepts are the firts three digits from the economic codes
        ec_code = full_ec_code[:3]

        # Item numbers are the last two digits from the economic codes (fourth and fifth digits)
        item_number = full_ec_code[-2:]

        # Description
        description = line[mapper.description].strip()

        # Parse amount
        amount = line[mapper.actual_amount if is_actual else mapper.forecast_amount]
        amount = self._parse_amount(amount)

        # Expenses
        if is_expense:
            # Functional code
            # We got 3- or 4- digit functional codes as input, so add a trailing zero
            fc_code = line[mapper.fc_code].strip()
            fc_code = fc_code.ljust(4, '0')

            # Programme codes have changed in 2015, due to new laws. Since the application expects a code-programme
            # mapping to be constant over time, we are forced to amend budget data prior to 2015.
            # See https://github.com/dcabo/presupuestos-aragon/wiki/La-clasificaci%C3%B3n-funcional-en-las-Entidades-Locales
            # For years before 2015 we check whether we need to amend the programme code
            if int(self.year) < 2015:
                fc_code = programme_mapping.get(fc_code, fc_code)

        # Income
        else:
            # Functional code
            # We don't have a functional code in income
            fc_code = None

        return {
            'is_expense': is_expense,
            'is_actual': is_actual,
            'fc_code': fc_code,
            'ec_code': ec_code,
            'ic_code': ic_code,
            'item_number': item_number,
            'description': description,
            'amount': amount
        }
