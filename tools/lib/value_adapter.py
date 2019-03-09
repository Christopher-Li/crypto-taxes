import coinbase_api

class ValueAdapter:
    def __init__(self):
        self.currency_values_cache = dict()

    @staticmethod
    def get_currency_values_hash(transaction):
        return transaction.get_coinbase_date(), transaction.currency

    def set_transaction_value(self, transaction):
        if not transaction.value:
            if self.get_currency_values_hash(transaction) not in self.currency_values_cache:
                if coinbase_api.is_coinbase_price_available(transaction.currency):
                    self.currency_values_cache[self.get_currency_values_hash(transaction)] = \
                        float(coinbase_api.get_historic_price(transaction.currency, transaction.get_coinbase_date()))
                else: # cannot find price of currency
                    self.currency_values_cache[self.get_currency_values_hash(transaction)] = ''
            transaction.value = self.currency_values_cache[self.get_currency_values_hash(transaction)]
