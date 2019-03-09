from abc import ABCMeta, abstractmethod
from transaction import Transaction
from datetime import datetime
from utils import find

import re


class ExchangeConverter:
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_standard_transactions(self):
        pass


class GdaxExchangeConverter(ExchangeConverter):
    TYPE_TO_TRANSACTION_TYPE_DICT = {
        'deposit': 'transfer',
        'withdrawal': 'transfer',
        'match': 'trade',
        'fee': 'fee'
    }

    def __init__(self, csv_reader_data):
        self.csv_reader_data = csv_reader_data

        # remove first line
        self.csv_reader_data.next()

    # Format:
    # type, time, amount, balance, currency, transfer id, trace id, order id
    def get_standard_transactions(self):
        transactions = []
        for row in self.csv_reader_data:
            t = Transaction(self.get_date(row),
                            self.get_transaction_type(row),
                            self.get_currency(row),
                            self.get_amount(row))
            transactions.append(t)
        return transactions

    @staticmethod
    def get_date(row):
        try:
            return datetime.strptime(row[1][:-5], "%Y-%m-%dT%H:%M:%S")
        except ValueError:
            return None

    @staticmethod
    def get_currency(row):
        return row[4]

    @staticmethod
    def get_transaction_type(row):
        return GdaxExchangeConverter.TYPE_TO_TRANSACTION_TYPE_DICT[row[0]]

    @staticmethod
    def get_amount(row):
        return row[2]


class GeminiExchangeConverter(ExchangeConverter):
    TYPE_TO_TRANSACTION_TYPE_DICT = {
        'Credit': 'transfer',
        'Debit': 'transfer',
        'Buy': 'trade',
        'Sell': 'trade'
    }
# Format: # date, time, type, symbol, specification, liquidity, trading fee, usd amount, trading fee(usd), usd balance,
    # btc amount, trading fee(btc), btc balance, eth amount, eth balance, trade id, order id, order date, order time,
    # client order id, api session, tx hash, deposit tx output, withdrawal destination, withdrawal tx output
    def __init__(self, csv_reader_data):
        self.csv_reader_data = csv_reader_data

        headers = self.csv_reader_data.next()
        self.date_index = 0
        self.time_index = find(headers, "Time (UTC)")
        self.type_index = find(headers, "Type")
        self.symbol_index = find(headers, "Symbol")
        self.btc_amount_index = find(headers, "BTC Amount")
        self.btc_fee_index = find(headers, "Trading Fee (BTC)")
        self.eth_amount_index = find(headers, "ETH Amount")
        self.usd_amount_index = find(headers, "USD Amount")
        self.usd_fee_index = find(headers, "Trading Fee (USD)")

        self.transactions = list()

    def get_standard_transactions(self):
        for row in self.csv_reader_data:
            if self.get_date(row):
                self.maybe_create_btc_transaction(row)
                self.maybe_create_btc_fee(row)
                self.maybe_create_eth_transaction(row)
                self.maybe_create_usd_fee(row)
        return self.transactions

    def maybe_create_btc_transaction(self, row):
        t = self.maybe_create_generic_transaction(row, self.btc_amount_index, "btc")
        if t:
            self.transactions.append(t)

    def maybe_create_eth_transaction(self, row):
        t = self.maybe_create_generic_transaction(row, self.eth_amount_index, "eth")
        if t:
            self.transactions.append(t)

    def maybe_create_btc_fee(self, row):
        t = self.maybe_create_generic_fee(row, self.btc_fee_index, "btc")
        if t:
            self.transactions.append(t)

    def maybe_create_usd_fee(self, row):
        t = self.maybe_create_generic_fee(row, self.usd_fee_index, "usd")
        if t:
            self.transactions.append(t)

    def maybe_create_generic_transaction(self, row, amount_index, currency):
        if row[amount_index]:
            amount = self.get_amount(row[amount_index])
            value = self.get_value(row, amount)
            return Transaction(self.get_date(row),
                               self.get_transaction_type(row),
                               currency,
                               amount,
                               value)

    def maybe_create_generic_fee(self, row, amount_index, currency):
        if row[amount_index]:
            return Transaction(self.get_date(row),
                               "fee",
                               currency,
                               self.get_amount(row[amount_index]))

    # example: "10/15/2017  12:00:18 AM"
    def get_date(self, row):
        try:
            return datetime.strptime(row[self.date_index] + " " + row[self.time_index][:-4], "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return None

    def get_transaction_type(self, row):
        return GeminiExchangeConverter.TYPE_TO_TRANSACTION_TYPE_DICT[row[self.type_index]]

    @staticmethod
    def get_amount(cell_value):
        val = cell_value.replace(",","")
        amount = float(re.search("\d+\.\d+", val).group(0))
        if "(" in cell_value:
            amount = -amount
        return amount

    def get_value(self, row, amount):
        if row[self.usd_amount_index]:
            return abs(float(self.get_amount(row[self.usd_amount_index]))/float(amount))


class CoinbaseExchangeConverter(ExchangeConverter):
    DATETIME_FORMATS = ["%Y-%m-%d %H:%M:%S", "%m/%d/%y %H:%M"]

    # format:
    # timestamp, balance, amount, currency, to, notes, instantly exchanged, transfer total, transfer total currency,
    # transfer fee, transfer fee currency
    def __init__(self, csv_reader_data):
        self.csv_reader_data = csv_reader_data

        # drop 4 transactions
        for i in xrange(4):
            self.csv_reader_data.next()
        headers = self.csv_reader_data.next()
        self.timestamp_index = 0
        self.amount_index = find(headers, "Amount")
        self.currency_index = find(headers, "Currency")
        self.transfer_total_index = find(headers, "Transfer Total")
        self.transfer_total_currency_index = find(headers, "Transfer Total Currency")
        self.transfer_fee_index = find(headers, "Transfer Fee")
        self.transfer_fee_currency_index = find(headers, "Transfer Fee Currency")

        self.transactions = list()

    def get_standard_transactions(self):
        for row in self.csv_reader_data:
            # coinbase doesn't distinguish between transfers and trades, so I just set everything to trade
            self.transactions.append(Transaction(
                self.get_date(row),
                "trade",
                self.get_currency(row),
                self.get_amount(row),
                self.get_value(row)))
            if self.get_transfer_fee(row) and self.get_transfer_fee_currency(row):
                self.transactions.append(Transaction(
                    self.get_date(row),
                    "fee",
                    self.get_transfer_fee_currency(row),
                    self.get_transfer_fee(row)))
        return self.transactions

    # example: "2017-08-02 10:13:36"
    def get_date(self, row):
        if len(row[self.timestamp_index].split()) != 2:
            timestamp_str = " ".join(row[self.timestamp_index].split()[:2])
        else:
            timestamp_str = row[self.timestamp_index]

        for format in self.DATETIME_FORMATS:
            try:
                return datetime.strptime(timestamp_str, format)
            except ValueError:
                pass

    def get_amount(self, row):
        return row[self.amount_index]

    def get_currency(self, row):
        return row[self.currency_index]

    def get_transfer_total(self, row):
        return row[self.transfer_total_index]

    def get_transfer_total_currency(self, row):
        return row[self.transfer_total_currency_index]

    def get_transfer_fee(self, row):
        return row[self.transfer_fee_index]

    def get_transfer_fee_currency(self, row):
        return row[self.transfer_fee_currency_index]

    def get_value(self, row):
        if self.get_transfer_total(row) and self.get_transfer_total_currency(row) == "USD":
            return float(self.get_transfer_total(row))/float(self.get_amount(row))


class BinanceExchangeConverter(ExchangeConverter):
    CURRENCY_EXCHANGES = ["BTC", "ETH", "BNB", "USDT"]

    # format:
    # date, market, type, price, amount, total, fee, fee coin
    def __init__(self, csv_reader_data):
        self.csv_reader_data = csv_reader_data

        headers = self.csv_reader_data.next()
        self.date_index = 0
        self.market_index = find(headers, "Market")
        self.coin_index = find(headers, "Coin")
        self.type_index = find(headers, "Type")
        self.price_index = find(headers, "Price")
        self.amount_index = find(headers, "Amount")
        self.fee_index = find(headers, "Fee")
        self.fee_currency_index = find(headers, "Fee Coin")

        self.transactions = list()

    def get_standard_transactions(self):
        if self.coin_index: # if coin column is present then it is a csv of transfers and not trades
            self.get_standard_transfer_transactions()
        else:
            self.get_standard_trade_transactions()

        self.transactions.reverse()
        return self.transactions

    def get_standard_transfer_transactions(self):
        for row in self.csv_reader_data:
            self.transactions.append(Transaction(
                self.get_date(row),
                "transfer",
                self.get_coin(row),
                self.get_amount(row)))

    def get_standard_trade_transactions(self):
        for row in self.csv_reader_data:
            first_currency, second_currency = self.get_currency(row)
            # self.transactions.append(Transaction(
            #     self.get_date(row),
            #     "trade",
            #     first_currency,
            #     self.get_amount(row),
            #     self.get_price(row),
            #     second_currency))
            self.transactions.append(Transaction(
                self.get_date(row),
                "fee",
                self.get_fee_currency(row),
                self.get_fee(row)))

            self.transactions.append(Transaction(
                self.get_date(row),
                "trade",
                first_currency,
                self.get_amount(row)
            ))
            self.transactions.append(Transaction(
                self.get_date(row),
                "trade",
                second_currency,
                self.get_amount(row) * -1.0 * self.get_price(row)
            ))

    def get_date(self, row):
        return datetime.strptime(row[self.date_index], "%Y-%m-%d %H:%M:%S")

    def get_currency(self, row):
        for currency in self.CURRENCY_EXCHANGES:
            if row[self.market_index].endswith(currency):
                return row[self.market_index][:-len(currency)], currency

    def get_coin(self, row):
        return row[self.coin_index]

    def get_amount(self, row):
        prefix = "" if self.type_index and row[self.type_index] == "BUY" else "-"
        return float(prefix + row[self.amount_index])

    def get_price(self, row):
        return float(row[self.price_index])

    def get_fee(self, row):
        return row[self.fee_index]

    def get_fee_currency(self, row):
        return row[self.fee_currency_index]
